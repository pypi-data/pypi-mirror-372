"""
Wizard module for automated processing of mass spectrometry studies.

This module provides the Wizard class for fully automated processing of MS data
from raw files to final study results, including batch conversion, assembly,
alignment, merging, plotting, and export.

Key Features:
- Automated discovery and batch conversion of raw data files
- Intelligent resume capability for interrupted processes
- Parallel processing optimization for large datasets
- Adaptive study format based on study size
- Comprehensive logging and progress tracking
- Optimized memory management for large studies

Classes:
- Wizard: Main class for automated study processing
- wizard_def: Default parameters configuration class

Example Usage:
```python
from masster import Wizard, wizard_def

# Create wizard with default parameters
wizard = Wizard(
    data_source="./raw_data",
    study_folder="./processed_study",
    polarity="positive",
    num_cores=4
)

# Run complete processing pipeline
wizard.run_full_pipeline()

# Or run individual steps
wizard.convert_to_sample5()
wizard.assemble_study()
wizard.align_and_merge()
wizard.generate_plots()
wizard.export_results()
```
"""

from __future__ import annotations

import os
import time
import multiprocessing
from pathlib import Path
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
import concurrent.futures
from datetime import datetime

# Import masster modules - use delayed import to avoid circular dependencies
from masster.logger import MassterLogger
from masster.study.defaults.study_def import study_defaults
from masster.study.defaults.align_def import align_defaults
from masster.study.defaults.merge_def import merge_defaults


@dataclass
class wizard_def:
    """
    Default parameters for the Wizard automated processing system.
    
    This class provides comprehensive configuration for all stages of automated
    mass spectrometry data processing from raw files to final results.
    
    Attributes:
        # Core Configuration
        data_source (str): Path to directory containing raw data files
        study_folder (str): Output directory for processed study
        polarity (str): Ion polarity mode ("positive" or "negative")
        num_cores (int): Number of CPU cores to use for parallel processing
        
        # File Discovery
        file_extensions (List[str]): File extensions to search for
        search_subfolders (bool): Whether to search subdirectories
        skip_patterns (List[str]): Filename patterns to skip
        
        # Processing Parameters
        adducts (List[str]): Adduct specifications for given polarity
        batch_size (int): Number of files to process per batch
        memory_limit_gb (float): Memory limit for processing (GB)
        
        # Resume & Recovery
        resume_enabled (bool): Enable automatic resume capability
        force_reprocess (bool): Force reprocessing of existing files
        backup_enabled (bool): Create backups of intermediate results
        
        # Output & Export
        generate_plots (bool): Generate visualization plots
        export_formats (List[str]): Output formats to generate
        compress_output (bool): Compress final study file
        
        # Logging
        log_level (str): Logging detail level
        log_to_file (bool): Save logs to file
        progress_interval (int): Progress update interval (seconds)
    """
    
    # === Core Configuration ===
    data_source: str = ""
    study_folder: str = ""  
    polarity: str = "positive"
    num_cores: int = 4
    
    # === File Discovery ===
    file_extensions: List[str] = field(default_factory=lambda: [".wiff", ".raw", ".mzML", ".d"])
    search_subfolders: bool = True
    skip_patterns: List[str] = field(default_factory=lambda: ["blank", "QC", "test"])
    
    # === Processing Parameters ===
    adducts: List[str] = field(default_factory=list)  # Will be set based on polarity
    batch_size: int = 8
    memory_limit_gb: float = 16.0
    max_file_size_gb: float = 4.0
    
    # === Resume & Recovery ===
    resume_enabled: bool = True
    force_reprocess: bool = False
    backup_enabled: bool = True
    checkpoint_interval: int = 10  # Save progress every N files
    
    # === Study Assembly ===
    min_samples_for_merge: int = 50
    rt_tolerance: float = 1.5
    mz_tolerance: float = 0.01
    alignment_algorithm: str = "kd"
    merge_method: str = "chunked"
    
    # === Feature Detection ===
    chrom_fwhm: float = 0.2
    noise_threshold: float = 1e5
    chrom_peak_snr: float = 5.0
    tol_ppm: float = 10.0
    
    # === Output & Export ===
    generate_plots: bool = True
    generate_interactive: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "mgf", "xlsx"])
    compress_output: bool = True
    adaptive_compression: bool = True  # Adapt based on study size
    
    # === Logging ===
    log_level: str = "INFO"
    log_to_file: bool = True
    progress_interval: int = 30  # seconds
    verbose_progress: bool = True
    
    # === Advanced Options ===
    use_process_pool: bool = True  # vs ThreadPoolExecutor
    optimize_memory: bool = True
    cleanup_temp_files: bool = True
    validate_outputs: bool = True
    
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "data_source": {
                "dtype": str,
                "description": "Path to directory containing raw data files",
                "required": True,
            },
            "study_folder": {
                "dtype": str, 
                "description": "Output directory for processed study",
                "required": True,
            },
            "polarity": {
                "dtype": str,
                "description": "Ion polarity mode",
                "default": "positive",
                "allowed_values": ["positive", "negative", "pos", "neg"],
            },
            "num_cores": {
                "dtype": int,
                "description": "Number of CPU cores to use",
                "default": 4,
                "min_value": 1,
                "max_value": multiprocessing.cpu_count(),
            },
            "batch_size": {
                "dtype": int,
                "description": "Number of files to process per batch",
                "default": 8,
                "min_value": 1,
                "max_value": 32,
            },
            "memory_limit_gb": {
                "dtype": float,
                "description": "Memory limit for processing (GB)",
                "default": 16.0,
                "min_value": 1.0,
                "max_value": 128.0,
            },
        },
        repr=False,
    )
    
    def __post_init__(self):
        """Set polarity-specific defaults after initialization."""
        # Set default adducts based on polarity if not provided
        if not self.adducts:
            if self.polarity.lower() in ["positive", "pos"]:
                self.adducts = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]
            elif self.polarity.lower() in ["negative", "neg"]: 
                self.adducts = ["H-1:-:1.0", "CH2O2:0:0.5"]
            else:
                # Default to positive
                self.adducts = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]
        
        # Validate num_cores
        max_cores = multiprocessing.cpu_count()
        if self.num_cores <= 0:
            self.num_cores = max_cores
        elif self.num_cores > max_cores:
            self.num_cores = max_cores
            
        # Ensure paths are absolute
        if self.data_source:
            self.data_source = os.path.abspath(self.data_source)
        if self.study_folder:
            self.study_folder = os.path.abspath(self.study_folder)


class Wizard:
    """
    Automated processing wizard for mass spectrometry studies.
    
    The Wizard class provides end-to-end automation for processing collections
    of mass spectrometry files from raw data to final study results, including:
    
    1. Raw data discovery and batch conversion to sample5 format
    2. Study assembly with feature alignment and merging 
    3. Automated plot generation and result export
    4. Intelligent resume capability for interrupted processes
    5. Adaptive optimization based on study size and system resources
    
    The wizard handles the complete workflow with minimal user intervention
    while providing comprehensive logging and progress tracking.
    """
    
    def __init__(
        self,
        data_source: str = "",
        study_folder: str = "",  
        polarity: str = "positive",
        adducts: Optional[List[str]] = None,
        num_cores: int = 4,
        **kwargs
    ):
        """
        Initialize the Wizard for automated study processing.
        
        Parameters:
            data_source: Directory containing raw data files
            study_folder: Output directory for processed study
            polarity: Ion polarity mode ("positive" or "negative")
            adducts: List of adduct specifications (auto-set if None)
            num_cores: Number of CPU cores for parallel processing
            **kwargs: Additional parameters (see wizard_def for full list)
        """
        
        # Create parameters instance
        if "params" in kwargs and isinstance(kwargs["params"], wizard_def):
            self.params = kwargs.pop("params")
        else:
            # Create default parameters and update with provided values
            self.params = wizard_def(
                data_source=data_source,
                study_folder=study_folder,
                polarity=polarity,
                num_cores=num_cores
            )
            
            if adducts is not None:
                self.params.adducts = adducts
            
            # Update with any additional parameters
            for key, value in kwargs.items():
                if hasattr(self.params, key):
                    setattr(self.params, key, value)
        
        # Validate required parameters
        if not self.params.data_source:
            raise ValueError("data_source is required")
        if not self.params.study_folder:
            raise ValueError("study_folder is required")
        
        # Create directories
        self.data_source_path = Path(self.params.data_source)
        self.study_folder_path = Path(self.params.study_folder) 
        self.study_folder_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize state tracking
        self.processed_files = []
        self.failed_files = []
        self.study = None
        self.start_time = None
        self.current_step = "initialized"
        
        # Create checkpoint file path
        self.checkpoint_file = self.study_folder_path / "wizard_checkpoint.json"
        
        self.logger.info(f"Wizard initialized for {self.polarity} mode")
        self.logger.info(f"Data source: {self.data_source_path}")
        self.logger.info(f"Study folder: {self.study_folder_path}")
        self.logger.info(f"Using {self.params.num_cores} CPU cores")
        
        # Load checkpoint if resuming
        if self.params.resume_enabled:
            self._load_checkpoint()
    
    @property
    def polarity(self) -> str:
        """Get the polarity setting."""
        return self.params.polarity
    
    @property 
    def adducts(self) -> List[str]:
        """Get the adducts list."""
        return self.params.adducts
        
    def _setup_logging(self):
        """Setup comprehensive logging system."""
        # Create logger
        log_label = f"Wizard-{self.polarity}"
        
        if self.params.log_to_file:
            log_file = self.study_folder_path / "wizard.log"
            sink = str(log_file)
        else:
            sink = "sys.stdout"
            
        self.logger = MassterLogger(
            instance_type="wizard",
            level=self.params.log_level.upper(),
            label=log_label,
            sink=sink,
        )
        
        # Also create a simple file logger for critical info
        self.log_file = self.study_folder_path / "processing.log"
        
    def _log_progress(self, message: str, level: str = "INFO"):
        """Log progress message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        # Log to masster logger
        getattr(self.logger, level.lower())(message)
        
        # Also write to simple log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{full_message}\n")
            
        if self.params.verbose_progress and level in ["INFO", "WARNING", "ERROR"]:
            print(full_message)
    
    def _save_checkpoint(self):
        """Save processing checkpoint for resume capability."""
        if not self.params.resume_enabled:
            return
            
        import json
        checkpoint_data = {
            "timestamp": datetime.now().isoformat(),
            "current_step": self.current_step,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "params": {
                "data_source": self.params.data_source,
                "study_folder": self.params.study_folder,
                "polarity": self.params.polarity,
                "adducts": self.params.adducts,
                "num_cores": self.params.num_cores,
            }
        }
        
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)
            self.logger.debug(f"Checkpoint saved: {len(self.processed_files)} files processed")
        except Exception as e:
            self.logger.warning(f"Failed to save checkpoint: {e}")
    
    def _load_checkpoint(self):
        """Load processing checkpoint for resume capability."""
        if not self.checkpoint_file.exists():
            return
            
        import json
        try:
            with open(self.checkpoint_file, "r") as f:
                checkpoint_data = json.load(f)
            
            self.processed_files = checkpoint_data.get("processed_files", [])
            self.failed_files = checkpoint_data.get("failed_files", [])
            self.current_step = checkpoint_data.get("current_step", "initialized")
            
            self.logger.info(f"Resuming from checkpoint: {len(self.processed_files)} files already processed")
            self.logger.info(f"Previous step: {self.current_step}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load checkpoint: {e}")
            self.processed_files = []
            self.failed_files = []
    
    def discover_files(self) -> List[Path]:
        """
        Discover raw data files in the source directory.
        
        Returns:
            List of file paths found for processing
        """
        self._log_progress("Discovering raw data files...")
        self.current_step = "discovering_files"
        
        found_files = []
        
        for extension in self.params.file_extensions:
            if self.params.search_subfolders:
                pattern = f"**/*{extension}"
                files = list(self.data_source_path.rglob(pattern))
            else:
                pattern = f"*{extension}"
                files = list(self.data_source_path.glob(pattern))
            
            # Filter out files matching skip patterns
            filtered_files = []
            for file_path in files:
                skip_file = False
                for pattern in self.params.skip_patterns:
                    if pattern.lower() in file_path.name.lower():
                        skip_file = True
                        self.logger.debug(f"Skipping file (matches pattern '{pattern}'): {file_path.name}")
                        break
                
                if not skip_file:
                    # Check file size
                    try:
                        file_size_gb = file_path.stat().st_size / (1024**3)
                        if file_size_gb > self.params.max_file_size_gb:
                            self.logger.warning(f"Large file ({file_size_gb:.1f}GB): {file_path.name}")
                        filtered_files.append(file_path)
                    except Exception as e:
                        self.logger.warning(f"Could not check file size for {file_path}: {e}")
                        filtered_files.append(file_path)
            
            found_files.extend(filtered_files)
            self.logger.info(f"Found {len(filtered_files)} {extension} files")
        
        # Remove duplicates and sort
        found_files = sorted(list(set(found_files)))
        
        self._log_progress(f"Total files discovered: {len(found_files)}")
        
        return found_files
    
    def _process_single_file(self, file_path: Path, reset: bool = False) -> Optional[str]:
        """
        Process a single file to sample5 format.
        
        This method replicates the core processing from parallel_sample_processing.py
        but with wizard-specific configuration and error handling.
        
        Parameters:
            file_path: Path to the raw data file
            reset: Force reprocessing even if output exists
        
        Returns:
            Base filename of output on success, None on failure
        """
        import gc
        
        # Generate output filename
        file_out = file_path.stem + '.sample5'
        output_file = self.study_folder_path / file_out
        
        # Initialize masster Sample with delayed import
        import masster
        sample = masster.Sample(
            log_label=file_path.name,
            log_level='ERROR'  # Reduce logging overhead in parallel processing
        )
        
        # Check if file should be skipped
        skip = False
        if not reset and not self.params.force_reprocess and output_file.exists():
            try:
                # Attempt to load existing processed file to verify it's valid
                sample.load(str(output_file))
                skip = True
            except Exception:
                # If loading fails, file needs to be reprocessed
                skip = False
        
        if skip:
            self.logger.debug(f"Skipping {file_path.name} (already processed)")
            return output_file.stem
        
        self.logger.info(f"Processing {file_path.name}")
        
        try:
            # STEP 1: Load raw data
            sample.load(str(file_path))
            
            # STEP 2: Feature detection - First pass (strict parameters)
            sample.find_features(
                chrom_fwhm=self.params.chrom_fwhm,
                noise=self.params.noise_threshold,
                tol_ppm=self.params.tol_ppm,
                chrom_peak_snr=self.params.chrom_peak_snr,
                min_trace_length_multiplier=0.5,
                chrom_fwhm_min=self.params.chrom_fwhm
            )
            
            # STEP 3: Feature detection - Second pass (relaxed parameters)
            sample.find_features(
                chrom_peak_snr=self.params.chrom_peak_snr,
                noise=self.params.noise_threshold / 10,  # Lower noise threshold
                chrom_fwhm=2.0  # Wider peaks
            )
            
            # STEP 4: Adduct detection
            sample.find_adducts(adducts=self.adducts)
            
            # STEP 5: MS2 spectrum identification
            sample.find_ms2()
            
            # STEP 6: Save processed data
            sample.save(filename=str(output_file))
            
            # STEP 7: Generate additional outputs if requested
            if "csv" in self.params.export_formats:
                csv_file = output_file.with_suffix('.features.csv')
                sample.export_features(filename=str(csv_file))
            
            if "mgf" in self.params.export_formats:
                mgf_file = output_file.with_suffix('.mgf')
                sample.export_mgf(filename=str(mgf_file), use_cache=False)
            
            if self.params.generate_plots:
                plot_file = output_file.with_suffix('_2d.html')
                sample.plot_2d(filename=str(plot_file), markersize=4)
            
            # Memory cleanup
            result = output_file.stem
            del sample
            gc.collect()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {e}")
            # Cleanup on error
            gc.collect()
            return None
    
    def _process_batch(self, file_batch: List[Path]) -> List[str]:
        """Process a batch of files in a single worker."""
        results = []
        for file_path in file_batch:
            result = self._process_single_file(file_path)
            if result:
                results.append(result)
            else:
                results.append(None)
        return results
    
    def convert_to_sample5(self, file_list: Optional[List[Path]] = None) -> bool:
        """
        Convert raw data files to sample5 format in parallel.
        
        Parameters:
            file_list: List of files to process (None to discover automatically)
        
        Returns:
            True if conversion completed successfully
        """
        self._log_progress("=== Starting Sample5 Conversion ===")
        self.current_step = "converting_to_sample5"
        
        if file_list is None:
            file_list = self.discover_files()
        
        if not file_list:
            self.logger.warning("No files found for conversion")
            return False
        
        # Filter out already processed files if resuming
        if self.params.resume_enabled and self.processed_files:
            remaining_files = []
            for file_path in file_list:
                if str(file_path) not in self.processed_files:
                    remaining_files.append(file_path)
            file_list = remaining_files
            
            if not file_list:
                self._log_progress("All files already processed")
                return True
        
        self._log_progress(f"Converting {len(file_list)} files to sample5 format")
        
        conversion_start = time.time()
        successful_count = 0
        failed_count = 0
        
        if self.params.use_process_pool:
            # ProcessPoolExecutor approach - better for CPU-intensive work
            if len(file_list) <= self.params.batch_size:
                # Few files: process individually
                self.logger.info(f"Processing {len(file_list)} files individually with {self.params.num_cores} workers")
                
                with concurrent.futures.ProcessPoolExecutor(max_workers=self.params.num_cores) as executor:
                    futures = [
                        executor.submit(self._process_single_file, file_path)
                        for file_path in file_list
                    ]
                    
                    for i, future in enumerate(concurrent.futures.as_completed(futures)):
                        result = future.result()
                        if result:
                            successful_count += 1
                            self.processed_files.append(str(file_list[i]))
                        else:
                            failed_count += 1
                            self.failed_files.append(str(file_list[i]))
                        
                        # Progress update and checkpoint
                        if (successful_count + failed_count) % self.params.checkpoint_interval == 0:
                            progress = (successful_count + failed_count) / len(file_list) * 100
                            self._log_progress(f"Progress: {progress:.1f}% ({successful_count} successful, {failed_count} failed)")
                            self._save_checkpoint()
            
            else:
                # Many files: process in batches
                batches = [
                    file_list[i:i + self.params.batch_size]
                    for i in range(0, len(file_list), self.params.batch_size)
                ]
                
                self.logger.info(f"Processing {len(file_list)} files in {len(batches)} batches")
                
                with concurrent.futures.ProcessPoolExecutor(max_workers=self.params.num_cores) as executor:
                    futures = [executor.submit(self._process_batch, batch) for batch in batches]
                    
                    for batch_idx, future in enumerate(concurrent.futures.as_completed(futures)):
                        batch_results = future.result()
                        batch = batches[batch_idx]
                        
                        for i, result in enumerate(batch_results):
                            if result:
                                successful_count += 1
                                self.processed_files.append(str(batch[i]))
                            else:
                                failed_count += 1
                                self.failed_files.append(str(batch[i]))
                        
                        # Progress update
                        progress = (successful_count + failed_count) / len(file_list) * 100
                        self._log_progress(f"Batch {batch_idx + 1}/{len(batches)} complete. Progress: {progress:.1f}%")
                        self._save_checkpoint()
        
        else:
            # ThreadPoolExecutor approach
            self.logger.info(f"Processing {len(file_list)} files with {self.params.num_cores} threads")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.params.num_cores) as executor:
                futures = [
                    executor.submit(self._process_single_file, file_path)
                    for file_path in file_list
                ]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    result = future.result()
                    if result:
                        successful_count += 1
                        self.processed_files.append(str(file_list[i]))
                    else:
                        failed_count += 1
                        self.failed_files.append(str(file_list[i]))
                    
                    if (successful_count + failed_count) % self.params.checkpoint_interval == 0:
                        progress = (successful_count + failed_count) / len(file_list) * 100
                        self._log_progress(f"Progress: {progress:.1f}%")
                        self._save_checkpoint()
        
        conversion_time = time.time() - conversion_start
        
        self._log_progress("=== Sample5 Conversion Complete ===")
        self._log_progress(f"Successful: {successful_count}")
        self._log_progress(f"Failed: {failed_count}")
        self._log_progress(f"Total time: {conversion_time:.1f} seconds")
        
        if failed_count > 0:
            self.logger.warning(f"{failed_count} files failed to process")
            for failed_file in self.failed_files[-failed_count:]:
                self.logger.warning(f"Failed: {failed_file}")
        
        self._save_checkpoint()
        return successful_count > 0
    
    def assemble_study(self) -> bool:
        """
        Assemble processed sample5 files into a study.
        
        Returns:
            True if study assembly was successful
        """
        self._log_progress("=== Starting Study Assembly ===")
        self.current_step = "assembling_study"
        
        # Find all sample5 files
        sample5_files = list(self.study_folder_path.glob("*.sample5"))
        
        if not sample5_files:
            self.logger.error("No sample5 files found for study assembly")
            return False
        
        self._log_progress(f"Assembling study from {len(sample5_files)} sample5 files")
        
        try:
            # Create study with optimized settings
            import masster
            study_params = study_defaults(
                folder=str(self.study_folder_path),
                polarity=self.polarity,
                log_level="INFO",
                log_label=f"Study-{self.polarity}",
                adducts=self.adducts
            )
            
            self.study = masster.Study(params=study_params)
            
            # Add all sample5 files
            sample5_pattern = str(self.study_folder_path / "*.sample5")
            self.study.add(sample5_pattern)
            
            self._log_progress(f"Added {len(self.study.samples_df)} samples to study")
            
            # Filter features based on quality criteria
            if hasattr(self.study, 'features_filter'):
                initial_features = len(self.study.features_df) if hasattr(self.study, 'features_df') else 0
                
                # Apply feature filtering
                feature_selection = self.study.features_select(
                    chrom_coherence=0.3,
                    chrom_prominence_scaled=1
                )
                self.study.features_filter(feature_selection)
                
                final_features = len(self.study.features_df) if hasattr(self.study, 'features_df') else 0
                self._log_progress(f"Feature filtering: {initial_features} -> {final_features} features")
            
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assemble study: {e}")
            return False
    
    def align_and_merge(self) -> bool:
        """
        Perform feature alignment and merging.
        
        Returns:
            True if alignment and merging were successful
        """
        self._log_progress("=== Starting Feature Alignment and Merging ===")
        self.current_step = "aligning_and_merging"
        
        if self.study is None:
            self.logger.error("Study not assembled. Run assemble_study() first.")
            return False
        
        try:
            # Align features across samples
            align_params = align_defaults(
                rt_tol=self.params.rt_tolerance,
                mz_tol=self.params.mz_tolerance,
                algorithm=self.params.alignment_algorithm
            )
            
            self.logger.info(f"Aligning features with RT tolerance {self.params.rt_tolerance}s, m/z tolerance {self.params.mz_tolerance} Da")
            self.study.align(params=align_params)
            
            # Merge aligned features
            merge_params = merge_defaults(
                method=self.params.merge_method,
                rt_tol=self.params.rt_tolerance,
                mz_tol=self.params.mz_tolerance,
                min_samples=self.params.min_samples_for_merge
            )
            
            self.logger.info(f"Merging features using {self.params.merge_method} method")
            self.study.merge(params=merge_params)
            
            # Log results
            num_consensus = len(self.study.consensus_df) if hasattr(self.study, 'consensus_df') else 0
            self._log_progress(f"Generated {num_consensus} consensus features")
            
            # Get study info
            if hasattr(self.study, 'info'):
                self.study.info()
            
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to align and merge: {e}")
            return False
    
    def generate_plots(self) -> bool:
        """
        Generate visualization plots for the study.
        
        Returns:
            True if plot generation was successful
        """
        if not self.params.generate_plots:
            self._log_progress("Plot generation disabled, skipping...")
            return True
            
        self._log_progress("=== Generating Visualization Plots ===")
        self.current_step = "generating_plots"
        
        if self.study is None:
            self.logger.error("Study not available. Complete previous steps first.")
            return False
        
        try:
            plots_generated = 0
            
            # Alignment plot
            if hasattr(self.study, 'plot_alignment'):
                alignment_plot = self.study_folder_path / "alignment_plot.html"
                self.study.plot_alignment(filename=str(alignment_plot))
                plots_generated += 1
                self.logger.info(f"Generated alignment plot: {alignment_plot}")
            
            # Consensus 2D plot
            if hasattr(self.study, 'plot_consensus_2d'):
                consensus_2d_plot = self.study_folder_path / "consensus_2d.html"
                self.study.plot_consensus_2d(filename=str(consensus_2d_plot))
                plots_generated += 1
                self.logger.info(f"Generated consensus 2D plot: {consensus_2d_plot}")
            
            # PCA plot
            if hasattr(self.study, 'plot_pca'):
                pca_plot = self.study_folder_path / "pca_plot.html"
                self.study.plot_pca(filename=str(pca_plot))
                plots_generated += 1
                self.logger.info(f"Generated PCA plot: {pca_plot}")
            
            # Consensus statistics
            if hasattr(self.study, 'plot_consensus_stats'):
                stats_plot = self.study_folder_path / "consensus_stats.html"
                self.study.plot_consensus_stats(filename=str(stats_plot))
                plots_generated += 1
                self.logger.info(f"Generated statistics plot: {stats_plot}")
            
            self._log_progress(f"Generated {plots_generated} visualization plots")
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate plots: {e}")
            return False
    
    def export_results(self) -> bool:
        """
        Export study results in requested formats.
        
        Returns:
            True if export was successful
        """
        self._log_progress("=== Exporting Study Results ===")
        self.current_step = "exporting_results"
        
        if self.study is None:
            self.logger.error("Study not available. Complete previous steps first.")
            return False
        
        try:
            exports_completed = 0
            
            # Export consensus features as CSV
            if "csv" in self.params.export_formats:
                csv_file = self.study_folder_path / "consensus_features.csv"
                if hasattr(self.study.consensus_df, 'write_csv'):
                    self.study.consensus_df.write_csv(str(csv_file))
                exports_completed += 1
                self.logger.info(f"Exported CSV: {csv_file}")
            
            # Export as Excel
            if "xlsx" in self.params.export_formats and hasattr(self.study, 'export_xlsx'):
                xlsx_file = self.study_folder_path / "study_results.xlsx"
                self.study.export_xlsx(filename=str(xlsx_file))
                exports_completed += 1
                self.logger.info(f"Exported Excel: {xlsx_file}")
            
            # Export MGF for MS2 spectra
            if "mgf" in self.params.export_formats and hasattr(self.study, 'export_mgf'):
                mgf_file = self.study_folder_path / "consensus_ms2.mgf"
                self.study.export_mgf(filename=str(mgf_file))
                exports_completed += 1
                self.logger.info(f"Exported MGF: {mgf_file}")
            
            # Export as Parquet for efficient storage
            if "parquet" in self.params.export_formats and hasattr(self.study, 'export_parquet'):
                parquet_file = self.study_folder_path / "study_data.parquet"
                self.study.export_parquet(filename=str(parquet_file))
                exports_completed += 1
                self.logger.info(f"Exported Parquet: {parquet_file}")
            
            self._log_progress(f"Completed {exports_completed} exports")
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return False
    
    def save_study(self) -> bool:
        """
        Save the final study in optimized format.
        
        Returns:
            True if study was saved successfully
        """
        self._log_progress("=== Saving Final Study ===")
        self.current_step = "saving_study"
        
        if self.study is None:
            self.logger.error("Study not available. Complete previous steps first.")
            return False
        
        try:
            study_file = self.study_folder_path / "final_study.study5"
            
            # Determine optimal save format based on study size
            num_samples = len(self.study.samples_df)
            num_features = len(self.study.consensus_df) if hasattr(self.study, 'consensus_df') else 0
            
            if self.params.adaptive_compression:
                # Use compressed format for large studies
                if num_samples > 50 or num_features > 10000:
                    self.logger.info(f"Large study detected ({num_samples} samples, {num_features} features) - using compressed format")
                    self.params.compress_output = True
                else:
                    self.logger.info(f"Small study ({num_samples} samples, {num_features} features) - using standard format")
                    self.params.compress_output = False
            
            # Save study
            if self.params.compress_output and hasattr(self.study, 'save_compressed'):
                self.study.save_compressed(filename=str(study_file))
                self.logger.info(f"Saved compressed study: {study_file}")
            else:
                self.study.save(filename=str(study_file))
                self.logger.info(f"Saved study: {study_file}")
            
            # Save metadata summary
            metadata_file = self.study_folder_path / "study_metadata.txt"
            with open(metadata_file, "w") as f:
                f.write("Study Processing Summary\n")
                f.write("========================\n")
                f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Polarity: {self.polarity}\n")
                f.write(f"Adducts: {', '.join(self.adducts)}\n")
                f.write(f"Number of Samples: {num_samples}\n")
                f.write(f"Number of Consensus Features: {num_features}\n")
                f.write(f"Successful Files: {len(self.processed_files)}\n")
                f.write(f"Failed Files: {len(self.failed_files)}\n")
                f.write(f"RT Tolerance: {self.params.rt_tolerance}s\n")
                f.write(f"m/z Tolerance: {self.params.mz_tolerance} Da\n")
                f.write(f"Merge Method: {self.params.merge_method}\n")
                f.write(f"Processing Time: {self._get_total_processing_time()}\n")
            
            self._log_progress(f"Saved study metadata: {metadata_file}")
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save study: {e}")
            return False
    
    def cleanup_temp_files(self) -> bool:
        """
        Clean up temporary files if requested.
        
        Returns:
            True if cleanup was successful
        """
        if not self.params.cleanup_temp_files:
            return True
            
        self._log_progress("=== Cleaning Up Temporary Files ===")
        
        try:
            cleaned_count = 0
            
            # Remove individual sample plots if study plots were generated
            if self.params.generate_plots:
                temp_plots = list(self.study_folder_path.glob("*_2d.html"))
                for plot_file in temp_plots:
                    if plot_file.name not in ["alignment_plot.html", "consensus_2d.html", "pca_plot.html"]:
                        plot_file.unlink()
                        cleaned_count += 1
            
            # Remove checkpoint file
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                cleaned_count += 1
            
            self._log_progress(f"Cleaned up {cleaned_count} temporary files")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """
        Run the complete automated processing pipeline.
        
        This method executes all processing steps in sequence:
        1. Convert raw files to sample5 format
        2. Assemble study from sample5 files
        3. Align and merge features
        4. Generate visualization plots
        5. Export results in requested formats
        6. Save final study
        7. Clean up temporary files
        
        Returns:
            True if the entire pipeline completed successfully
        """
        self._log_progress("=" * 60)
        self._log_progress("STARTING AUTOMATED STUDY PROCESSING PIPELINE")
        self._log_progress("=" * 60)
        
        self.start_time = time.time()
        pipeline_success = True
        
        try:
            # Step 1: Convert to sample5
            if not self.convert_to_sample5():
                self.logger.error("Sample5 conversion failed")
                return False
            
            # Step 2: Assemble study
            if not self.assemble_study():
                self.logger.error("Study assembly failed")
                return False
            
            # Step 3: Align and merge
            if not self.align_and_merge():
                self.logger.error("Feature alignment and merging failed")
                return False
            
            # Step 4: Generate plots
            if not self.generate_plots():
                self.logger.warning("Plot generation failed, continuing...")
                pipeline_success = False
            
            # Step 5: Export results
            if not self.export_results():
                self.logger.warning("Result export failed, continuing...")
                pipeline_success = False
            
            # Step 6: Save study
            if not self.save_study():
                self.logger.error("Study saving failed")
                return False
            
            # Step 7: Cleanup
            if not self.cleanup_temp_files():
                self.logger.warning("Cleanup failed, continuing...")
            
            # Final summary
            total_time = time.time() - self.start_time
            self._log_progress("=" * 60)
            self._log_progress("PIPELINE COMPLETED SUCCESSFULLY")
            self._log_progress(f"Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            self._log_progress(f"Files processed: {len(self.processed_files)}")
            self._log_progress(f"Files failed: {len(self.failed_files)}")
            if hasattr(self.study, 'consensus_df'):
                self._log_progress(f"Consensus features: {len(self.study.consensus_df)}")
            self._log_progress("=" * 60)
            
            return pipeline_success
            
        except KeyboardInterrupt:
            self.logger.info("Pipeline interrupted by user")
            self._save_checkpoint()
            return False
        except Exception as e:
            self.logger.error(f"Pipeline failed with unexpected error: {e}")
            self._save_checkpoint()
            return False
    
    def _get_total_processing_time(self) -> str:
        """Get formatted total processing time."""
        if self.start_time is None:
            return "Unknown"
        
        total_seconds = time.time() - self.start_time
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current processing status.
        
        Returns:
            Dictionary with current status information
        """
        return {
            "current_step": self.current_step,
            "processed_files": len(self.processed_files),
            "failed_files": len(self.failed_files),
            "study_loaded": self.study is not None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "processing_time": self._get_total_processing_time(),
            "parameters": {
                "data_source": self.params.data_source,
                "study_folder": self.params.study_folder,
                "polarity": self.params.polarity,
                "num_cores": self.params.num_cores,
                "adducts": self.params.adducts,
            }
        }
    
    def info(self):
        """Print comprehensive wizard status information."""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("WIZARD STATUS")
        print("=" * 50)
        print(f"Current Step: {status['current_step']}")
        print(f"Data Source: {self.params.data_source}")
        print(f"Study Folder: {self.params.study_folder}")
        print(f"Polarity: {status['parameters']['polarity']}")
        print(f"CPU Cores: {status['parameters']['num_cores']}")
        print(f"Adducts: {', '.join(status['parameters']['adducts'])}")
        print(f"Processing Time: {status['processing_time']}")
        print(f"Files Processed: {status['processed_files']}")
        print(f"Files Failed: {status['failed_files']}")
        print(f"Study Loaded: {status['study_loaded']}")
        
        if self.study is not None and hasattr(self.study, 'samples_df'):
            print(f"Samples in Study: {len(self.study.samples_df)}")
        
        if self.study is not None and hasattr(self.study, 'consensus_df'):
            print(f"Consensus Features: {len(self.study.consensus_df)}")
        
        print("=" * 50)


# Export the main classes
__all__ = ["Wizard", "wizard_def"]
