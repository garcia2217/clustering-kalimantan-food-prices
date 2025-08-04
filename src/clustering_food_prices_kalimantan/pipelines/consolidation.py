"""Data consolidation pipeline for food price data."""

import logging
from pathlib import Path
from typing import Dict, Optional, Union, List
import pandas as pd

from ..config.settings import ConsolidatorConfig, PathConfig
from ..data import DataConsolidator


class ConsolidationPipeline:
    """
    High-level pipeline for food price data consolidation.
    
    Provides a simple interface to consolidate food price data from multiple Excel files
    across different cities in Kalimantan into a single standardized dataset.
    """
    
    def __init__(self, 
                 data_root: Optional[Union[str, Path]] = None,
                 config: Optional[ConsolidatorConfig] = None,
                 paths: Optional[PathConfig] = None):
        """
        Initialize the consolidation pipeline.
        
        Args:
            data_root: Root directory containing raw data files (defaults to 'data/raw')
            config: Configuration instance (uses default if None)
            paths: Path configuration instance (uses default if None)
        """
        self.config = config or ConsolidatorConfig()
        self.paths = paths or PathConfig()
        
        # Set data root
        if data_root:
            self.data_root = Path(data_root)
        else:
            self.data_root = self.paths.raw_data_dir
        
        # Ensure output directories exist
        self.paths.create_directories()
        
        # Initialize consolidator
        self.consolidator = DataConsolidator(
            root_directory=self.data_root,
            config=self.config
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_consolidation(self, 
                         target_commodities: Optional[List[str]] = None,
                         save_outputs: bool = True,
                         output_formats: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Run the complete data consolidation pipeline.
        
        Args:
            target_commodities: List of commodities to filter for (overrides config)
            save_outputs: Whether to save consolidated data to files
            output_formats: List of formats to save ('csv', 'excel' or both)
            
        Returns:
            Consolidated DataFrame
        """
        self.logger.info("Starting data consolidation pipeline...")
        
        # Override target commodities if provided
        if target_commodities:
            self.consolidator.target_commodities = target_commodities
        
        # Run consolidation
        consolidated_df = self.consolidator.consolidate_data()
        
        if consolidated_df.empty:
            self.logger.error("Consolidation produced no data")
            return consolidated_df
        
        # Save outputs if requested
        if save_outputs:
            self._save_consolidated_data(consolidated_df, output_formats)
        
        self.logger.info("Data consolidation pipeline completed successfully!")
        return consolidated_df
    
    def _save_consolidated_data(self, 
                               df: pd.DataFrame,
                               output_formats: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Save consolidated data to specified formats.
        
        Args:
            df: Consolidated DataFrame to save
            output_formats: List of formats to save ('csv', 'excel' or both)
            
        Returns:
            Dictionary with save status for each format
        """
        if output_formats is None:
            output_formats = ['csv', 'excel']
        
        results = {}
        
        # Prepare filenames
        csv_filename = None
        excel_filename = None
        
        if 'csv' in output_formats:
            csv_filename = self.config.default_csv_output
        if 'excel' in output_formats:
            excel_filename = self.config.default_excel_output
        
        # Save to processed data directory
        save_results = self.consolidator.save_data(
            df=df,
            csv_filename=csv_filename,
            excel_filename=excel_filename,
            output_dir=self.paths.processed_data_dir
        )
        
        return save_results
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of the consolidated data.
        
        Args:
            df: Consolidated DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {}
        
        summary = {
            'total_records': len(df),
            'num_cities': df[self.config.city_col].nunique(),
            'num_commodities': df[self.config.commodity_col].nunique(),
            'num_unique_dates': df[self.config.date_col].nunique(),
            'cities': sorted(df[self.config.city_col].unique().tolist()),
            'commodities': sorted(df[self.config.commodity_col].unique().tolist()),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict()
        }
        
        # Add price statistics if price column is numeric
        if pd.api.types.is_numeric_dtype(df[self.config.price_col]):
            price_stats = df[self.config.price_col].describe().to_dict()
            summary['price_statistics'] = price_stats
        
        # Add date range if date column is datetime
        if pd.api.types.is_datetime64_any_dtype(df[self.config.date_col]):
            date_stats = {
                'date_range_start': df[self.config.date_col].min(),
                'date_range_end': df[self.config.date_col].max()
            }
            summary['date_statistics'] = date_stats
        
        return summary
    
    def validate_data_structure(self) -> Dict[str, List[str]]:
        """
        Validate the data directory structure and files.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid_files': [],
            'invalid_files': [],
            'missing_directories': [],
            'issues': []
        }
        
        # Check if data root exists
        if not self.data_root.exists():
            results['issues'].append(f"Data root directory does not exist: {self.data_root}")
            return results
        
        # Find all Excel files
        try:
            excel_files = self.consolidator.loader.find_excel_files(self.data_root)
            
            for file_path in excel_files:
                # Validate file path
                is_valid, issues = self.consolidator.validator.validate_file_path(file_path)
                
                if is_valid:
                    results['valid_files'].append(str(file_path))
                else:
                    results['invalid_files'].append(str(file_path))
                    results['issues'].extend(issues)
        
        except Exception as e:
            results['issues'].append(f"Error during file discovery: {str(e)}")
        
        return results
