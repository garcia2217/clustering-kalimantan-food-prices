"""Data cleaning and transformation utilities."""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

from ..config.settings import ConsolidatorConfig


class DataCleaner:
    """Handles data cleaning and transformation operations."""
    
    def __init__(self, config: ConsolidatorConfig, logger: Optional[logging.Logger] = None):
        """Initialize cleaner with configuration."""
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    def clean_dataframe(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """
        Clean and prepare DataFrame.
        
        Args:
            df: Raw DataFrame from Excel
            file_path: Source file path
            
        Returns:
            Cleaned DataFrame
        """
        # Drop unnecessary columns
        columns_to_drop = [col for col in self.config.columns_to_drop if col in df.columns]
        df = df.drop(columns=columns_to_drop)
        
        # Rename commodity column from original to new name
        if self.config.original_commodity_col in df.columns:
            df = df.rename(columns={self.config.original_commodity_col: self.config.commodity_col})
        
        # Add city information
        city_name = self._extract_city_from_path(file_path)
        df[self.config.city_col] = city_name
        
        return df
    
    def transform_to_long_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform DataFrame from wide to long format.
        
        Args:
            df: DataFrame in wide format
            
        Returns:
            DataFrame in long format
        """
        # Identify non-date columns (commodity and city)
        id_vars = [self.config.commodity_col, self.config.city_col]
        
        # Melt DataFrame to long format
        long_df = df.melt(
            id_vars=id_vars,
            var_name=self.config.date_col,
            value_name=self.config.price_col
        )
        
        return long_df
    
    def filter_commodities(self, df: pd.DataFrame, target_commodities: list) -> pd.DataFrame:
        """
        Filter DataFrame for target commodities.
        
        Args:
            df: DataFrame to filter
            target_commodities: List of commodities to keep
            
        Returns:
            Filtered DataFrame
        """
        return df[df[self.config.commodity_col].isin(target_commodities)].copy()
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the price data using forward fill and backward fill.
        
        Args:
            df: DataFrame with potential missing values
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        # Replace missing value indicators with NaN
        for indicator in self.config.missing_value_indicators:
            df[self.config.price_col] = df[self.config.price_col].replace(indicator, np.nan)
        
        # Sort by City, Commodity, and Date for proper forward/backward fill
        df = df.sort_values([self.config.city_col, self.config.commodity_col, self.config.date_col])
        
        # Group by City and Commodity, then apply forward fill and backward fill
        df[self.config.price_col] = df.groupby([self.config.city_col, self.config.commodity_col])[self.config.price_col].ffill().bfill()
        
        # Log missing value handling
        remaining_missing = df[self.config.price_col].isna().sum()
        if remaining_missing > 0:
            self.logger.warning(f"Still have {remaining_missing} missing values after forward/backward fill")
        else:
            self.logger.info("Successfully handled all missing values with forward/backward fill")
        
        return df
    
    def convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert column data types to appropriate types with robust data cleaning.
        
        Args:
            df: DataFrame with object types
            
        Returns:
            DataFrame with proper data types
        """
        df = df.copy()
        
        try:
            # Clean and convert Price column to numeric
            df[self.config.price_col] = self._clean_and_convert_price(df[self.config.price_col])
            
            # Clean and convert Date column to datetime
            df[self.config.date_col] = self._clean_and_convert_date(df[self.config.date_col])
            
            # Convert categorical columns to category type for memory efficiency
            df[self.config.city_col] = df[self.config.city_col].astype('category')
            df[self.config.commodity_col] = df[self.config.commodity_col].astype('category')
            
            # Log conversion results
            self._log_conversion_results(df)
            
        except Exception as e:
            self.logger.error(f"Error converting data types: {str(e)}")
            
        return df
    
    def _clean_and_convert_price(self, price_series: pd.Series) -> pd.Series:
        """
        Cleans a price series by removing commas and converts it to a numeric type.

        This simplified function is optimized for price data that uses commas as
        thousands separators and contains no currency symbols.

        Args:
            price_series: A pandas Series containing price strings, e.g., "1,250,000".

        Returns:
            A pandas Series of numeric price data.
        """
        # Use .loc to avoid SettingWithCopyWarning if price_series is a slice
        original_series = price_series.loc[:]

        # Convert to string, remove commas, and convert to numeric in one chain.
        # .str.replace is vectorized and much faster than applying a custom function.
        numeric_series = pd.to_numeric(
            original_series.astype(str).str.replace(',', '', regex=False),
            errors='coerce'  # Automatically turn failed conversions into NaN
        )

        # Optional: Log the results of the conversion
        original_count = len(original_series)
        nan_count = numeric_series.isna().sum()

        if original_count > 0:
            success_rate = ((original_count - nan_count) / original_count) * 100
            self.logger.info(
                f"Price conversion: {original_count - nan_count}/{original_count} "
                f"successful ({success_rate:.1f}%)"
            )

        if nan_count > 0:
            # Show some examples of failed conversions for debugging
            failed_examples = original_series[numeric_series.isna()].head(5).tolist()
            self.logger.warning(
                f"Failed to convert {nan_count} price values. "
                f"Examples: {failed_examples}"
            )

        return numeric_series
    
    def _clean_and_convert_date(self, date_series: pd.Series) -> pd.Series:
        """
        Cleans and converts date data to datetime format using a specific format.

        This function is optimized to parse dates exclusively in the 'dd/ mm/ YYYY'
        format. It will efficiently convert them to datetime objects.

        Args:
            date_series: A pandas Series containing date strings, e.g., "15/ 01/ 2024".

        Returns:
            A pandas Series of datetime data.
        """
        # Use a single, direct call to pd.to_datetime. It's highly optimized.
        # The 'format' argument ensures it only parses this specific format.
        # The 'errors' argument handles any values that don't match the format.
        datetime_series = pd.to_datetime(
            date_series,
            format='%d/ %m/ %Y',
            errors='coerce'  # Automatically turn failed conversions into NaT (Not a Time)
        )

        # Optional: Log the results of the conversion
        original_count = len(date_series)
        nat_count = datetime_series.isna().sum()

        if original_count > 0:
            success_rate = ((original_count - nat_count) / original_count) * 100
            self.logger.info(
                f"Date conversion: {original_count - nat_count}/{original_count} "
                f"successful ({success_rate:.1f}%)"
            )

        if nat_count > 0:
            # Show some examples of failed conversions for debugging
            failed_examples = date_series[datetime_series.isna()].head(5).tolist()
            self.logger.warning(
                f"Failed to convert {nat_count} date values. "
                f"Examples: {failed_examples}"
            )

        return datetime_series
    
    def _log_conversion_results(self, df: pd.DataFrame) -> None:
        """
        Log detailed results of data type conversion.
        
        Args:
            df: DataFrame after conversion
        """
        self.logger.info("=== Data Type Conversion Results ===")
        
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            total_count = len(df[col])
            
            if null_count > 0:
                null_pct = (null_count / total_count) * 100
                self.logger.info(f"{col}: {dtype} ({null_count}/{total_count} null, {null_pct:.1f}%)")
            else:
                self.logger.info(f"{col}: {dtype} (no null values)")
                
            # Additional info for numeric and datetime columns
            if pd.api.types.is_numeric_dtype(df[col]) and col == self.config.price_col:
                if null_count < total_count:  # Only if we have valid values
                    valid_data = df[col].dropna()
                    self.logger.info(f"  Price range: {valid_data.min():,.0f} - {valid_data.max():,.0f}")
            
            elif pd.api.types.is_datetime64_any_dtype(df[col]) and col == self.config.date_col:
                if null_count < total_count:  # Only if we have valid values
                    valid_data = df[col].dropna()
                    self.logger.info(f"  Date range: {valid_data.min()} to {valid_data.max()}")
    
    def _extract_city_from_path(self, file_path: Path) -> str:
        """
        Extract city name from file path.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            City name extracted from path
        """
        return file_path.parts[-2]
