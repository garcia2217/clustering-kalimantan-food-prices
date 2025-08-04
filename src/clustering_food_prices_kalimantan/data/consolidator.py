"""Data consolidation orchestrator."""

import logging
import warnings
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..config.settings import ConsolidatorConfig, PathConfig
from .validator import DataValidator
from .loader import DataLoader
from .cleaner import DataCleaner


class DataConsolidator:
    """
    Main class for consolidating food price data from multiple Excel files.
    Orchestrates the data loading, validation, cleaning, and consolidation process.
    """
    
    def __init__(self, 
                 root_directory: Union[str, Path], 
                 config: Optional[ConsolidatorConfig] = None,
                 target_commodities: Optional[List[str]] = None,
                 enable_logging: Optional[bool] = None):
        """
        Initialize the consolidator.
        
        Args:
            root_directory: Path to the main data directory
            config: Configuration instance (uses default if None)
            target_commodities: List of commodities to filter for (overrides config)
            enable_logging: Whether to enable logging (overrides config)
        """
        self.config = config or ConsolidatorConfig()
        self.root_directory = Path(root_directory)
        
        # Override config values if explicitly provided
        if target_commodities is not None:
            self.target_commodities = target_commodities
        else:
            self.target_commodities = self.config.target_commodities.copy()
        
        # Set up logging
        enable_log = enable_logging if enable_logging is not None else self.config.enable_logging
        if enable_log:
            self._setup_logging()
        else:
            # Create a null logger
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(logging.NullHandler())
        
        # Initialize components with shared logger and config
        self.validator = DataValidator(self.config)
        self.loader = DataLoader(self.config, self.logger)
        self.cleaner = DataCleaner(self.config, self.logger)
        
        # Suppress pandas warnings for cleaner output
        warnings.filterwarnings('ignore', category=UserWarning)
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        paths = PathConfig()
        paths.create_directories()
        
        # Set up log file path
        log_file = paths.logs_dir / 'food_price_consolidation.log'
        
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def consolidate_data(self) -> pd.DataFrame:
        """
        Main method to consolidate all data files.
        
        Returns:
            Consolidated DataFrame
        """
        self.logger.info(f"Starting consolidation in: {self.root_directory.resolve()}")
        
        # Find all Excel files
        excel_files = self.loader.find_excel_files(self.root_directory)
        self.logger.info(f"Found {len(excel_files)} Excel files to process")
        
        # Process each file
        processed_dataframes = []
        successful_files = 0
        
        for file_path in excel_files:
            processed_df = self._process_single_file(file_path)
            if processed_df is not None:
                processed_dataframes.append(processed_df)
                successful_files += 1
        
        # Consolidate results
        if not processed_dataframes:
            self.logger.error("No data could be processed successfully")
            return pd.DataFrame()
        
        self.logger.info(f"Successfully processed {successful_files}/{len(excel_files)} files")
        self.logger.info("Consolidating data into master DataFrame...")
        
        master_df = pd.concat(processed_dataframes, ignore_index=True)
        
        # Basic data quality report
        self._log_data_summary(master_df)
        
        return master_df
    
    def _process_single_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Process a single Excel file using the modular components.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Processed DataFrame or None if processing failed
        """
        try:
            # Load Excel file
            df = self.loader.load_excel_file(file_path)
            if df is None:
                return None
            
            # Validate DataFrame
            is_valid, issues = self.validator.validate_dataframe(df, file_path)
            if not is_valid:
                for issue in issues:
                    self.logger.warning(issue)
                return None
            
            # Clean and prepare data
            df = self.cleaner.clean_dataframe(df, file_path)
            
            # Transform to long format
            long_df = self.cleaner.transform_to_long_format(df)
            
            # Handle missing values (forward fill and backward fill)
            long_df = self.cleaner.handle_missing_values(long_df)
            
            # Convert data types to appropriate types
            long_df = self.cleaner.convert_data_types(long_df)
            
            # Filter commodities
            filtered_df = self.cleaner.filter_commodities(long_df, self.target_commodities)
            
            if not filtered_df.empty:
                self.logger.info(f"Successfully processed {file_path.name} for {df[self.config.city_col].iloc[0]}")
                return filtered_df
            else:
                self.logger.warning(f"No target commodities found in {file_path.name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to process {file_path.name}: {str(e)}")
            return None
    
    def _log_data_summary(self, df: pd.DataFrame) -> None:
        """
        Log summary statistics of the consolidated data.
        
        Args:
            df: Consolidated DataFrame
        """
        self.logger.info("=== Data Summary ===")
        self.logger.info(f"Total records: {len(df):,}")
        self.logger.info(f"Cities: {df[self.config.city_col].nunique()}")
        self.logger.info(f"Commodities: {df[self.config.commodity_col].nunique()}")
        self.logger.info(f"Date range: {df[self.config.date_col].nunique()} unique dates")
        
        # Log data types
        self.logger.info("=== Data Types ===")
        for col in df.columns:
            self.logger.info(f"{col}: {df[col].dtype}")
        
        # Log missing values
        missing_values = df.isnull().sum()
        total_missing = missing_values.sum()
        if total_missing > 0:
            self.logger.warning(f"Total missing values: {total_missing}")
            for col, count in missing_values.items():
                if count > 0:
                    self.logger.warning(f"  {col}: {count} missing values")
        else:
            self.logger.info("No missing values in final dataset")
        
        # Log cities found
        cities = sorted(df[self.config.city_col].unique())
        self.logger.info(f"Cities included: {', '.join(cities)}")
        
        # Log commodities found
        commodities = sorted(df[self.config.commodity_col].unique())
        self.logger.info(f"Commodities included: {', '.join(commodities)}")
        
        # Log price statistics
        if pd.api.types.is_numeric_dtype(df[self.config.price_col]):
            price_stats = df[self.config.price_col].describe()
            self.logger.info(f"Price range: {price_stats['min']:,.0f} - {price_stats['max']:,.0f}")
            self.logger.info(f"Average price: {price_stats['mean']:,.0f}")
    
    def save_data(self, 
                  df: pd.DataFrame, 
                  csv_filename: Optional[str] = None,
                  excel_filename: Optional[str] = None,
                  output_dir: Optional[Union[str, Path]] = None) -> Dict[str, bool]:
        """
        Save DataFrame to CSV and Excel files.
        
        Args:
            df: DataFrame to save
            csv_filename: CSV output filename
            excel_filename: Excel output filename
            output_dir: Output directory
            
        Returns:
            Dictionary with save status for each format
        """
        if df.empty:
            self.logger.error("Cannot save empty DataFrame")
            return {'csv': False, 'excel': False}
        
        # Set default filenames and output directory
        csv_file = csv_filename or self.config.default_csv_output
        excel_file = excel_filename or self.config.default_excel_output
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            csv_file = output_path / csv_file
            excel_file = output_path / excel_file
        
        results = {}
        
        # Save to CSV
        try:
            df.to_csv(csv_file, index=False, encoding='utf-8')
            results['csv'] = True
            self.logger.info(f"Successfully saved CSV: {csv_file}")
        except Exception as e:
            results['csv'] = False
            self.logger.error(f"Failed to save CSV: {str(e)}")
        
        # Save to Excel
        try:
            df.to_excel(excel_file, index=False, sheet_name='Consolidated_Data')
            results['excel'] = True
            self.logger.info(f"Successfully saved Excel: {excel_file}")
        except Exception as e:
            results['excel'] = False
            self.logger.error(f"Failed to save Excel: {str(e)}")
        
        return results
