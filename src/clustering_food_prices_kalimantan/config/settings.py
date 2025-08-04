"""Configuration settings for the food price consolidation process."""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConsolidatorConfig(BaseSettings):
    """Configuration settings for the data consolidation process."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CONSOLIDATOR_",
        case_sensitive=False,
    )
    
    # Target commodities to extract from the data
    target_commodities: List[str] = Field(
        default=[
            'Beras',
            'Telur Ayam', 
            'Daging Ayam',
            'Bawang Merah',
            'Bawang Putih'
        ],
        description="List of commodities to extract from the data"
    )
    
    # File processing settings
    file_pattern: str = Field(
        default="*.xlsx",
        description="File pattern to search for"
    )
    
    # Columns to drop from source data
    columns_to_drop: List[str] = Field(
        default=["No"],
        description="Column names to drop from source data"
    )
    
    # Output column names
    commodity_col: str = Field(
        default="Commodities",
        description="Name for the commodity column in output"
    )
    
    original_commodity_col: str = Field(
        default="Komoditas (Rp)",
        description="Original commodity column name in source data"
    )
    
    city_col: str = Field(
        default="City",
        description="Name for the city column in output"
    )
    
    date_col: str = Field(
        default="Date",
        description="Name for the date column in output"
    )
    
    price_col: str = Field(
        default="Price",
        description="Name for the price column in output"
    )
    
    # Missing value indicators
    missing_value_indicators: List[str] = Field(
        default=['-', '', 'nan', 'NaN', 'null', 'NULL'],
        description="Values that should be treated as missing"
    )
    
    # Default output filenames
    default_csv_output: str = Field(
        default="master_data_consolidated.csv",
        description="Default CSV output filename"
    )
    
    default_excel_output: str = Field(
        default="master_data_consolidated.xlsx",
        description="Default Excel output filename"
    )
    
    # Processing settings
    enable_logging: bool = Field(
        default=True,
        description="Whether to enable detailed logging"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Data validation settings
    min_expected_columns: int = Field(
        default=2,
        description="Minimum number of columns expected in source data"
    )
    
    # Performance settings
    chunk_size: Optional[int] = Field(
        default=None,
        description="Chunk size for processing large files"
    )
    
    # Data filtering settings
    target_years: Optional[List[int]] = Field(
        default=None,
        description="List of years to process (e.g., [2020, 2021, 2022]). If None, processes all available years"
    )
    
    target_cities: Optional[List[str]] = Field(
        default=["kab-sintang", "kota-pontianak", "kota-singkawang", "kota-banjarmasin",
                "kota-tanjung", "kota-palangkaraya", "kota-sampit", "kota-balikpapan",
                "kota-samarinda", "kota-tarakan"],
        description="List of cities to process (e.g., ['kota-pontianak', 'kota-banjarmasin']). If None, processes all available cities"
    )
    
    # Year range settings (alternative to target_years list)
    year_range_start: Optional[int] = Field(
        default=2018,
        description="Start year for processing (inclusive). Used only if target_years is None"
    )
    
    year_range_end: Optional[int] = Field(
        default=2024,
        description="End year for processing (inclusive). Used only if target_years is None"
    )
    
    @field_validator('target_years', mode='before')
    @classmethod
    def parse_target_years(cls, v):
        """Parse target_years from string (for environment variables) or return as-is."""
        if isinstance(v, str) and v:
            # Split comma-separated string and convert to integers
            return [int(year.strip()) for year in v.split(',')]
        return v
    
    @field_validator('target_cities', mode='before')
    @classmethod
    def parse_target_cities(cls, v):
        """Parse target_cities from string (for environment variables) or return as-is."""
        if isinstance(v, str) and v:
            # Split comma-separated string and strip whitespace
            return [city.strip() for city in v.split(',')]
        return v


class PathConfig(BaseModel):
    """Path configuration for data directories."""
    
    data_root: Path = Field(
        default=Path("data"),
        description="Root directory for all data"
    )
    
    raw_data_dir: Path = Field(
        default=Path("data/raw"),
        description="Directory containing raw data files"
    )
    
    processed_data_dir: Path = Field(
        default=Path("data/processed"),
        description="Directory for processed output files"
    )
    
    features_data_dir: Path = Field(
        default=Path("data/features"),
        description="Directory for feature-engineered data"
    )
    
    logs_dir: Path = Field(
        default=Path("logs"),
        description="Directory for log files"
    )
    
    def create_directories(self) -> None:
        """Create all configured directories if they don't exist."""
        for field_name in self.__class__.model_fields:
            path_value = getattr(self, field_name)
            if isinstance(path_value, Path):
                path_value.mkdir(parents=True, exist_ok=True)


# Global configuration instances
config = ConsolidatorConfig()
paths = PathConfig()