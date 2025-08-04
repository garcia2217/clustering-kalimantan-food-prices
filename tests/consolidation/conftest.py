"""Pytest configuration and shared fixtures."""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path

from clustering_food_prices_kalimantan import ConsolidatorConfig, PathConfig


@pytest.fixture
def temp_directory():
    """Provide a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config():
    """Provide a test configuration with logging disabled."""
    return ConsolidatorConfig(
        enable_logging=False,
        log_level="WARNING"
    )


@pytest.fixture
def sample_excel_data():
    """Provide sample Excel data for testing."""
    return pd.DataFrame({
        'Komoditas (Rp)': ['Beras', 'Telur Ayam', 'Daging Ayam'],
        'Jan-23': [12000, 25000, 35000],
        'Feb-23': [12500, 26000, 36000],
        'Mar-23': [13000, 27000, 37000]
    })


@pytest.fixture
def sample_consolidated_data():
    """Provide sample consolidated data for testing."""
    return pd.DataFrame({
        'City': ['pontianak', 'banjarmasin', 'pontianak', 'banjarmasin'],
        'Commodities': ['Beras', 'Beras', 'Telur Ayam', 'Telur Ayam'],
        'Price': [12000, 12200, 25000, 25500],
        'Date': pd.date_range('2023-01-01', periods=4, freq='MS')
    })


@pytest.fixture
def test_data_directory(temp_directory, sample_excel_data):
    """Create a test directory with sample Excel files."""
    # Create directory structure
    province_dir = temp_directory / "data" / "raw" / "kalimantan-barat"
    city1_dir = province_dir / "kota-pontianak"
    city2_dir = province_dir / "kota-singkawang"
    
    city1_dir.mkdir(parents=True)
    city2_dir.mkdir(parents=True)
    
    # Create test Excel files
    sample_excel_data.to_excel(city1_dir / "2023.xlsx", index=False)
    sample_excel_data.to_excel(city2_dir / "2023.xlsx", index=False)
    
    # Create additional year file
    sample_excel_data.to_excel(city1_dir / "2022.xlsx", index=False)
    
    return temp_directory / "data"