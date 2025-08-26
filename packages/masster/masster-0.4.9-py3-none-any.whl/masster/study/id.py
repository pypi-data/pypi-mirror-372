"""study/id.py

Identification helpers for Study: load a Lib and identify consensus features
by matching m/z (and optionally RT).
"""

from __future__ import annotations


import polars as pl


def lib_load(
    study,
    lib_source,
    polarity: str | None = None,
    adducts: list | None = None,
):
    """Load a co    # Add compound and formula count columns
    if "consensus_uid" in result_df.columns:
        # Calculate counts per consensus_uid
        count_stats = result_df.group_by("consensus_uid").agg([
            pl.col("cmpd_uid").filter(pl.col("cmpd_uid").is_not_null()).n_unique().alias("num_cmpds") if "cmpd_uid" in result_df.columns else pl.lit(None).alias("num_cmpds"),
            pl.col("formula").filter(pl.col("formula").is_not_null()).n_unique().alias("num_formulas") if "formula" in result_df.columns else pl.lit(None).alias("num_formulas")
        ])library into the study.

    Args:
        study: Study instance
        lib_source: either a CSV file path (str) or a Lib instance
        polarity: ionization polarity ("positive" or "negative") - used when lib_source is a CSV path
        adducts: specific adducts to generate - used when lib_source is a CSV path

    Side effects:
        sets study.lib_df to a Polars DataFrame and stores the lib object on
        study._lib for later reference.
    """
    # Lazy import to avoid circular imports at module import time
    try:
        from masster.lib.lib import Lib
    except Exception:
        Lib = None

    if lib_source is None:
        raise ValueError("lib_source must be a CSV file path (str) or a Lib instance")

    # Use study polarity if not explicitly provided
    if polarity is None:
        study_polarity = getattr(study, "polarity", "positive")
        # Normalize polarity names
        if study_polarity in ["pos", "positive"]:
            polarity = "positive"
        elif study_polarity in ["neg", "negative"]:
            polarity = "negative"
        else:
            polarity = "positive"  # Default fallback

    # Handle string input (CSV file path)
    if isinstance(lib_source, str):
        if Lib is None:
            raise ImportError(
                "Could not import masster.lib.lib.Lib - required for CSV loading",
            )

        lib_obj = Lib()
        lib_obj.import_csv(lib_source, polarity=polarity, adducts=adducts)

    # Handle Lib instance
    elif Lib is not None and isinstance(lib_source, Lib):
        lib_obj = lib_source

    # Handle other objects with lib_df attribute
    elif hasattr(lib_source, "lib_df"):
        lib_obj = lib_source

    else:
        raise TypeError(
            "lib_source must be a CSV file path (str), a masster.lib.Lib instance, or have a 'lib_df' attribute",
        )

    # Ensure lib_df is populated
    lf = getattr(lib_obj, "lib_df", None)
    if lf is None or (hasattr(lf, "is_empty") and lf.is_empty()):
        raise ValueError("Library has no data populated in lib_df")

    # Filter by polarity to match study
    # Map polarity to charge signs
    if polarity == "positive":
        target_charges = [1, 2]  # positive charges
    elif polarity == "negative":
        target_charges = [-1, -2]  # negative charges
    else:
        target_charges = [-2, -1, 1, 2]  # all charges

    # Filter library entries by charge sign (which corresponds to polarity)
    filtered_lf = lf.filter(pl.col("z").is_in(target_charges))

    if filtered_lf.is_empty():
        print(
            f"Warning: No library entries found for polarity '{polarity}'. Using all entries.",
        )
        filtered_lf = lf

    # Store pointer and DataFrame on study
    study._lib = lib_obj

    # Add to existing lib_df instead of replacing
    if (
        hasattr(study, "lib_df")
        and study.lib_df is not None
        and not study.lib_df.is_empty()
    ):
        # Concatenate with existing data
        study.lib_df = pl.concat([study.lib_df, filtered_lf])
    else:
        # First time loading - create new
        try:
            study.lib_df = (
                filtered_lf.clone()
                if hasattr(filtered_lf, "clone")
                else pl.DataFrame(filtered_lf)
            )
        except Exception:
            study.lib_df = (
                pl.from_pandas(filtered_lf)
                if hasattr(filtered_lf, "to_pandas")
                else pl.DataFrame(filtered_lf)
            )

    # Store this operation in history
    if hasattr(study, "store_history"):
        study.store_history(
            ["lib_load"],
            {"lib_source": str(lib_source), "polarity": polarity, "adducts": adducts},
        )


def identify(study, features=None, params=None, **kwargs):
    """Identify consensus features against the loaded library.

    Matches consensus_df.mz against lib_df.mz within mz_tolerance. If rt_tolerance
    is provided and both consensus and library entries have rt values, RT is
    used as an additional filter.

    Args:
        study: Study instance
        features: Optional DataFrame or list of consensus_uids to identify.
                 If None, identifies all consensus features.
        params: Optional identify_defaults instance with matching tolerances and scoring parameters.
                If None, uses default parameters.
        **kwargs: Individual parameter overrides (mz_tol, rt_tol, heteroatom_penalty,
                 multiple_formulas_penalty, multiple_compounds_penalty, heteroatoms)

    The resulting DataFrame is stored as study.id_df. Columns:
        - consensus_uid
        - lib_uid
        - mz_delta
        - rt_delta (nullable)
        - score (adduct probability from _get_adducts with penalties applied)
    """
    # Import defaults class
    try:
        from masster.study.defaults.identify_def import identify_defaults
    except ImportError:
        identify_defaults = None

    # Use provided params or create defaults
    if params is None:
        if identify_defaults is not None:
            params = identify_defaults()
        else:
            # Fallback if imports fail
            class FallbackParams:
                mz_tol = 0.01
                rt_tol = 2.0
                heteroatom_penalty = 0.7
                multiple_formulas_penalty = 0.8
                multiple_compounds_penalty = 0.8
                heteroatoms = ["Cl", "Br", "F", "I"]

            params = FallbackParams()

    # Override parameters with any provided kwargs
    if kwargs:
        for param_name, value in kwargs.items():
            if hasattr(params, param_name):
                setattr(params, param_name, value)

    # Get effective tolerances from params (now possibly overridden)
    effective_mz_tol = getattr(params, "mz_tol", 0.01)
    effective_rt_tol = getattr(params, "rt_tol", 2.0)
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    if logger:
        logger.debug(
            f"Starting identification with mz_tolerance={effective_mz_tol}, rt_tolerance={effective_rt_tol}",
        )

    # Determine which features to process
    target_uids = None
    if features is not None:
        if hasattr(features, "columns"):  # DataFrame-like
            if "consensus_uid" in features.columns:
                target_uids = features["consensus_uid"].unique().to_list()
            else:
                raise ValueError(
                    "features DataFrame must contain 'consensus_uid' column",
                )
        elif hasattr(features, "__iter__") and not isinstance(
            features,
            str,
        ):  # List-like
            target_uids = list(features)
        else:
            raise ValueError(
                "features must be a DataFrame with 'consensus_uid' column or a list of UIDs",
            )

        if logger:
            logger.debug(f"Identifying {len(target_uids)} specified features")

    # Clear previous identification results for target features only
    if hasattr(study, "id_df") and not study.id_df.is_empty():
        if target_uids is not None:
            # Keep results for features NOT being re-identified
            study.id_df = study.id_df.filter(
                ~pl.col("consensus_uid").is_in(target_uids),
            )
            if logger:
                logger.debug(
                    f"Cleared previous identification results for {len(target_uids)} features",
                )
        else:
            # Clear all results if no specific features specified
            study.id_df = pl.DataFrame()
            if logger:
                logger.debug("Cleared all previous identification results")
    elif not hasattr(study, "id_df"):
        study.id_df = pl.DataFrame()
        if logger:
            logger.debug("Initialized empty id_df")

    # Validate inputs
    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        if logger:
            logger.warning("No consensus features found for identification")
        return

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        if logger:
            logger.error("Library (study.lib_df) is empty; call lib_load() first")
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    # Filter consensus features if target_uids specified
    consensus_to_process = study.consensus_df
    if target_uids is not None:
        consensus_to_process = study.consensus_df.filter(
            pl.col("consensus_uid").is_in(target_uids),
        )
        if consensus_to_process.is_empty():
            if logger:
                logger.warning(
                    "No consensus features found matching specified features",
                )
            return

    consensus_count = len(consensus_to_process)
    lib_count = len(study.lib_df)

    if logger:
        if target_uids is not None:
            logger.debug(
                f"Identifying {consensus_count} specified consensus features against {lib_count} library entries",
            )
        else:
            logger.debug(
                f"Identifying {consensus_count} consensus features against {lib_count} library entries",
            )

    # Get adduct probabilities
    adducts_df = study._get_adducts()
    adduct_prob_map = {}
    if not adducts_df.is_empty():
        for row in adducts_df.iter_rows(named=True):
            adduct_prob_map[row.get("name")] = row.get("probability", 1.0)

    results = []
    features_with_matches = 0
    total_matches = 0
    rt_filtered_compounds = 0
    multiply_charged_filtered = 0

    # Iterate consensus rows and find matching lib rows by m/z +/- tolerance
    for cons in consensus_to_process.iter_rows(named=True):
        cons_mz = cons.get("mz")
        cons_rt = cons.get("rt")
        cons_uid = cons.get("consensus_uid")

        if cons_mz is None:
            if logger:
                logger.debug(f"Skipping consensus feature {cons_uid} - no m/z value")
            continue

        # Filter lib by mz window
        matches = study.lib_df.filter(
            (pl.col("mz") >= cons_mz - effective_mz_tol)
            & (pl.col("mz") <= cons_mz + effective_mz_tol),
        )

        initial_matches = len(matches)

        # If rt_tol provided and consensus RT present, prefer rt-filtered hits
        if effective_rt_tol is not None and cons_rt is not None:
            rt_matches = matches.filter(
                pl.col("rt").is_not_null()
                & (pl.col("rt") >= cons_rt - effective_rt_tol)
                & (pl.col("rt") <= cons_rt + effective_rt_tol),
            )
            if not rt_matches.is_empty():
                matches = rt_matches
                if logger:
                    logger.debug(
                        f"Consensus {cons_uid}: {initial_matches} m/z matches, {len(matches)} after RT filter",
                    )
            else:
                if logger:
                    logger.debug(
                        f"Consensus {cons_uid}: {initial_matches} m/z matches, 0 after RT filter - using m/z matches only",
                    )

        # Apply scoring-based filtering system
        if not matches.is_empty():
            filtered_matches = matches.clone()
        else:
            filtered_matches = pl.DataFrame()

        if not filtered_matches.is_empty():
            features_with_matches += 1
            feature_match_count = len(filtered_matches)
            total_matches += feature_match_count

            if logger:
                logger.debug(
                    f"Consensus {cons_uid} (mz={cons_mz:.5f}): {feature_match_count} library matches",
                )

        for m in filtered_matches.iter_rows(named=True):
            mz_delta = abs(cons_mz - m.get("mz")) if m.get("mz") is not None else None
            lib_rt = m.get("rt")
            rt_delta = (
                abs(cons_rt - lib_rt)
                if (cons_rt is not None and lib_rt is not None)
                else None
            )

            # Get adduct probability from _get_adducts() results
            adduct = m.get("adduct")
            score = adduct_prob_map.get(adduct, 1.0) if adduct else 1.0

            results.append(
                {
                    "consensus_uid": cons.get("consensus_uid"),
                    "lib_uid": m.get("lib_uid"),
                    "mz_delta": mz_delta,
                    "rt_delta": rt_delta,
                    "matcher": "ms1",
                    "score": score,
                },
            )

    # Merge new results with existing results
    new_results_df = pl.DataFrame(results) if results else pl.DataFrame()

    if not new_results_df.is_empty():
        if hasattr(study, "id_df") and not study.id_df.is_empty():
            # Concatenate new results with existing results
            study.id_df = pl.concat([study.id_df, new_results_df])
        else:
            # First results
            study.id_df = new_results_df

    # Apply scoring adjustments based on compound and formula counts
    if (
        not study.id_df.is_empty()
        and hasattr(study, "lib_df")
        and not study.lib_df.is_empty()
    ):
        # Join with lib_df to get compound and formula information
        id_with_lib = study.id_df.join(
            study.lib_df.select(["lib_uid", "cmpd_uid", "formula"]),
            on="lib_uid",
            how="left",
        )

        # Calculate counts per consensus_uid
        count_stats = id_with_lib.group_by("consensus_uid").agg(
            [
                pl.col("cmpd_uid").n_unique().alias("num_cmpds"),
                pl.col("formula")
                .filter(pl.col("formula").is_not_null())
                .n_unique()
                .alias("num_formulas"),
            ],
        )

        # Join counts back to id_df
        id_with_counts = study.id_df.join(count_stats, on="consensus_uid", how="left")

        # Join with lib_df again to get formula information for heteroatom penalty
        id_with_formula = id_with_counts.join(
            study.lib_df.select(["lib_uid", "formula"]),
            on="lib_uid",
            how="left",
        )

        # Apply scoring penalties
        heteroatoms = getattr(params, "heteroatoms", ["Cl", "Br", "F", "I"])
        heteroatom_penalty = getattr(params, "heteroatom_penalty", 0.7)
        formulas_penalty = getattr(params, "multiple_formulas_penalty", 0.8)
        compounds_penalty = getattr(params, "multiple_compounds_penalty", 0.8)

        # Build heteroatom condition
        heteroatom_condition = None
        for atom in heteroatoms:
            atom_condition = pl.col("formula").str.contains(atom)
            if heteroatom_condition is None:
                heteroatom_condition = atom_condition
            else:
                heteroatom_condition = heteroatom_condition | atom_condition

        # Apply penalties
        study.id_df = (
            id_with_formula.with_columns(
                [
                    # Heteroatom penalty: if formula contains specified heteroatoms, apply penalty
                    pl.when(
                        pl.col("formula").is_not_null() & heteroatom_condition,
                    )
                    .then(pl.col("score") * heteroatom_penalty)
                    .otherwise(pl.col("score"))
                    .alias("score_temp0"),
                ],
            )
            .with_columns(
                [
                    # If num_formulas > 1, apply multiple formulas penalty
                    pl.when(pl.col("num_formulas") > 1)
                    .then(pl.col("score_temp0") * formulas_penalty)
                    .otherwise(pl.col("score_temp0"))
                    .alias("score_temp1"),
                ],
            )
            .with_columns(
                [
                    # If num_cmpds > 1, apply multiple compounds penalty
                    pl.when(pl.col("num_cmpds") > 1)
                    .then(pl.col("score_temp1") * compounds_penalty)
                    .otherwise(pl.col("score_temp1"))
                    .round(4)  # Round to 4 decimal places
                    .alias("score"),
                ],
            )
            .select(
                [
                    "consensus_uid",
                    "lib_uid",
                    "mz_delta",
                    "rt_delta",
                    "matcher",
                    "score",
                ],
            )
        )

    # Store this operation in history
    if hasattr(study, "store_history"):
        history_params = {"mz_tol": effective_mz_tol, "rt_tol": effective_rt_tol}
        if features is not None:
            history_params["features"] = target_uids
        if params is not None and hasattr(params, "to_dict"):
            history_params["params"] = params.to_dict()
        if kwargs:
            history_params["kwargs"] = kwargs
        study.store_history(["identify"], history_params)

    if logger:
        if rt_filtered_compounds > 0:
            logger.debug(
                f"RT consistency filtering applied to {rt_filtered_compounds} compound groups",
            )

        if multiply_charged_filtered > 0:
            logger.debug(
                f"Excluded {multiply_charged_filtered} multiply charged adducts (no [M+H]+ or [M-H]- coeluting)",
            )

        logger.info(
            f"Identification completed: {features_with_matches}/{consensus_count} features matched, {total_matches} total identifications",
        )

        if total_matches > 0:
            # Calculate some statistics
            mz_deltas = [r["mz_delta"] for r in results if r["mz_delta"] is not None]
            rt_deltas = [r["rt_delta"] for r in results if r["rt_delta"] is not None]
            scores = [r["score"] for r in results if r["score"] is not None]

            if mz_deltas:
                avg_mz_delta = sum(mz_deltas) / len(mz_deltas)
                max_mz_delta = max(mz_deltas)
                logger.debug(
                    f"m/z accuracy: average Δ={avg_mz_delta:.5f} Da, max Δ={max_mz_delta:.5f} Da",
                )

            if rt_deltas:
                avg_rt_delta = sum(rt_deltas) / len(rt_deltas)
                max_rt_delta = max(rt_deltas)
                logger.debug(
                    f"RT accuracy: average Δ={avg_rt_delta:.2f} min, max Δ={max_rt_delta:.2f} min",
                )

            if scores:
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                logger.debug(
                    f"Adduct probability scores: average={avg_score:.3f}, min={min_score:.3f}, max={max_score:.3f}",
                )


def get_id(study, features=None) -> pl.DataFrame:
    """Get identification results with comprehensive annotation data.

    Combines identification results (study.id_df) with library information to provide
    comprehensive identification data including names, adducts, formulas, etc.

    Args:
        study: Study instance with id_df and lib_df populated
        features: Optional DataFrame or list of consensus_uids to filter results.
                 If None, returns all identification results.

    Returns:
        Polars DataFrame with columns:
        - consensus_uid
        - lib_uid
        - mz (consensus feature m/z)
        - rt (consensus feature RT)
        - name (compound name from library)
        - formula (molecular formula from library)
        - adduct (adduct type from library)
        - smiles (SMILES notation from library)
        - mz_delta (absolute m/z difference)
        - rt_delta (absolute RT difference, nullable)
        - Additional library columns if available (inchi, inchikey, etc.)

    Raises:
        ValueError: If study.id_df or study.lib_df are empty
    """
    # Validate inputs
    if getattr(study, "id_df", None) is None or study.id_df.is_empty():
        raise ValueError(
            "Identification results (study.id_df) are empty; call identify() first",
        )

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        raise ValueError("Consensus features (study.consensus_df) are empty")

    # Start with identification results
    result_df = study.id_df.clone()

    # Filter by features if provided
    if features is not None:
        if hasattr(features, "columns"):  # DataFrame-like
            if "consensus_uid" in features.columns:
                uids = features["consensus_uid"].unique().to_list()
            else:
                raise ValueError(
                    "features DataFrame must contain 'consensus_uid' column",
                )
        elif hasattr(features, "__iter__") and not isinstance(
            features,
            str,
        ):  # List-like
            uids = list(features)
        else:
            raise ValueError(
                "features must be a DataFrame with 'consensus_uid' column or a list of UIDs",
            )

        result_df = result_df.filter(pl.col("consensus_uid").is_in(uids))

        if result_df.is_empty():
            return pl.DataFrame()

    # Join with consensus_df to get consensus feature m/z and RT
    consensus_cols = ["consensus_uid", "mz", "rt"]
    # Only select columns that exist in consensus_df
    available_consensus_cols = [
        col for col in consensus_cols if col in study.consensus_df.columns
    ]

    result_df = result_df.join(
        study.consensus_df.select(available_consensus_cols),
        on="consensus_uid",
        how="left",
        suffix="_consensus",
    )

    # Join with lib_df to get library information
    lib_cols = [
        "lib_uid",
        "name",
        "formula",
        "adduct",
        "smiles",
        "cmpd_uid",
        "inchikey",
    ]
    # Add optional columns if they exist
    optional_lib_cols = ["inchi", "db_id", "db"]
    for col in optional_lib_cols:
        if col in study.lib_df.columns:
            lib_cols.append(col)

    # Only select columns that exist in lib_df
    available_lib_cols = [col for col in lib_cols if col in study.lib_df.columns]

    result_df = result_df.join(
        study.lib_df.select(available_lib_cols),
        on="lib_uid",
        how="left",
        suffix="_lib",
    )

    # Reorder columns for better readability
    column_order = [
        "consensus_uid",
        "cmpd_uid" if "cmpd_uid" in result_df.columns else None,
        "lib_uid",
        "name" if "name" in result_df.columns else None,
        "formula" if "formula" in result_df.columns else None,
        "adduct" if "adduct" in result_df.columns else None,
        "mz" if "mz" in result_df.columns else None,
        "mz_delta",
        "rt" if "rt" in result_df.columns else None,
        "rt_delta",
        "matcher" if "matcher" in result_df.columns else None,
        "score" if "score" in result_df.columns else None,
        "smiles" if "smiles" in result_df.columns else None,
        "inchikey" if "inchikey" in result_df.columns else None,
    ]

    # Add any remaining columns
    remaining_cols = [col for col in result_df.columns if col not in column_order]
    column_order.extend(remaining_cols)

    # Filter out None values and select existing columns
    final_column_order = [
        col for col in column_order if col is not None and col in result_df.columns
    ]

    result_df = result_df.select(final_column_order)

    # Add compound and formula count columns
    if "consensus_uid" in result_df.columns:
        # Calculate counts per consensus_uid
        count_stats = result_df.group_by("consensus_uid").agg(
            [
                pl.col("cmpd_uid").n_unique().alias("num_cmpds")
                if "cmpd_uid" in result_df.columns
                else pl.lit(None).alias("num_cmpds"),
                pl.col("formula")
                .filter(pl.col("formula").is_not_null())
                .n_unique()
                .alias("num_formulas")
                if "formula" in result_df.columns
                else pl.lit(None).alias("num_formulas"),
            ],
        )

        # Join the counts back to the main dataframe
        result_df = result_df.join(count_stats, on="consensus_uid", how="left")

        # Reorder columns to put count columns in the right position
        final_columns = []
        for col in result_df.columns:
            if col in [
                "consensus_uid",
                "cmpd_uid",
                "lib_uid",
                "name",
                "formula",
                "adduct",
                "mz",
                "mz_delta",
                "rt",
                "rt_delta",
                "matcher",
                "score",
            ]:
                final_columns.append(col)
        # Add count columns
        if "num_cmpds" in result_df.columns:
            final_columns.append("num_cmpds")
        if "num_formulas" in result_df.columns:
            final_columns.append("num_formulas")
        # Add remaining columns
        for col in result_df.columns:
            if col not in final_columns:
                final_columns.append(col)

        result_df = result_df.select(final_columns)

        # Apply filtering logic (scores are already final from identify())
        if "consensus_uid" in result_df.columns and len(result_df) > 0:
            # (v) Rank by score, assume that highest score has the correct rt
            # (vi) Remove all lower-scoring ids with a different rt (group by cmpd_uid)
            # (vii) Remove multiply charged ids if not in line with [M+H]+ or [M-H]- (group by cmpd_uid)

            # Group by cmpd_uid and apply filtering logic
            if "cmpd_uid" in result_df.columns:
                filtered_dfs = []
                for cmpd_uid, group_df in result_df.group_by("cmpd_uid"):
                    # Sort by score descending to get highest score first
                    group_df = group_df.sort("score", descending=True)

                    if len(group_df) == 0:
                        continue

                    # Get the highest scoring entry's RT as reference
                    reference_rt = (
                        group_df["rt"][0]
                        if "rt" in group_df.columns and group_df["rt"][0] is not None
                        else None
                    )

                    # Filter entries: keep those with same RT as highest scoring entry
                    if reference_rt is not None and "rt" in group_df.columns:
                        # Keep entries with the same RT or null RT
                        rt_filtered = group_df.filter(
                            (pl.col("rt") == reference_rt) | pl.col("rt").is_null(),
                        )
                    else:
                        # No reference RT, keep all
                        rt_filtered = group_df

                    # Check multiply charged constraint
                    if (
                        "z" in rt_filtered.columns
                        and "adduct" in rt_filtered.columns
                        and len(rt_filtered) > 0
                    ):
                        # Check if there are multiply charged adducts
                        multiply_charged = rt_filtered.filter(
                            (pl.col("z") > 1) | (pl.col("z") < -1),
                        )
                        singly_charged = rt_filtered.filter(
                            (pl.col("z") == 1) | (pl.col("z") == -1),
                        )

                        if not multiply_charged.is_empty():
                            # Check if [M+H]+ or [M-H]- are present
                            reference_adducts = ["[M+H]+", "[M-H]-"]
                            has_reference = any(
                                singly_charged.filter(
                                    pl.col("adduct").is_in(reference_adducts),
                                ).height
                                > 0,
                            )

                            if not has_reference:
                                # Remove multiply charged adducts
                                rt_filtered = singly_charged

                    if len(rt_filtered) > 0:
                        filtered_dfs.append(rt_filtered)

                if filtered_dfs:
                    result_df = pl.concat(filtered_dfs)
                else:
                    result_df = pl.DataFrame()

    # Sort by cmpd_uid if available
    if "cmpd_uid" in result_df.columns:
        result_df = result_df.sort("cmpd_uid")

    return result_df


def id_reset(study):
    """Reset identification data and remove from history.

    Removes:
    - study.id_df (identification results DataFrame)
    - 'identify' from study.history

    Args:
        study: Study instance to reset
    """
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    # Remove id_df
    if hasattr(study, "id_df"):
        if logger:
            logger.debug("Removing id_df")
        delattr(study, "id_df")

    # Remove identify from history
    if hasattr(study, "history") and "identify" in study.history:
        if logger:
            logger.debug("Removing 'identify' from history")
        del study.history["identify"]

    if logger:
        logger.info("Identification data reset completed")


def lib_reset(study):
    """Reset library and identification data and remove from history.

    Removes:
    - study.id_df (identification results DataFrame)
    - study.lib_df (library DataFrame)
    - study._lib (library object reference)
    - 'identify' from study.history
    - 'lib_load' from study.history (if exists)

    Args:
        study: Study instance to reset
    """
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    # Remove id_df
    if hasattr(study, "id_df"):
        if logger:
            logger.debug("Removing id_df")
        delattr(study, "id_df")

    # Remove lib_df
    if hasattr(study, "lib_df"):
        if logger:
            logger.debug("Removing lib_df")
        delattr(study, "lib_df")

    # Remove lib object reference
    if hasattr(study, "_lib"):
        if logger:
            logger.debug("Removing _lib reference")
        delattr(study, "_lib")

    # Remove from history
    if hasattr(study, "history"):
        if "identify" in study.history:
            if logger:
                logger.debug("Removing 'identify' from history")
            del study.history["identify"]

        if "lib_load" in study.history:
            if logger:
                logger.debug("Removing 'lib_load' from history")
            del study.history["lib_load"]

    if logger:
        logger.info("Library and identification data reset completed")


def _get_adducts(self, adducts_list: list = None, **kwargs):
    """
    Generate comprehensive adduct specifications for study-level adduct filtering.

    This method creates a DataFrame of adduct combinations that will be used to filter
    and score adducts at the study level. Similar to sample._get_adducts() but uses
    study-level parameters and constraints.

    Parameters
    ----------
    adducts_list : List[str], optional
        List of base adduct specifications in format "+H:1:0.6" or "-H:-1:0.8"
        If None, uses self.parameters.adducts
    **kwargs : dict
        Override parameters, including:
        - charge_min: Minimum charge to consider (default 1)
        - charge_max: Maximum charge to consider (default 3)
        - max_combinations: Maximum number of adduct components to combine (default 3)
        - min_probability: Minimum probability threshold (default from study parameters)

    Returns
    -------
    pl.DataFrame
        DataFrame with columns:
        - name: Formatted adduct name like "[M+H]1+" or "[M+2H]2+"
        - charge: Total charge of the adduct
        - mass_shift: Total mass shift in Da
        - probability: Combined probability score
        - complexity: Number of adduct components (1-3)
    """
    # Import required modules

    # Use provided adducts list or get from study parameters
    if adducts_list is None:
        adducts_list = (
            self.parameters.adducts
            if hasattr(self.parameters, "adducts") and self.parameters.adducts
            else []
        )

    # Get parameters with study-specific defaults
    charge_min = kwargs.get("charge_min", -3)  # Allow negative charges
    charge_max = kwargs.get("charge_max", 3)  # Study uses up to charge ±3
    max_combinations = kwargs.get("max_combinations", 3)  # Up to 3 combinations
    min_probability = kwargs.get(
        "min_probability",
        getattr(self.parameters, "adduct_min_probability", 0.04),
    )

    # Parse base adduct specifications
    base_specs = []

    for adduct_str in adducts_list:
        if not isinstance(adduct_str, str) or ":" not in adduct_str:
            continue

        try:
            parts = adduct_str.split(":")
            if len(parts) != 3:
                continue

            formula_part = parts[0]
            charge = int(parts[1])
            probability = float(parts[2])

            # Calculate mass shift from formula
            mass_shift = self._calculate_formula_mass_shift(formula_part)

            base_specs.append(
                {
                    "formula": formula_part,
                    "charge": charge,
                    "mass_shift": mass_shift,
                    "probability": probability,
                    "raw_string": adduct_str,
                },
            )

        except (ValueError, IndexError):
            continue

    if not base_specs:
        # Return empty DataFrame with correct schema
        return pl.DataFrame(
            {
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
            },
        )

    # Generate all valid combinations
    combinations_list = []

    # Separate specs by charge type
    positive_specs = [spec for spec in base_specs if spec["charge"] > 0]
    negative_specs = [spec for spec in base_specs if spec["charge"] < 0]
    neutral_specs = [spec for spec in base_specs if spec["charge"] == 0]

    # 1. Single adducts (filter out neutral adducts with charge == 0)
    for spec in base_specs:
        if charge_min <= spec["charge"] <= charge_max and spec["charge"] != 0:
            formatted_name = self._format_adduct_name([spec])
            combinations_list.append(
                {
                    "components": [spec],
                    "formatted_name": formatted_name,
                    "total_mass_shift": spec["mass_shift"],
                    "total_charge": spec["charge"],
                    "combined_probability": spec["probability"],
                    "complexity": 1,
                },
            )

    # 2. Generate multiply charged versions (2H+, 3H+, etc.) - already excludes charge==0
    for spec in positive_specs + negative_specs:
        base_charge = spec["charge"]
        for multiplier in range(2, min(max_combinations + 1, 4)):  # Up to 3x multiplier
            total_charge = base_charge * multiplier
            if charge_min <= total_charge <= charge_max and total_charge != 0:
                components = [spec] * multiplier
                formatted_name = self._format_adduct_name(components)

                combinations_list.append(
                    {
                        "components": components,
                        "formatted_name": formatted_name,
                        "total_mass_shift": spec["mass_shift"] * multiplier,
                        "total_charge": total_charge,
                        "combined_probability": spec["probability"] ** multiplier,
                        "complexity": multiplier,
                    },
                )

    # 3. Mixed combinations (2-component) - limited for study level, filter out charge==0
    if max_combinations >= 2:
        # Positive + Neutral (1 neutral loss only) - but exclude if total charge == 0
        for pos_spec in positive_specs[:2]:  # Limit to first 2 positive specs
            for neut_spec in neutral_specs[:1]:  # Only 1 neutral loss
                total_charge = pos_spec["charge"] + neut_spec["charge"]
                if charge_min <= total_charge <= charge_max and total_charge != 0:
                    components = [pos_spec, neut_spec]
                    formatted_name = self._format_adduct_name(components)
                    combinations_list.append(
                        {
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": pos_spec["mass_shift"]
                            + neut_spec["mass_shift"],
                            "total_charge": total_charge,
                            "combined_probability": pos_spec["probability"]
                            * neut_spec["probability"],
                            "complexity": 2,
                        },
                    )

    # Convert to polars DataFrame
    if combinations_list:
        combinations_list.sort(
            key=lambda x: (-x["combined_probability"], x["complexity"]),
        )

        adducts_df = pl.DataFrame(
            [
                {
                    "name": combo["formatted_name"],
                    "charge": combo["total_charge"],
                    "mass_shift": combo["total_mass_shift"],
                    "probability": combo["combined_probability"],
                    "complexity": combo["complexity"],
                }
                for combo in combinations_list
            ],
        )

        # Filter by minimum probability threshold
        if min_probability > 0.0:
            adducts_before_filter = len(adducts_df)
            adducts_df = adducts_df.filter(pl.col("probability") >= min_probability)
            adducts_after_filter = len(adducts_df)

            self.logger.debug(
                f"Study adducts: generated {adducts_before_filter}, filtered to {adducts_after_filter} (min_prob={min_probability})",
            )

    else:
        # Return empty DataFrame with correct schema
        adducts_df = pl.DataFrame(
            {
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
            },
        )

    return adducts_df


def _calculate_formula_mass_shift(self, formula: str) -> float:
    """Calculate mass shift from formula string like "+H", "-H2O", "+Na-H", etc."""
    # Standard atomic masses
    atomic_masses = {
        "H": 1.007825,
        "C": 12.0,
        "N": 14.003074,
        "O": 15.994915,
        "Na": 22.989769,
        "K": 38.963707,
        "Li": 7.016003,
        "Ca": 39.962591,
        "Mg": 23.985042,
        "Fe": 55.934938,
        "Cl": 34.968853,
        "Br": 78.918336,
        "I": 126.904473,
        "P": 30.973762,
        "S": 31.972071,
    }

    total_mass = 0.0

    # Parse formula by splitting on + and - while preserving the operators
    parts = []
    current_part = ""
    current_sign = 1

    for char in formula:
        if char == "+":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = 1
        elif char == "-":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = -1
        else:
            current_part += char

    if current_part:
        parts.append((current_sign, current_part))

    # Process each part
    for sign, part in parts:
        if not part:
            continue

        # Parse element and count (e.g., "H2O" -> H:2, O:1)
        elements = self._parse_element_counts(part)

        for element, count in elements.items():
            if element in atomic_masses:
                total_mass += sign * atomic_masses[element] * count

    return total_mass


def _parse_element_counts(self, formula_part: str) -> dict[str, int]:
    """Parse element counts from a formula part like 'H2O' -> {'H': 2, 'O': 1}"""
    elements = {}
    i = 0

    while i < len(formula_part):
        # Get element (uppercase letter, possibly followed by lowercase)
        element = formula_part[i]
        i += 1

        while i < len(formula_part) and formula_part[i].islower():
            element += formula_part[i]
            i += 1

        # Get count (digits following element)
        count_str = ""
        while i < len(formula_part) and formula_part[i].isdigit():
            count_str += formula_part[i]
            i += 1

        count = int(count_str) if count_str else 1
        elements[element] = elements.get(element, 0) + count

    return elements


def _format_adduct_name(self, components: list[dict]) -> str:
    """Format adduct name from components like [M+H]1+ or [M+2H]2+"""
    if not components:
        return "[M]"

    # Count occurrences of each formula
    from collections import Counter

    formula_counts = Counter(comp["formula"] for comp in components)
    total_charge = sum(comp["charge"] for comp in components)

    # Build formula part with proper multipliers
    formula_parts = []
    for formula, count in sorted(
        formula_counts.items(),
    ):  # Sort for consistent ordering
        if count == 1:
            formula_parts.append(formula)
        else:
            # For multiple occurrences, use count prefix (e.g., 2H, 3Na)
            # Handle special case where formula might already start with + or -
            if formula.startswith(("+", "-")):
                sign = formula[0]
                base_formula = formula[1:]
                formula_parts.append(f"{sign}{count}{base_formula}")
            else:
                formula_parts.append(f"{count}{formula}")

    # Combine formula parts
    formula = "".join(formula_parts)

    # Format charge
    if total_charge == 0:
        charge_str = ""
    elif abs(total_charge) == 1:
        charge_str = "1+" if total_charge > 0 else "1-"
    else:
        charge_str = (
            f"{abs(total_charge)}+" if total_charge > 0 else f"{abs(total_charge)}-"
        )

    return f"[M{formula}]{charge_str}"
