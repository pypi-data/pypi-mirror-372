"""
Unified merge module for the Study class.
Supports multiple merge methods: 'kd', 'qt', 'kd-nowarp', 'chunked'
"""

import time
import numpy as np
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm
import pyopenms as oms
import polars as pl
from masster.study.defaults import merge_defaults


def merge(self, **kwargs) -> None:
    """
    Group features across samples into consensus features using various algorithms.

    This function provides a unified interface to multiple feature grouping algorithms,
    each optimized for different dataset sizes and analysis requirements.

    Parameters
    ----------
    **kwargs : dict
        Parameters from merge_defaults class:
        - method : str, default 'kd'
          Merge algorithm: 'kd', 'qt', 'kd-nowarp', 'chunked'
        - min_samples : int, default 10  
          Minimum number of samples for consensus feature
        - rt_tol : float, default 2.0
          RT tolerance in seconds
        - mz_tol : float, default 0.01
          m/z tolerance in Da (Daltons) for all methods
        - chunk_size : int, default 500
          Chunk size for 'chunked' method
        - nr_partitions : int, default 500
          Number of partitions in m/z dimension for KD algorithms
        - min_rel_cc_size : float, default 0.3
          Minimum relative connected component size for conflict resolution
        - max_pairwise_log_fc : float, default 0.5
          Maximum pairwise log fold change for conflict resolution
        - max_nr_conflicts : int, default 0
          Maximum number of conflicts allowed in consensus feature
        - link_ms2 : bool, default True
          Whether to link MS2 spectra to consensus features

    Algorithm Guidelines
    -------------------
    - KD: Best general purpose, O(n log n), recommended default
    - QT: Thorough but slow O(n²), good for <1000 samples  
    - KD-NoWarp: Memory efficient KD without RT warping for large datasets
    - Chunked: Memory-optimized KD algorithm for very large datasets (>5000 samples)
      Uses optimized partitioning for better memory management while maintaining
      full cross-sample consensus feature detection.
    """
    start_time = time.time()
    
    # Initialize with defaults and override with kwargs
    params = merge_defaults()
    
    # Filter and apply only valid parameters
    valid_params = set(params.list_parameters())
    for key, value in kwargs.items():
        if key in valid_params:
            setattr(params, key, value)
        else:
            self.logger.warning(f"Unknown parameter '{key}' ignored")
    
    # Validate method
    if params.method not in ['kd', 'qt', 'kd-nowarp', 'chunked']:
        raise ValueError(f"Invalid method '{params.method}'. Must be one of: ['kd', 'qt', 'kd-nowarp', 'chunked']")
    
    # Persist last used params for diagnostics
    try:
        self._merge_params_last = params.to_dict()
    except Exception:
        self._merge_params_last = {}
    
    # Ensure feature maps are available for merging (regenerate if needed)
    if len(self.features_maps) < len(self.samples_df):
        self.features_maps = []
        self.load_features()
    
    self.logger.info(
        f"Merge: {params.method}, samples={params.min_samples}, rt_tol={params.rt_tol}s, mz_tol={params.mz_tol}Da, min_rel_cc_size={params.min_rel_cc_size}, max_pairwise_log_fc={params.max_pairwise_log_fc}, max_nr_conflicts={params.max_nr_conflicts}"
    )
    
    # Initialize
    self._reset_consensus_data()

    # Cache adducts for performance (avoid repeated _get_adducts() calls)
    cached_adducts_df = None
    cached_valid_adducts = None
    try:
        cached_adducts_df = self._get_adducts()
        if not cached_adducts_df.is_empty():
            cached_valid_adducts = set(cached_adducts_df["name"].to_list())
        else:
            cached_valid_adducts = set()
    except Exception as e:
        self.logger.warning(f"Could not retrieve study adducts: {e}")
        cached_valid_adducts = set()
    
    # Always allow '?' adducts
    cached_valid_adducts.add("?")
    
    # Route to algorithm implementation  
    if params.method == 'kd':
        consensus_map = _merge_kd(self, params)
        # Extract consensus features
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
    elif params.method == 'qt':
        consensus_map = _merge_qt(self, params)
        # Extract consensus features
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
    elif params.method == 'kd-nowarp':
        consensus_map = _merge_kd_nowarp(self, params)
        # Extract consensus features
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
    elif params.method == 'chunked':
        consensus_map = _merge_chunked(self, params, cached_adducts_df, cached_valid_adducts)
        # Note: _merge_chunked populates consensus_df directly, no need to extract
    
    # Perform adduct grouping
    self._perform_adduct_grouping(params.rt_tol, params.mz_tol)
    
    # Link MS2 if requested
    if params.link_ms2:
        self._finalize_merge(params.link_ms2, params.min_samples)
    
    # Log completion without the misleading feature count
    elapsed = time.time() - start_time
    self.logger.debug(f"Merge process completed in {elapsed:.1f}s")


def _merge_kd(self, params: merge_defaults) -> oms.ConsensusMap:
    """KD-tree based merge (fast, recommended)"""
    
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()
    
    for i, feature_map in enumerate(self.features_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description
    
    consensus_map.setColumnHeaders(file_descriptions)
    
    # Configure KD algorithm
    grouper = oms.FeatureGroupingAlgorithmKD()
    params_oms = grouper.getParameters()
    
    params_oms.setValue("mz_unit", "Da")
    params_oms.setValue("nr_partitions", params.nr_partitions)
    params_oms.setValue("warp:enabled", "true")
    params_oms.setValue("warp:rt_tol", params.rt_tol)
    params_oms.setValue("warp:mz_tol", params.mz_tol)
    params_oms.setValue("link:rt_tol", params.rt_tol)
    params_oms.setValue("link:mz_tol", params.mz_tol)
    params_oms.setValue("link:min_rel_cc_size", params.min_rel_cc_size)
    params_oms.setValue("link:max_pairwise_log_fc", params.max_pairwise_log_fc)
    params_oms.setValue("link:max_nr_conflicts", params.max_nr_conflicts)
    #params_oms.setValue("link:charge_merging", "With_charge_zero") THIS LEADS TO A CRASH
    
    grouper.setParameters(params_oms)
    grouper.group(self.features_maps, consensus_map)
    
    return consensus_map


def _merge_qt(self, params: merge_defaults) -> oms.ConsensusMap:
    """QT (Quality Threshold) based merge"""
    
    n_samples = len(self.features_maps)
    if n_samples > 1000:
        self.logger.warning(f"QT with {n_samples} samples may be slow [O(n²)]. Consider KD [O(n log n)]")
    
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()
    
    for i, feature_map in enumerate(self.features_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description
    
    consensus_map.setColumnHeaders(file_descriptions)
    
    # Configure QT algorithm
    grouper = oms.FeatureGroupingAlgorithmQT()
    params_oms = grouper.getParameters()
    
    params_oms.setValue("distance_RT:max_difference", params.rt_tol)
    params_oms.setValue("distance_MZ:max_difference", params.mz_tol)
    params_oms.setValue("distance_MZ:unit", "Da")  # QT now uses Da like all other methods
    params_oms.setValue("ignore_charge", "true")
    params_oms.setValue("min_rel_cc_size", params.min_rel_cc_size)
    params_oms.setValue("max_pairwise_log_fc", params.max_pairwise_log_fc)
    params_oms.setValue("max_nr_conflicts", params.max_nr_conflicts)
    params_oms.setValue("nr_partitions", params.nr_partitions)

    grouper.setParameters(params_oms)
    grouper.group(self.features_maps, consensus_map)
    
    return consensus_map


def _merge_kd_nowarp(self, params: merge_defaults) -> oms.ConsensusMap:
    """KD-tree based merge without RT warping"""
    
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()
    
    for i, feature_map in enumerate(self.features_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description
    
    consensus_map.setColumnHeaders(file_descriptions)
    
    # Configure KD algorithm with warping disabled for memory efficiency
    grouper = oms.FeatureGroupingAlgorithmKD()
    params_oms = grouper.getParameters()
    
    params_oms.setValue("mz_unit", "Da")
    params_oms.setValue("nr_partitions", params.nr_partitions)
    params_oms.setValue("warp:enabled", "false")  # Disabled for memory efficiency
    params_oms.setValue("link:rt_tol", params.rt_tol)
    params_oms.setValue("link:mz_tol", params.mz_tol)
    params_oms.setValue("link:min_rel_cc_size", params.min_rel_cc_size)
    params_oms.setValue("link:max_pairwise_log_fc", params.max_pairwise_log_fc)
    params_oms.setValue("link:max_nr_conflicts", params.max_nr_conflicts)
    #params_oms.setValue("link:charge_merging", "Any")
    
    grouper.setParameters(params_oms)
    grouper.group(self.features_maps, consensus_map)
    
    return consensus_map


def _merge_chunked(self, params: merge_defaults, cached_adducts_df=None, cached_valid_adducts=None) -> oms.ConsensusMap:
    """Chunked merge with proper cross-chunk consensus building"""
    
    n_samples = len(self.features_maps)
    if n_samples <= params.chunk_size:
        self.logger.info(f"Dataset size ({n_samples}) ≤ chunk_size, using KD merge")
        consensus_map = _merge_kd(self, params)
        # Extract consensus features to populate consensus_df for chunked method consistency
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
        return consensus_map
    
    # Process in chunks
    chunks = []
    for i in range(0, n_samples, params.chunk_size):
        chunk_end = min(i + params.chunk_size, n_samples)
        chunks.append((i, self.features_maps[i:chunk_end]))
    
    self.logger.debug(f"Processing {len(chunks)} chunks of max {params.chunk_size} samples")
    
    # Process each chunk to create chunk consensus maps
    chunk_consensus_maps = []
    
    for chunk_idx, (chunk_start_idx, chunk_maps) in enumerate(tqdm(chunks, desc="Chunk", disable=self.log_level not in ["TRACE", "DEBUG", "INFO"])):
        chunk_consensus_map = oms.ConsensusMap()
        
        # Set up file descriptions for chunk
        file_descriptions = chunk_consensus_map.getColumnHeaders()
        for j, feature_map in enumerate(chunk_maps):
            file_description = file_descriptions.get(j, oms.ColumnHeader())
            file_description.filename = self.samples_df.row(chunk_start_idx + j, named=True)["sample_name"]
            file_description.size = feature_map.size()
            file_description.unique_id = feature_map.getUniqueId()
            file_descriptions[j] = file_description
        
        chunk_consensus_map.setColumnHeaders(file_descriptions)
        
        # Use KD algorithm for chunk
        grouper = oms.FeatureGroupingAlgorithmKD()
        chunk_params = grouper.getParameters()
        chunk_params.setValue("mz_unit", "Da")
        chunk_params.setValue("nr_partitions", params.nr_partitions)
        chunk_params.setValue("warp:enabled", "true")
        chunk_params.setValue("warp:rt_tol", params.rt_tol)
        chunk_params.setValue("warp:mz_tol", params.mz_tol)
        chunk_params.setValue("link:rt_tol", params.rt_tol)
        chunk_params.setValue("link:mz_tol", params.mz_tol)
        chunk_params.setValue("link:min_rel_cc_size", params.min_rel_cc_size)
        chunk_params.setValue("link:max_pairwise_log_fc", params.max_pairwise_log_fc)
        chunk_params.setValue("link:max_nr_conflicts", params.max_nr_conflicts)
        
        grouper.setParameters(chunk_params)
        grouper.group(chunk_maps, chunk_consensus_map)
        
        chunk_consensus_maps.append((chunk_start_idx, chunk_consensus_map))
    
    # Merge chunk results with proper cross-chunk consensus building
    _merge_chunk_results(self, chunk_consensus_maps, params, cached_adducts_df, cached_valid_adducts)
    
    # Create a dummy consensus map for compatibility (since other functions expect it)
    consensus_map = oms.ConsensusMap()
    return consensus_map


def _merge_chunk_results(self, chunk_consensus_maps: list, params: merge_defaults, cached_adducts_df=None, cached_valid_adducts=None) -> None:
    """
    Scalable aggregation of chunk consensus maps into final consensus_df.
    
    This function implements cross-chunk consensus building by:
    1. Extracting feature_uids from each chunk consensus map
    2. Aggregating features close in RT/m/z across chunks
    3. Building consensus_df and consensus_mapping_df directly
    """
    
    if len(chunk_consensus_maps) == 1:
        # Single chunk case - just extract using the true global min_samples.
        # No need for permissive threshold because we are not discarding singletons pre-aggregation.
        self._extract_consensus_features(
            chunk_consensus_maps[0][1],
            params.min_samples,
            cached_adducts_df,
            cached_valid_adducts,
        )
        return
    
    # Build feature_uid to feature_data lookup for fast access
    feature_uid_map = {
        row["feature_id"]: row["feature_uid"]
        for row in self.features_df.iter_rows(named=True)
    }
    
    features_lookup = _optimized_feature_lookup(self, self.features_df)
    
    # Extract all consensus features from chunks with their feature_uids
    all_chunk_consensus = []
    consensus_id_counter = 0
    
    for chunk_idx, (chunk_start_idx, chunk_consensus_map) in enumerate(chunk_consensus_maps):
        for consensus_feature in chunk_consensus_map:
            # ACCEPT ALL consensus features (size >=1) here.
            # Reason: A feature that is globally present in many samples can still
            # appear only once inside a given sample chunk. Early filtering at
            # size>=2 causes irreversible loss and underestimates the final
            # consensus count (observed ~296 vs 950 for KD). We defer filtering
            # strictly to the final global min_samples.
                
            # Extract feature_uids from this consensus feature
            feature_uids = []
            feature_data_list = []
            sample_uids = []
            
            for feature_handle in consensus_feature.getFeatureList():
                fuid = str(feature_handle.getUniqueId())
                if fuid not in feature_uid_map:
                    continue
                    
                feature_uid = feature_uid_map[fuid]
                feature_data = features_lookup.get(feature_uid)
                if feature_data:
                    feature_uids.append(feature_uid)
                    feature_data_list.append(feature_data)
                    sample_uids.append(chunk_start_idx + feature_handle.getMapIndex() + 1)

            if not feature_data_list:
                # No retrievable feature metadata (possible stale map reference) -> skip
                continue            # Derive RT / m/z ranges from underlying features (used for robust cross-chunk stitching)
            rt_vals_local = [fd.get("rt") for fd in feature_data_list if fd.get("rt") is not None]
            mz_vals_local = [fd.get("mz") for fd in feature_data_list if fd.get("mz") is not None]
            if rt_vals_local:
                rt_min_local = min(rt_vals_local)
                rt_max_local = max(rt_vals_local)
            else:
                rt_min_local = rt_max_local = consensus_feature.getRT()
            if mz_vals_local:
                mz_min_local = min(mz_vals_local)
                mz_max_local = max(mz_vals_local)
            else:
                mz_min_local = mz_max_local = consensus_feature.getMZ()
                
            # Store chunk consensus with feature tracking
            chunk_consensus_data = {
                'consensus_id': consensus_id_counter,
                'chunk_idx': chunk_idx,
                'chunk_start_idx': chunk_start_idx,
                'mz': consensus_feature.getMZ(),
                'rt': consensus_feature.getRT(),
                'mz_min': mz_min_local,
                'mz_max': mz_max_local,
                'rt_min': rt_min_local,
                'rt_max': rt_max_local,
                'intensity': consensus_feature.getIntensity(),
                'quality': consensus_feature.getQuality(),
                'feature_uids': feature_uids,
                'feature_data_list': feature_data_list,
                'sample_uids': sample_uids,
                'sample_count': len(feature_data_list)
            }
            
            all_chunk_consensus.append(chunk_consensus_data)
            consensus_id_counter += 1

    if not all_chunk_consensus:
        # No valid consensus features found
        self.consensus_df = pl.DataFrame()
        self.consensus_mapping_df = pl.DataFrame()
        return
    
    # Perform cross-chunk clustering using optimized spatial indexing
    def _cluster_chunk_consensus(chunk_consensus_list: list, rt_tol: float, mz_tol: float) -> list:
        """Cluster chunk consensus features using interval overlap (no over-relaxation).

        A union is formed if either centroids are within tolerance OR their RT / m/z
        intervals (expanded by tolerance) overlap, and they originate from different chunks.
        """
        if not chunk_consensus_list:
            return []

        n_features = len(chunk_consensus_list)

        # Spatial bins using strict tolerances (improves candidate reduction without recall loss)
        rt_bin_size = rt_tol if rt_tol > 0 else 1.0
        mz_bin_size = mz_tol if mz_tol > 0 else 0.01
        features_by_bin = defaultdict(list)

        for i, cf in enumerate(chunk_consensus_list):
            rt_bin = int(cf['rt'] / rt_bin_size)
            mz_bin = int(cf['mz'] / mz_bin_size)
            features_by_bin[(rt_bin, mz_bin)].append(i)

        class UF:
            def __init__(self, n):
                self.p = list(range(n))
                self.r = [0]*n
            def find(self, x):
                if self.p[x] != x:
                    self.p[x] = self.find(self.p[x])
                return self.p[x]
            def union(self, a,b):
                pa, pb = self.find(a), self.find(b)
                if pa == pb:
                    return
                if self.r[pa] < self.r[pb]:
                    pa, pb = pb, pa
                self.p[pb] = pa
                if self.r[pa] == self.r[pb]:
                    self.r[pa] += 1

        uf = UF(n_features)
        checked = set()
        for (rtb, mzb), idxs in features_by_bin.items():
            for dr in (-1,0,1):
                for dm in (-1,0,1):
                    neigh = (rtb+dr, mzb+dm)
                    if neigh not in features_by_bin:
                        continue
                    for i in idxs:
                        for j in features_by_bin[neigh]:
                            if i >= j:
                                continue
                            pair = (i,j)
                            if pair in checked:
                                continue
                            checked.add(pair)
                            a = chunk_consensus_list[i]
                            b = chunk_consensus_list[j]
                            if a['chunk_idx'] == b['chunk_idx']:
                                continue
                            # Centroid checks
                            centroid_close = (abs(a['rt']-b['rt']) <= rt_tol and abs(a['mz']-b['mz']) <= mz_tol)
                            # Interval overlap checks (expanded by tolerance)
                            rt_overlap = (a['rt_min'] - rt_tol) <= (b['rt_max'] + rt_tol) and (b['rt_min'] - rt_tol) <= (a['rt_max'] + rt_tol)
                            mz_overlap = (a['mz_min'] - mz_tol) <= (b['mz_max'] + mz_tol) and (b['mz_min'] - mz_tol) <= (a['mz_max'] + mz_tol)
                            if centroid_close or (rt_overlap and mz_overlap):
                                uf.union(i,j)

        groups_by_root = defaultdict(list)
        for i in range(n_features):
            groups_by_root[uf.find(i)].append(chunk_consensus_list[i])
        return list(groups_by_root.values())
    # (Obsolete relaxed + centroid stitching code removed.)

    # --- Stage 1: initial cross-chunk clustering of chunk consensus features ---
    initial_groups = _cluster_chunk_consensus(all_chunk_consensus, params.rt_tol, params.mz_tol)

    # --- Stage 2: centroid refinement (lightweight second pass) ---
    def _refine_groups(groups: list, rt_tol: float, mz_tol: float) -> list:
        """Refine groups by clustering group centroids (single-link) under same tolerances.

        This reconciles borderline splits left after interval-overlap clustering without
        re-introducing broad over-merging. Works on group centroids only (low cost).
        """
        if len(groups) <= 1:
            return groups
        # Build centroid list
        centroids = []  # (idx, rt, mz)
        for gi, g in enumerate(groups):
            if not g:
                continue
            rt_vals = [cf['rt'] for cf in g]
            mz_vals = [cf['mz'] for cf in g]
            if not rt_vals or not mz_vals:
                continue
            centroids.append((gi, float(np.mean(rt_vals)), float(np.mean(mz_vals))))
        if len(centroids) <= 1:
            return groups

        # Spatial binning for centroid clustering
        rt_bin = rt_tol if rt_tol > 0 else 1.0
        mz_bin = mz_tol if mz_tol > 0 else 0.01
        bins = defaultdict(list)
        for idx, rt_c, mz_c in centroids:
            bins[(int(rt_c/rt_bin), int(mz_c/mz_bin))].append((idx, rt_c, mz_c))

        # Union-Find over group indices
        parent = list(range(len(groups)))
        rank = [0]*len(groups)
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        def union(a,b):
            pa, pb = find(a), find(b)
            if pa == pb:
                return
            if rank[pa] < rank[pb]:
                pa, pb = pb, pa
            parent[pb] = pa
            if rank[pa] == rank[pb]:
                rank[pa] += 1

        checked = set()
        for (rb, mb), items in bins.items():
            for dr in (-1,0,1):
                for dm in (-1,0,1):
                    neigh_key = (rb+dr, mb+dm)
                    if neigh_key not in bins:
                        continue
                    for (gi, rt_i, mz_i) in items:
                        for (gj, rt_j, mz_j) in bins[neigh_key]:
                            if gi >= gj:
                                continue
                            pair = (gi, gj)
                            if pair in checked:
                                continue
                            checked.add(pair)
                            if abs(rt_i-rt_j) <= rt_tol and abs(mz_i-mz_j) <= mz_tol:
                                union(gi, gj)

        merged = defaultdict(list)
        for gi, g in enumerate(groups):
            merged[find(gi)].extend(g)
        return list(merged.values())

    refined_groups = _refine_groups(initial_groups, params.rt_tol, params.mz_tol)

    # --- Stage 3: build final consensus feature metadata and mapping ---
    consensus_metadata = []
    consensus_mapping_list = []
    consensus_uid_counter = 0

    for group in refined_groups:
        if not group:
            continue
        
        # Aggregate underlying feature data (deduplicated by feature_uid)
        feature_data_acc = {}
        sample_uids_acc = set()
        rt_values_chunk = []  # use chunk-level centroids for statistic helper
        mz_values_chunk = []
        intensity_values_chunk = []
        quality_values_chunk = []

        for cf in group:
            rt_values_chunk.append(cf['rt'])
            mz_values_chunk.append(cf['mz'])
            intensity_values_chunk.append(cf.get('intensity', 0.0) or 0.0)
            quality_values_chunk.append(cf.get('quality', 1.0) or 1.0)
            
            for fd, samp_uid in zip(cf['feature_data_list'], cf['sample_uids']):
                fid = fd.get('feature_uid') or fd.get('uid') or fd.get('feature_id')
                # feature_uid expected in fd under 'feature_uid'; fallback attempts just in case
                if fid is None:
                    continue
                if fid not in feature_data_acc:
                    feature_data_acc[fid] = fd
                sample_uids_acc.add(samp_uid)
                
        if not feature_data_acc:
            continue

        number_samples = len(sample_uids_acc)
        
        # NOTE: Don't filter by min_samples here - let _finalize_merge handle it
        # This allows proper cross-chunk consensus building before final filtering

        metadata = _calculate_consensus_statistics(
            self,
            consensus_uid_counter,
            list(feature_data_acc.values()),
            rt_values_chunk,
            mz_values_chunk,
            intensity_values_chunk,
            quality_values_chunk,
            number_features=len(feature_data_acc),
            number_samples=number_samples,
            cached_adducts_df=cached_adducts_df,
            cached_valid_adducts=cached_valid_adducts,
        )
        consensus_metadata.append(metadata)

        # Build mapping rows (deduplicated)
        for fid, fd in feature_data_acc.items():
            samp_uid = fd.get('sample_uid') or fd.get('sample_id') or fd.get('sample')
            # If absent we attempt to derive from original group sample_uids pairing
            # but most feature_data rows should include sample_uid already.
            if samp_uid is None:
                # fallback: search for cf containing this fid
                for cf in group:
                    for fd2, samp2 in zip(cf['feature_data_list'], cf['sample_uids']):
                        f2id = fd2.get('feature_uid') or fd2.get('uid') or fd2.get('feature_id')
                        if f2id == fid:
                            samp_uid = samp2
                            break
                    if samp_uid is not None:
                        break
            if samp_uid is None:
                continue
            consensus_mapping_list.append({
                'consensus_uid': consensus_uid_counter,
                'sample_uid': samp_uid,
                'feature_uid': fid,
            })

        consensus_uid_counter += 1

    # Assign DataFrames
    self.consensus_df = pl.DataFrame(consensus_metadata, strict=False)
    self.consensus_mapping_df = pl.DataFrame(consensus_mapping_list, strict=False)

    # Ensure mapping only contains features from retained consensus_df
    if len(self.consensus_df) > 0:
        valid_consensus_ids = set(self.consensus_df['consensus_uid'].to_list())
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            pl.col('consensus_uid').is_in(list(valid_consensus_ids))
        )
    else:
        self.consensus_mapping_df = pl.DataFrame()

    # Attach empty consensus_map placeholder for downstream compatibility
    self.consensus_map = oms.ConsensusMap()
    return


def _calculate_consensus_statistics(study_obj, consensus_uid: int, feature_data_list: list, 
                                  rt_values: list, mz_values: list, 
                                  intensity_values: list, quality_values: list,
                                  number_features: int = None, number_samples: int = None,
                                  cached_adducts_df=None, cached_valid_adducts=None) -> dict:
    """
    Calculate comprehensive statistics for a consensus feature from aggregated feature data.
    
    Args:
        consensus_uid: Unique ID for this consensus feature
        feature_data_list: List of individual feature dictionaries
        rt_values: RT values from chunk consensus features
        mz_values: m/z values from chunk consensus features  
        intensity_values: Intensity values from chunk consensus features
        quality_values: Quality values from chunk consensus features
        
    Returns:
        Dictionary with consensus feature metadata
    """
    if not feature_data_list:
        return {}
    
    # Convert feature data to numpy arrays for vectorized computation
    rt_feat_values = np.array([fd.get("rt", 0) for fd in feature_data_list if fd.get("rt") is not None])
    mz_feat_values = np.array([fd.get("mz", 0) for fd in feature_data_list if fd.get("mz") is not None])
    rt_start_values = np.array([fd.get("rt_start", 0) for fd in feature_data_list if fd.get("rt_start") is not None])
    rt_end_values = np.array([fd.get("rt_end", 0) for fd in feature_data_list if fd.get("rt_end") is not None])
    rt_delta_values = np.array([fd.get("rt_delta", 0) for fd in feature_data_list if fd.get("rt_delta") is not None])
    mz_start_values = np.array([fd.get("mz_start", 0) for fd in feature_data_list if fd.get("mz_start") is not None])
    mz_end_values = np.array([fd.get("mz_end", 0) for fd in feature_data_list if fd.get("mz_end") is not None])
    inty_values = np.array([fd.get("inty", 0) for fd in feature_data_list if fd.get("inty") is not None])
    coherence_values = np.array([fd.get("chrom_coherence", 0) for fd in feature_data_list if fd.get("chrom_coherence") is not None])
    prominence_values = np.array([fd.get("chrom_prominence", 0) for fd in feature_data_list if fd.get("chrom_prominence") is not None])
    prominence_scaled_values = np.array([fd.get("chrom_prominence_scaled", 0) for fd in feature_data_list if fd.get("chrom_prominence_scaled") is not None])
    height_scaled_values = np.array([fd.get("chrom_height_scaled", 0) for fd in feature_data_list if fd.get("chrom_height_scaled") is not None])
    iso_values = np.array([fd.get("iso", 0) for fd in feature_data_list if fd.get("iso") is not None])
    charge_values = np.array([fd.get("charge", 0) for fd in feature_data_list if fd.get("charge") is not None])
    
    # Process adducts with cached validation
    all_adducts = []
    valid_adducts = cached_valid_adducts if cached_valid_adducts is not None else set()
    valid_adducts.add("?")  # Always allow '?' adducts
    
    for fd in feature_data_list:
        adduct = fd.get("adduct")
        if adduct is not None:
            # Only include adducts that are valid (from cached study adducts or contain '?')
            if adduct in valid_adducts or "?" in adduct:
                all_adducts.append(adduct)
    
    # Calculate adduct consensus
    adduct_values = []
    adduct_top = None
    adduct_charge_top = None
    adduct_mass_neutral_top = None
    adduct_mass_shift_top = None
    
    if all_adducts:
        adduct_counts = {adduct: all_adducts.count(adduct) for adduct in set(all_adducts)}
        total_count = sum(adduct_counts.values())
        for adduct, count in adduct_counts.items():
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            adduct_values.append([str(adduct), int(count), float(round(percentage, 2))])
        
        adduct_values.sort(key=lambda x: x[1], reverse=True)
        
        if adduct_values:
            adduct_top = adduct_values[0][0]
            # Try to get charge and mass shift from cached study adducts
            adduct_found = False
            if cached_adducts_df is not None and not cached_adducts_df.is_empty():
                matching_adduct = cached_adducts_df.filter(
                    pl.col("name") == adduct_top,
                )
                if not matching_adduct.is_empty():
                    adduct_row = matching_adduct.row(0, named=True)
                    adduct_charge_top = adduct_row["charge"]
                    adduct_mass_shift_top = adduct_row["mass_shift"]
                    adduct_found = True
            
            if not adduct_found:
                # Set default charge and mass shift for top adduct
                adduct_charge_top = 1
                adduct_mass_shift_top = 1.007825
    else:
        # Default adduct based on study polarity
        study_polarity = getattr(study_obj, "polarity", "positive")
        if study_polarity in ["negative", "neg"]:
            adduct_top = "[M-?]1-"
            adduct_charge_top = -1
            adduct_mass_shift_top = -1.007825
        else:
            adduct_top = "[M+?]1+"
            adduct_charge_top = 1
            adduct_mass_shift_top = 1.007825
        
        adduct_values = [[adduct_top, 1, 100.0]]
    
    # Calculate neutral mass
    consensus_mz = round(float(np.mean(mz_values)), 4) if len(mz_values) > 0 else 0.0
    if adduct_charge_top and adduct_mass_shift_top is not None:
        adduct_mass_neutral_top = consensus_mz * abs(adduct_charge_top) - adduct_mass_shift_top
    
    # Calculate MS2 count
    ms2_count = 0
    for fd in feature_data_list:
        ms2_scans = fd.get("ms2_scans")
        if ms2_scans is not None:
            ms2_count += len(ms2_scans)
    
    # Build consensus metadata
    return {
        "consensus_uid": int(consensus_uid),
        "consensus_id": str(consensus_uid),  # Use simple string ID
        "quality": round(float(np.mean(quality_values)), 3) if len(quality_values) > 0 else 1.0,
        "number_samples": number_samples if number_samples is not None else len(feature_data_list),
        "rt": round(float(np.mean(rt_values)), 4) if len(rt_values) > 0 else 0.0,
        "mz": consensus_mz,
        "rt_min": round(float(np.min(rt_feat_values)), 3) if len(rt_feat_values) > 0 else 0.0,
        "rt_max": round(float(np.max(rt_feat_values)), 3) if len(rt_feat_values) > 0 else 0.0,
        "rt_mean": round(float(np.mean(rt_feat_values)), 3) if len(rt_feat_values) > 0 else 0.0,
        "rt_start_mean": round(float(np.mean(rt_start_values)), 3) if len(rt_start_values) > 0 else 0.0,
        "rt_end_mean": round(float(np.mean(rt_end_values)), 3) if len(rt_end_values) > 0 else 0.0,
        "rt_delta_mean": round(float(np.mean(rt_delta_values)), 3) if len(rt_delta_values) > 0 else 0.0,
        "mz_min": round(float(np.min(mz_feat_values)), 4) if len(mz_feat_values) > 0 else 0.0,
        "mz_max": round(float(np.max(mz_feat_values)), 4) if len(mz_feat_values) > 0 else 0.0,
        "mz_mean": round(float(np.mean(mz_feat_values)), 4) if len(mz_feat_values) > 0 else 0.0,
        "mz_start_mean": round(float(np.mean(mz_start_values)), 4) if len(mz_start_values) > 0 else 0.0,
        "mz_end_mean": round(float(np.mean(mz_end_values)), 4) if len(mz_end_values) > 0 else 0.0,
        "inty_mean": round(float(np.mean(inty_values)), 0) if len(inty_values) > 0 else 0.0,
        "bl": -1.0,
        "chrom_coherence_mean": round(float(np.mean(coherence_values)), 3) if len(coherence_values) > 0 else 0.0,
        "chrom_prominence_mean": round(float(np.mean(prominence_values)), 0) if len(prominence_values) > 0 else 0.0,
        "chrom_prominence_scaled_mean": round(float(np.mean(prominence_scaled_values)), 3) if len(prominence_scaled_values) > 0 else 0.0,
        "chrom_height_scaled_mean": round(float(np.mean(height_scaled_values)), 3) if len(height_scaled_values) > 0 else 0.0,
        "iso_mean": round(float(np.mean(iso_values)), 2) if len(iso_values) > 0 else 0.0,
        "charge_mean": round(float(np.mean(charge_values)), 2) if len(charge_values) > 0 else 0.0,
        "number_ms2": int(ms2_count),
        "adducts": adduct_values,
        "adduct_top": adduct_top,
        "adduct_charge_top": adduct_charge_top,
        "adduct_mass_neutral_top": round(adduct_mass_neutral_top, 6) if adduct_mass_neutral_top is not None else None,
        "adduct_mass_shift_top": round(adduct_mass_shift_top, 6) if adduct_mass_shift_top is not None else None,
        "id_top_name": None,
        "id_top_class": None,
        "id_top_adduct": None,
        "id_top_score": None,
    }


def _cluster_consensus_features(features: list, rt_tol: float, mz_tol: float) -> list:
    """
    Cluster consensus features from different chunks based on RT and m/z similarity.
    
    Args:
        features: List of feature dictionaries with 'mz', 'rt', 'id' keys
        rt_tol: RT tolerance in seconds
        mz_tol: m/z tolerance in Da
        
    Returns:
        List of groups, where each group is a list of feature dictionaries
    """
    if not features:
        return []
    
    # Use Union-Find for efficient clustering
    class UnionFind:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
    
    n_features = len(features)
    uf = UnionFind(n_features)
    
    # Build distance matrix and cluster features within tolerance
    for i in range(n_features):
        for j in range(i + 1, n_features):
            feat_i = features[i]
            feat_j = features[j]
            
            # Skip if features are from the same chunk (they're already processed)
            if feat_i['chunk_idx'] == feat_j['chunk_idx']:
                continue
            
            mz_diff = abs(feat_i['mz'] - feat_j['mz'])
            rt_diff = abs(feat_i['rt'] - feat_j['rt'])
            
            # Cluster if within tolerance
            if mz_diff <= mz_tol and rt_diff <= rt_tol:
                uf.union(i, j)
    
    # Extract groups
    groups_by_root = {}
    for i in range(n_features):
        root = uf.find(i)
        if root not in groups_by_root:
            groups_by_root[root] = []
        groups_by_root[root].append(features[i])
    
    return list(groups_by_root.values())


# Note: Restored proper chunked implementation with cross-chunk consensus clustering


def _reset_consensus_data(self):
    """Reset consensus-related DataFrames at the start of merge."""
    self.consensus_df = pl.DataFrame()
    self.consensus_ms2 = pl.DataFrame()
    self.consensus_mapping_df = pl.DataFrame()


def _extract_consensus_features(self, consensus_map, min_samples, cached_adducts_df=None, cached_valid_adducts=None):
    """Extract consensus features and build metadata."""
    # create a dict to map uid to feature_uid using self.features_df
    feature_uid_map = {
        row["feature_id"]: row["feature_uid"]
        for row in self.features_df.iter_rows(named=True)
    }
    imax = consensus_map.size()

    self.logger.debug(f"Found {imax} feature groups by clustering.")

    # Pre-build fast lookup tables for features_df data using optimized approach
    features_lookup = _optimized_feature_lookup(self, self.features_df)

    # create a list to store the consensus mapping
    consensus_mapping = []
    metadata_list = []

    tqdm_disable = self.log_level not in ["TRACE", "DEBUG"]

    for i, feature in enumerate(
        tqdm(
            consensus_map,
            total=imax,
            disable=tqdm_disable,
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extract metadata",
        ),
    ):
        # get all features in the feature map with the same unique id as the consensus feature
        features_list = feature.getFeatureList()
        uids = []
        feature_data_list = []

        for _j, f in enumerate(features_list):
            fuid = str(f.getUniqueId())
            if fuid not in feature_uid_map:
                # this is a feature that was removed but is still in the feature maps
                continue
            fuid = feature_uid_map[fuid]
            consensus_mapping.append(
                {
                    "consensus_uid": i,
                    "sample_uid": f.getMapIndex() + 1,
                    "feature_uid": fuid,
                },
            )
            uids.append(fuid)

            # Get feature data from lookup instead of DataFrame filtering
            feature_data = features_lookup.get(fuid)
            if feature_data:
                feature_data_list.append(feature_data)

        if not feature_data_list:
            # Skip this consensus feature if no valid features found
            continue

        # Compute statistics using vectorized operations on collected data
        # Convert to numpy arrays for faster computation
        rt_values = np.array(
            [fd.get("rt", 0) for fd in feature_data_list if fd.get("rt") is not None],
        )
        mz_values = np.array(
            [fd.get("mz", 0) for fd in feature_data_list if fd.get("mz") is not None],
        )
        rt_start_values = np.array(
            [
                fd.get("rt_start", 0)
                for fd in feature_data_list
                if fd.get("rt_start") is not None
            ],
        )
        rt_end_values = np.array(
            [
                fd.get("rt_end", 0)
                for fd in feature_data_list
                if fd.get("rt_end") is not None
            ],
        )
        rt_delta_values = np.array(
            [
                fd.get("rt_delta", 0)
                for fd in feature_data_list
                if fd.get("rt_delta") is not None
            ],
        )
        mz_start_values = np.array(
            [
                fd.get("mz_start", 0)
                for fd in feature_data_list
                if fd.get("mz_start") is not None
            ],
        )
        mz_end_values = np.array(
            [
                fd.get("mz_end", 0)
                for fd in feature_data_list
                if fd.get("mz_end") is not None
            ],
        )
        inty_values = np.array(
            [
                fd.get("inty", 0)
                for fd in feature_data_list
                if fd.get("inty") is not None
            ],
        )
        coherence_values = np.array(
            [
                fd.get("chrom_coherence", 0)
                for fd in feature_data_list
                if fd.get("chrom_coherence") is not None
            ],
        )
        prominence_values = np.array(
            [
                fd.get("chrom_prominence", 0)
                for fd in feature_data_list
                if fd.get("chrom_prominence") is not None
            ],
        )
        prominence_scaled_values = np.array(
            [
                fd.get("chrom_prominence_scaled", 0)
                for fd in feature_data_list
                if fd.get("chrom_prominence_scaled") is not None
            ],
        )
        height_scaled_values = np.array(
            [
                fd.get("chrom_height_scaled", 0)
                for fd in feature_data_list
                if fd.get("chrom_height_scaled") is not None
            ],
        )
        iso_values = np.array(
            [fd.get("iso", 0) for fd in feature_data_list if fd.get("iso") is not None],
        )
        charge_values = np.array(
            [
                fd.get("charge", 0)
                for fd in feature_data_list
                if fd.get("charge") is not None
            ],
        )

        # adduct_values
        # Collect all adducts from feature_data_list to create consensus adduct information
        # Only consider adducts that are in study._get_adducts() plus items with '?'
        all_adducts = []
        adduct_masses = {}

        # Get valid adducts from cached result (avoid repeated _get_adducts() calls)
        valid_adducts = cached_valid_adducts if cached_valid_adducts is not None else set()
        valid_adducts.add("?")  # Always allow '?' adducts

        for fd in feature_data_list:
            # Get individual adduct and mass from each feature data (fd)
            adduct = fd.get("adduct")
            adduct_mass = fd.get("adduct_mass")

            if adduct is not None:
                # Only include adducts that are valid (from study._get_adducts() or contain '?')
                if adduct in valid_adducts or "?" in adduct:
                    all_adducts.append(adduct)
                    if adduct_mass is not None:
                        adduct_masses[adduct] = adduct_mass

        # Calculate adduct_values for the consensus feature
        adduct_values = []
        if all_adducts:
            adduct_counts = {
                adduct: all_adducts.count(adduct) for adduct in set(all_adducts)
            }
            total_count = sum(adduct_counts.values())
            for adduct, count in adduct_counts.items():
                percentage = (count / total_count) * 100 if total_count > 0 else 0
                # Store as list with [name, num, %] format for the adducts column
                adduct_values.append(
                    [
                        str(adduct),
                        int(count),
                        float(round(percentage, 2)),
                    ],
                )

        # Sort adduct_values by count in descending order
        adduct_values.sort(key=lambda x: x[1], reverse=True)  # Sort by count (index 1)
        # Store adduct_values for use in metadata
        consensus_adduct_values = adduct_values

        # Extract top adduct information for new columns
        adduct_top = None
        adduct_charge_top = None
        adduct_mass_neutral_top = None
        adduct_mass_shift_top = None

        if consensus_adduct_values:
            top_adduct_name = consensus_adduct_values[0][0]  # Get top adduct name
            adduct_top = top_adduct_name

            # Parse adduct information to extract charge and mass shift
            # Handle "?" as "H" and parse common adduct formats
            if top_adduct_name == "?" or top_adduct_name == "[M+?]+":
                adduct_charge_top = 1
                adduct_mass_shift_top = 1.007825  # H mass
            elif top_adduct_name == "[M+?]-":
                adduct_charge_top = -1
                adduct_mass_shift_top = -1.007825  # -H mass
            else:
                # Try to get charge and mass shift from cached study adducts
                adduct_found = False
                if cached_adducts_df is not None and not cached_adducts_df.is_empty():
                    # Look for exact match in study adducts
                    matching_adduct = cached_adducts_df.filter(
                        pl.col("name") == top_adduct_name,
                    )
                    if not matching_adduct.is_empty():
                        adduct_row = matching_adduct.row(0, named=True)
                        adduct_charge_top = adduct_row["charge"]
                        adduct_mass_shift_top = adduct_row["mass_shift"]
                        adduct_found = True

                if not adduct_found:
                    # Fallback to regex parsing
                    import re

                    # Pattern for adducts like [M+H]+, [M-H]-, [M+Na]+, etc.
                    pattern = r"\[M([+\-])([A-Za-z0-9]+)\]([0-9]*)([+\-])"
                    match = re.match(pattern, top_adduct_name)

                    if match:
                        sign = match.group(1)
                        element = match.group(2)
                        multiplier_str = match.group(3)
                        charge_sign = match.group(4)

                        multiplier = int(multiplier_str) if multiplier_str else 1
                        charge = multiplier if charge_sign == "+" else -multiplier
                        adduct_charge_top = charge

                        # Calculate mass shift based on element
                        element_masses = {
                            "H": 1.007825,
                            "Na": 22.989769,
                            "K": 38.963708,
                            "NH4": 18.033823,
                            "Li": 7.016930,
                            "Cl": 34.969401,
                            "Br": 78.918885,
                            "HCOO": 44.998201,
                            "CH3COO": 59.013851,
                            "H2O": 18.010565,
                        }

                        base_mass = element_masses.get(
                            element,
                            1.007825,
                        )  # Default to H if unknown
                        mass_shift = (
                            base_mass * multiplier
                            if sign == "+"
                            else -base_mass * multiplier
                        )
                        adduct_mass_shift_top = mass_shift
                    else:
                        # Default fallback
                        adduct_charge_top = 1
                        adduct_mass_shift_top = 1.007825
        else:
            # No valid adducts found - assign default based on study polarity
            study_polarity = getattr(self, "polarity", "positive")
            if study_polarity in ["negative", "neg"]:
                # Negative mode default
                adduct_top = "[M-?]1-"
                adduct_charge_top = -1
                adduct_mass_shift_top = -1.007825  # -H mass (loss of proton)
            else:
                # Positive mode default (includes 'positive', 'pos', or any other value)
                adduct_top = "[M+?]1+"
                adduct_charge_top = 1
                adduct_mass_shift_top = 1.007825  # H mass (gain of proton)

            # Create a single default adduct entry in the adducts list for consistency
            consensus_adduct_values = [[adduct_top, 1, 100.0]]

        # Calculate neutral mass from consensus mz (for both cases)
        consensus_mz = (
            round(float(np.mean(mz_values)), 4) if len(mz_values) > 0 else 0.0
        )
        if adduct_charge_top and adduct_mass_shift_top is not None:
            adduct_mass_neutral_top = (
                consensus_mz * abs(adduct_charge_top) - adduct_mass_shift_top
            )

        # Calculate number of MS2 spectra
        ms2_count = 0
        for fd in feature_data_list:
            ms2_scans = fd.get("ms2_scans")
            if ms2_scans is not None:
                ms2_count += len(ms2_scans)

        metadata_list.append(
            {
                "consensus_uid": int(i),  # "consensus_id": i,
                "consensus_id": str(feature.getUniqueId()),
                "quality": round(float(feature.getQuality()), 3),
                "number_samples": len(feature_data_list),
                # "number_ext": int(len(features_list)),
                "rt": round(float(np.mean(rt_values)), 4)
                if len(rt_values) > 0
                else 0.0,
                "mz": round(float(np.mean(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "rt_min": round(float(np.min(rt_values)), 3)
                if len(rt_values) > 0
                else 0.0,
                "rt_max": round(float(np.max(rt_values)), 3)
                if len(rt_values) > 0
                else 0.0,
                "rt_mean": round(float(np.mean(rt_values)), 3)
                if len(rt_values) > 0
                else 0.0,
                "rt_start_mean": round(float(np.mean(rt_start_values)), 3)
                if len(rt_start_values) > 0
                else 0.0,
                "rt_end_mean": round(float(np.mean(rt_end_values)), 3)
                if len(rt_end_values) > 0
                else 0.0,
                "rt_delta_mean": round(float(np.ptp(rt_delta_values)), 3)
                if len(rt_delta_values) > 0
                else 0.0,
                "mz_min": round(float(np.min(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "mz_max": round(float(np.max(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "mz_mean": round(float(np.mean(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "mz_start_mean": round(float(np.mean(mz_start_values)), 4)
                if len(mz_start_values) > 0
                else 0.0,
                "mz_end_mean": round(float(np.mean(mz_end_values)), 4)
                if len(mz_end_values) > 0
                else 0.0,
                "inty_mean": round(float(np.mean(inty_values)), 0)
                if len(inty_values) > 0
                else 0.0,
                "bl": -1.0,
                "chrom_coherence_mean": round(float(np.mean(coherence_values)), 3)
                if len(coherence_values) > 0
                else 0.0,
                "chrom_prominence_mean": round(float(np.mean(prominence_values)), 0)
                if len(prominence_values) > 0
                else 0.0,
                "chrom_prominence_scaled_mean": round(
                    float(np.mean(prominence_scaled_values)),
                    3,
                )
                if len(prominence_scaled_values) > 0
                else 0.0,
                "chrom_height_scaled_mean": round(
                    float(np.mean(height_scaled_values)),
                    3,
                )
                if len(height_scaled_values) > 0
                else 0.0,
                "iso_mean": round(float(np.mean(iso_values)), 2)
                if len(iso_values) > 0
                else 0.0,
                "charge_mean": round(float(np.mean(charge_values)), 2)
                if len(charge_values) > 0
                else 0.0,
                "number_ms2": int(ms2_count),
                "adducts": consensus_adduct_values
                if consensus_adduct_values
                else [],  # Ensure it's always a list
                # New columns for top-ranked adduct information
                "adduct_top": adduct_top,
                "adduct_charge_top": adduct_charge_top,
                "adduct_mass_neutral_top": round(adduct_mass_neutral_top, 6)
                if adduct_mass_neutral_top is not None
                else None,
                "adduct_mass_shift_top": round(adduct_mass_shift_top, 6)
                if adduct_mass_shift_top is not None
                else None,
                # New columns for top-scoring identification results
                "id_top_name": None,
                "id_top_class": None,
                "id_top_adduct": None,
                "id_top_score": None,
            },
        )

    consensus_mapping_df = pl.DataFrame(consensus_mapping)
    # remove all rows in consensus_mapping_df where consensus_id is not in self.featured_df['uid']
    l1 = len(consensus_mapping_df)
    consensus_mapping_df = consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(self.features_df["feature_uid"].to_list()),
    )
    self.logger.debug(
        f"Filtered {l1 - len(consensus_mapping_df)} orphan features from maps.",
    )
    self.consensus_mapping_df = consensus_mapping_df
    self.consensus_df = pl.DataFrame(metadata_list, strict=False)

    if min_samples is None:
        min_samples = 1
    if min_samples < 1:
        min_samples = int(min_samples * len(self.samples_df))

    # Validate that min_samples doesn't exceed the number of samples
    if min_samples > len(self.samples_df):
        self.logger.warning(
            f"min_samples ({min_samples}) exceeds the number of samples ({len(self.samples_df)}). "
            f"Setting min_samples to {len(self.samples_df)}.",
        )
        min_samples = len(self.samples_df)

    # filter out consensus features with less than min_samples features
    l1 = len(self.consensus_df)
    self.consensus_df = self.consensus_df.filter(
        pl.col("number_samples") >= min_samples,
    )
    self.logger.debug(
        f"Filtered {l1 - len(self.consensus_df)} consensus features with less than {min_samples} samples.",
    )
    # filter out consensus mapping with less than min_samples features
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(self.consensus_df["consensus_uid"].to_list()),
    )

    self.consensus_map = consensus_map


def _perform_adduct_grouping(self, rt_tol, mz_tol):
    """Perform adduct grouping on consensus features."""
    import polars as pl
    
    # Add adduct grouping and adduct_of assignment
    if len(self.consensus_df) > 0:
        # Get relevant columns for grouping
        consensus_data = []
        for row in self.consensus_df.iter_rows(named=True):
            consensus_data.append(
                {
                    "consensus_uid": row["consensus_uid"],
                    "rt": row["rt"],
                    "adduct_mass_neutral_top": row.get("adduct_mass_neutral_top"),
                    "adduct_top": row.get("adduct_top"),
                    "inty_mean": row.get("inty_mean", 0),
                },
            )

        # Use optimized adduct grouping
        adduct_group_list, adduct_of_list = _optimized_adduct_grouping(
            self, consensus_data, rt_tol, mz_tol
        )

        # Add the new columns to consensus_df
        self.consensus_df = self.consensus_df.with_columns(
            [
                pl.Series("adduct_group", adduct_group_list, dtype=pl.Int64),
                pl.Series("adduct_of", adduct_of_list, dtype=pl.Int64),
            ],
        )


def _finalize_merge(self, link_ms2, min_samples):
    """Complete the merge process with final calculations and cleanup."""
    import polars as pl
    
    # Check if consensus_df is empty or missing required columns
    if len(self.consensus_df) == 0 or "number_samples" not in self.consensus_df.columns:
        self.logger.debug("No consensus features found or consensus_df is empty. Skipping finalize merge.")
        return
    
    # Validate min_samples parameter
    if min_samples is None:
        min_samples = 1
    if min_samples < 1:
        min_samples = int(min_samples * len(self.samples_df))

    # Validate that min_samples doesn't exceed the number of samples
    if min_samples > len(self.samples_df):
        self.logger.warning(
            f"min_samples ({min_samples}) exceeds the number of samples ({len(self.samples_df)}). "
            f"Setting min_samples to {len(self.samples_df)}.",
        )
        min_samples = len(self.samples_df)

    # Filter out consensus features with less than min_samples features
    l1 = len(self.consensus_df)
    self.consensus_df = self.consensus_df.filter(
        pl.col("number_samples") >= min_samples,
    )
    self.logger.debug(
        f"Filtered {l1 - len(self.consensus_df)} consensus features with less than {min_samples} samples.",
    )
    
    # Filter out consensus mapping with less than min_samples features
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(self.consensus_df["consensus_uid"].to_list()),
    )

    # Calculate the completeness of the consensus map
    if len(self.consensus_df) > 0 and len(self.samples_df) > 0:
        c = (
            len(self.consensus_mapping_df)
            / len(self.consensus_df)
            / len(self.samples_df)
        )
        self.logger.info(
            f"Merging completed. Consensus features: {len(self.consensus_df)}. Completeness: {c:.2f}.",
        )
    else:
        self.logger.warning(
            f"Merging completed with empty result. Consensus features: {len(self.consensus_df)}. "
            f"This may be due to min_samples ({min_samples}) being too high for the available data.",
        )
    
    if link_ms2:
        self.find_ms2()


def _optimized_feature_lookup(study_obj, features_df):
    """
    Optimized feature lookup creation using Polars operations.
    """
    study_obj.logger.debug("Creating optimized feature lookup...")
    start_time = time.time()
    
    # Use Polars select for faster conversion
    feature_columns = [
        "feature_uid", "rt", "mz", "rt_start", "rt_end", "rt_delta", 
        "mz_start", "mz_end", "inty", "chrom_coherence", "chrom_prominence", 
        "chrom_prominence_scaled", "chrom_height_scaled", "iso", "charge", 
        "ms2_scans", "adduct", "adduct_mass"
    ]
    
    # Filter to only existing columns
    existing_columns = [col for col in feature_columns if col in features_df.columns]
    
    # Convert to dictionary more efficiently
    selected_df = features_df.select(existing_columns)
    
    features_lookup = {}
    for row in selected_df.iter_rows(named=True):
        feature_uid = row["feature_uid"]
        # Keep feature_uid in the dictionary for chunked merge compatibility
        features_lookup[feature_uid] = {k: v for k, v in row.items()}
    
    lookup_time = time.time() - start_time
    if len(features_lookup) > 50000:
        study_obj.logger.debug(f"Feature lookup created in {lookup_time:.2f}s for {len(features_lookup)} features")
    return features_lookup


def _optimized_adduct_grouping(study_obj, consensus_data, rt_tol, mz_tol):
    """
    Optimized O(n log n) adduct grouping using spatial indexing.
    
    Args:
        study_obj: Study object with logger
        consensus_data: List of consensus feature dictionaries
        rt_tol: RT tolerance in minutes
        mz_tol: m/z tolerance in Da
        
    Returns:
        Tuple of (adduct_group_list, adduct_of_list)
    """
    if not consensus_data:
        return [], []
    
    n_features = len(consensus_data)
    if n_features > 10000:
        study_obj.logger.info(f"Adduct grouping for {n_features} consensus features...")
    else:
        study_obj.logger.debug(f"Adduct grouping for {n_features} consensus features...")
    
    # Build spatial index using RT and neutral mass as coordinates
    features_by_mass = defaultdict(list)
    mass_bin_size = mz_tol * 2  # 2x tolerance for conservative binning
    
    valid_features = []
    for feature in consensus_data:
        consensus_uid = feature["consensus_uid"]
        rt = feature["rt"]
        neutral_mass = feature.get("adduct_mass_neutral_top")
        intensity = feature.get("inty_mean", 0)
        adduct = feature.get("adduct_top", "")
        
        if neutral_mass is not None:
            mass_bin = int(neutral_mass / mass_bin_size)
            features_by_mass[mass_bin].append((consensus_uid, rt, neutral_mass, intensity, adduct))
            valid_features.append((consensus_uid, rt, neutral_mass, intensity, adduct, mass_bin))
    
    # Union-Find for efficient grouping
    class UnionFind:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
    
    uid_to_idx = {feature[0]: i for i, feature in enumerate(valid_features)}
    uf = UnionFind(len(valid_features))
    
    # Find groups using spatial index
    checked_pairs = set()
    for i, (uid1, rt1, mass1, inty1, adduct1, bin1) in enumerate(valid_features):
        for bin_offset in [-1, 0, 1]:
            check_bin = bin1 + bin_offset
            if check_bin not in features_by_mass:
                continue
                
            for uid2, rt2, mass2, inty2, adduct2 in features_by_mass[check_bin]:
                if uid1 >= uid2:
                    continue
                
                pair = (min(uid1, uid2), max(uid1, uid2))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                mass_diff = abs(mass1 - mass2)
                rt_diff = abs(rt1 - rt2) / 60.0  # Convert to minutes
                
                if mass_diff <= mz_tol and rt_diff <= rt_tol:
                    j = uid_to_idx[uid2]
                    uf.union(i, j)
    
    # Extract groups
    groups_by_root = defaultdict(list)
    for i, (uid, rt, mass, inty, adduct, _) in enumerate(valid_features):
        root = uf.find(i)
        groups_by_root[root].append((uid, rt, mass, inty, adduct))
    
    groups = {}
    group_id = 1
    assigned_groups = {}
    
    for group_members in groups_by_root.values():
        member_uids = [uid for uid, _, _, _, _ in group_members]
        
        for uid in member_uids:
            assigned_groups[uid] = group_id
        groups[group_id] = member_uids
        group_id += 1
    
    # Handle features without neutral mass
    for feature in consensus_data:
        uid = feature["consensus_uid"]
        if uid not in assigned_groups:
            assigned_groups[uid] = group_id
            groups[group_id] = [uid]
            group_id += 1
    
    # Determine adduct_of for each group
    group_adduct_of = {}
    for grp_id, member_uids in groups.items():
        best_uid = None
        best_priority = -1
        best_intensity = 0
        
        for uid in member_uids:
            feature_data = next((f for f in consensus_data if f["consensus_uid"] == uid), None)
            if not feature_data:
                continue
                
            adduct = feature_data.get("adduct_top", "")
            intensity = feature_data.get("inty_mean", 0)
            
            priority = 0
            if adduct and ("[M+H]" in adduct or adduct == "H" or adduct == "?"):
                priority = 3
            elif adduct and "[M-H]" in adduct:
                priority = 2
            elif adduct and "M" in adduct:
                priority = 1
            
            if priority > best_priority or (priority == best_priority and intensity > best_intensity):
                best_uid = uid
                best_priority = priority
                best_intensity = intensity
        
        group_adduct_of[grp_id] = best_uid if best_uid else member_uids[0]
    
    # Build final lists in same order as consensus_data
    adduct_group_list = []
    adduct_of_list = []
    
    for feature in consensus_data:
        uid = feature["consensus_uid"]
        group = assigned_groups.get(uid, 0)
        adduct_of = group_adduct_of.get(group, uid)
        
        adduct_group_list.append(group)
        adduct_of_list.append(adduct_of)
    
    if n_features > 10000:
        study_obj.logger.info("Adduct grouping completed.")
    else:
        study_obj.logger.debug("Adduct grouping completed.")

    return adduct_group_list, adduct_of_list
