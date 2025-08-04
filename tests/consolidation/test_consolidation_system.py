"""Comprehensive tests for the food price data consolidation system."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import logging
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from clustering_food_prices_kalimantan import (
    ConsolidationPipeline, 
    ConsolidatorConfig, 
    PathConfig,
    DataValidator,
    DataLoader,
    DataCleaner,
    DataConsolidator
)


class TestConsolidatorConfig:
    """Test configuration settings."""
    
    def test_default_config_values(self):
        """Test that default configuration values are set correctly."""
        config = ConsolidatorConfig()
        
        assert len(config.target_commodities) == 5
        assert "Beras" in config.target_commodities
        assert "Telur Ayam" in config.target_commodities
        assert config.file_pattern == "*.xlsx"
        assert config.log_level == "INFO"
        assert config.enable_logging is True
        
    def test_custom_config_values(self):
        """Test creating config with custom values."""
        custom_commodities = ["Beras", "Gula"]
        config = ConsolidatorConfig(
            target_commodities=custom_commodities,
            log_level="DEBUG",
            target_years=[2023, 2024]
        )
        
        assert config.target_commodities == custom_commodities
        assert config.log_level == "DEBUG"
        assert config.target_years == [2023, 2024]


class TestPathConfig:
    """Test path configuration."""
    
    def test_default_paths(self):
        """Test default path values."""
        paths = PathConfig()
        
        assert paths.data_root == Path("data")
        assert paths.raw_data_dir == Path("data/raw")
        assert paths.processed_data_dir == Path("data/processed")
        assert paths.logs_dir == Path("logs")
        
    def test_create_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            paths = PathConfig(
                data_root=temp_path / "data",
                raw_data_dir=temp_path / "data" / "raw",
                processed_data_dir=temp_path / "data" / "processed",
                logs_dir=temp_path / "logs"
            )
            
            paths.create_directories()
            
            assert (temp_path / "data").exists()
            assert (temp_path / "data" / "raw").exists()
            assert (temp_path / "data" / "processed").exists()
            assert (temp_path / "logs").exists()


class TestDataValidator:
    """Test data validation functionality."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return ConsolidatorConfig()
    
    @pytest.fixture
    def validator(self, config):
        """Provide validator instance."""
        return DataValidator(config)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Provide sample DataFrame for testing."""
        return pd.DataFrame({
            'Komoditas (Rp)': ['Beras', 'Telur Ayam', 'Daging Ayam'],
            'Jan-18': [12000, 25000, 35000],
            'Feb-18': [12500, 26000, 36000],
            'Mar-18': [13000, 27000, 37000]
        })
    
    def test_validate_dataframe_success(self, validator, sample_dataframe):
        """Test successful DataFrame validation."""
        is_valid, issues = validator.validate_dataframe(
            sample_dataframe, 
            Path("test_file.xlsx")
        )
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_dataframe_missing_commodity_column(self, validator):
        """Test validation with missing commodity column."""
        df = pd.DataFrame({
            'Wrong_Column': ['Beras', 'Telur Ayam'],
            'Jan-18': [12000, 25000]
        })
        
        is_valid, issues = validator.validate_dataframe(df, Path("test_file.xlsx"))
        
        assert is_valid is False
        assert any('commodity column' in issue.lower() for issue in issues)
    
    def test_validate_dataframe_empty(self, validator):
        """Test validation with empty DataFrame."""
        df = pd.DataFrame()
        
        is_valid, issues = validator.validate_dataframe(df, Path("test_file.xlsx"))
        
        assert is_valid is False
        assert any('empty' in issue.lower() for issue in issues)
    
    def test_validate_file_path_success(self, validator):
        """Test successful file path validation."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            
            try:
                is_valid, issues = validator.validate_file_path(temp_path)
                assert is_valid is True
                assert len(issues) == 0
            finally:
                temp_path.unlink()
    
    def test_validate_file_path_not_exists(self, validator):
        """Test validation with non-existent file."""
        fake_path = Path("non_existent_file.xlsx")
        
        is_valid, issues = validator.validate_file_path(fake_path)
        
        assert is_valid is False
        assert any('does not exist' in issue for issue in issues)


class TestDataLoader:
    """Test data loading functionality."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return ConsolidatorConfig()
    
    @pytest.fixture
    def loader(self, config):
        """Provide loader instance."""
        return DataLoader(config)
    
    @pytest.fixture
    def sample_excel_data(self):
        """Provide sample Excel data."""
        return pd.DataFrame({
            'Komoditas (Rp)': ['Beras', 'Telur Ayam', 'Daging Ayam'],
            'Jan-18': [12000, 25000, 35000],
            'Feb-18': [12500, 26000, 36000],
            'Mar-18': [13000, 27000, 37000]
        })
    
    @patch('pandas.read_excel')
    def test_load_excel_file_success(self, mock_read_excel, loader, sample_excel_data):
        """Test successful Excel file loading."""
        mock_read_excel.return_value = sample_excel_data
        
        result = loader.load_excel_file(Path("test_file.xlsx"))
        
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        mock_read_excel.assert_called_once()
    
    @patch('pandas.read_excel')
    def test_load_excel_file_failure(self, mock_read_excel, loader):
        """Test Excel file loading failure."""
        mock_read_excel.side_effect = Exception("File not found")
        
        result = loader.load_excel_file(Path("missing_file.xlsx"))
        
        assert result is None
    
    def test_extract_year_from_filename(self, loader):
        """Test year extraction from filename."""
        assert loader._extract_year_from_filename(Path("2023.xlsx")) == 2023
        assert loader._extract_year_from_filename(Path("data_2022.xlsx")) == 2022
        assert loader._extract_year_from_filename(Path("no_year.xlsx")) is None
    
    def test_extract_city_from_path(self, loader):
        """Test city extraction from file path."""
        path = Path("data/raw/kalimantan-barat/kota-pontianak/2023.xlsx")
        city = loader._extract_city_from_path(path)
        assert city == "kota-pontianak"
    
    def test_find_excel_files_filtering(self, loader):
        """Test Excel file finding with filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock directory structure
            city_dir = temp_path / "province" / "kota-pontianak"
            city_dir.mkdir(parents=True)
            
            # Create test files
            (city_dir / "2023.xlsx").touch()
            (city_dir / "2022.xlsx").touch()
            (city_dir / "2021.xlsx").touch()
            (city_dir / "not_excel.txt").touch()
            
            # Test with year filtering
            loader.config.target_years = [2023]
            files = loader.find_excel_files(temp_path)
            
            assert len(files) == 1
            assert "2023.xlsx" in str(files[0])


class TestDataCleaner:
    """Test data cleaning functionality."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return ConsolidatorConfig()
    
    @pytest.fixture
    def cleaner(self, config):
        """Provide cleaner instance."""
        return DataCleaner(config)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Provide sample DataFrame for cleaning."""
        return pd.DataFrame({
            'Komoditas (Rp)': ['Beras', 'Telur Ayam', 'Daging Ayam'],
            'Jan-18': [12000, 25000, 35000],
            'Feb-18': [12500, '-', 36000],  # Missing value
            'Mar-18': [13000, 27000, 37000],
            'No': [1, 2, 3]  # Column to drop
        })
    
    def test_clean_dataframe(self, cleaner, sample_dataframe):
        """Test complete DataFrame cleaning process."""
        result = cleaner.clean_dataframe(sample_dataframe, Path("test.xlsx"))
        
        assert isinstance(result, pd.DataFrame)
        assert 'No' not in result.columns  # Should be dropped
        assert len(result) > 0
    
    def test_transform_to_long_format(self, cleaner, sample_dataframe):
        """Test transformation to long format."""
        # Remove the 'No' column for this test
        df = sample_dataframe.drop(columns=['No'])
        result = cleaner.transform_to_long_format(df)
        
        assert 'Date' in result.columns
        assert 'Price' in result.columns
        assert len(result) > len(sample_dataframe)  # Should have more rows
    
    def test_filter_commodities(self, cleaner):
        """Test commodity filtering."""
        df = pd.DataFrame({
            'Commodities': ['Beras', 'Telur Ayam', 'Unknown Item'],
            'Price': [12000, 25000, 15000],
            'Date': ['2023-01-01', '2023-01-01', '2023-01-01']
        })
        
        target_commodities = ['Beras', 'Telur Ayam']
        result = cleaner.filter_commodities(df, target_commodities)
        
        assert len(result) == 2
        assert 'Unknown Item' not in result['Commodities'].values
    
    def test_handle_missing_values(self, cleaner):
        """Test missing value handling."""
        df = pd.DataFrame({
            'Price': [10000, np.nan, 12000, np.nan, 14000],
            'Date': pd.date_range('2023-01-01', periods=5, freq='MS')
        })
        
        result = cleaner.handle_missing_values(df)
        
        # Should have fewer or equal missing values
        assert result['Price'].isnull().sum() <= df['Price'].isnull().sum()
    
    def test_convert_data_types(self, cleaner):
        """Test data type conversion."""
        df = pd.DataFrame({
            'Price': ['10000', '12000', '14000'],
            'Date': ['2023-01-01', '2023-02-01', '2023-03-01'],
            'City': ['pontianak', 'banjarmasin', 'samarinda']
        })
        
        result = cleaner.convert_data_types(df)
        
        assert pd.api.types.is_numeric_dtype(result['Price'])
        assert pd.api.types.is_datetime64_any_dtype(result['Date'])


class TestDataConsolidator:
    """Test data consolidation orchestration."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return ConsolidatorConfig(enable_logging=False)  # Disable logging for tests
    
    @pytest.fixture
    def temp_directory(self):
        """Provide temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def consolidator(self, config, temp_directory):
        """Provide consolidator instance."""
        return DataConsolidator(temp_directory, config)
    
    def test_consolidator_initialization(self, consolidator, temp_directory):
        """Test consolidator initialization."""
        assert consolidator.root_directory == temp_directory
        assert isinstance(consolidator.config, ConsolidatorConfig)
        assert hasattr(consolidator, 'loader')
        assert hasattr(consolidator, 'validator')
        assert hasattr(consolidator, 'cleaner')
    
    @patch.object(DataLoader, 'find_excel_files')
    @patch.object(DataLoader, 'load_excel_file')
    def test_consolidate_data_no_files(self, mock_load, mock_find, consolidator):
        """Test consolidation with no files found."""
        mock_find.return_value = []
        
        result = consolidator.consolidate_data()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_save_data_empty_dataframe(self, consolidator, temp_directory):
        """Test saving empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result = consolidator.save_data(empty_df, output_dir=temp_directory)
        
        assert result['csv'] is False
        assert result['excel'] is False
    
    def test_save_data_success(self, consolidator, temp_directory):
        """Test successful data saving."""
        test_df = pd.DataFrame({
            'City': ['pontianak', 'banjarmasin'],
            'Commodities': ['Beras', 'Telur Ayam'],
            'Price': [12000, 25000],
            'Date': pd.date_range('2023-01-01', periods=2)
        })
        
        result = consolidator.save_data(test_df, output_dir=temp_directory)
        
        # At least one format should succeed
        assert result['csv'] is True or result['excel'] is True


class TestConsolidationPipeline:
    """Test the complete consolidation pipeline."""
    
    @pytest.fixture
    def temp_directory(self):
        """Provide temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return ConsolidatorConfig(enable_logging=False)
    
    @pytest.fixture
    def pipeline(self, config, temp_directory):
        """Provide pipeline instance."""
        return ConsolidationPipeline(data_root=temp_directory, config=config)
    
    def test_pipeline_initialization(self, pipeline, temp_directory):
        """Test pipeline initialization."""
        assert pipeline.data_root == temp_directory
        assert isinstance(pipeline.config, ConsolidatorConfig)
        assert hasattr(pipeline, 'consolidator')
    
    def test_validate_data_structure_empty(self, pipeline):
        """Test data validation with empty directory."""
        result = pipeline.validate_data_structure()
        
        assert 'valid_files' in result
        assert 'invalid_files' in result
        assert 'issues' in result
        assert len(result['valid_files']) == 0
    
    def test_get_data_summary(self, pipeline):
        """Test data summary generation."""
        test_df = pd.DataFrame({
            'City': ['pontianak', 'banjarmasin', 'pontianak'],
            'Commodities': ['Beras', 'Telur Ayam', 'Beras'],
            'Price': [12000, 25000, 12500],
            'Date': pd.date_range('2023-01-01', periods=3)
        })
        
        summary = pipeline.get_data_summary(test_df)
        
        assert summary['total_records'] == 3
        assert summary['num_cities'] == 2
        assert summary['num_commodities'] == 2
        assert 'cities' in summary
        assert 'commodities' in summary
        assert 'missing_values' in summary
    
    @patch.object(DataConsolidator, 'consolidate_data')
    def test_run_consolidation_no_save(self, mock_consolidate, pipeline):
        """Test running consolidation without saving."""
        mock_df = pd.DataFrame({
            'City': ['pontianak'],
            'Commodities': ['Beras'],
            'Price': [12000],
            'Date': ['2023-01-01']
        })
        mock_consolidate.return_value = mock_df
        
        result = pipeline.run_consolidation(save_outputs=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_consolidate.assert_called_once()


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_log_level(self):
        """Test handling of invalid log level."""
        config = ConsolidatorConfig(log_level="INVALID")
        # Should not raise an exception, should use default
        assert config.log_level == "INVALID"  # Pydantic allows it, logging will handle
    
    def test_empty_target_commodities(self):
        """Test handling of empty target commodities list."""
        config = ConsolidatorConfig(target_commodities=[])
        assert config.target_commodities == []
    
    def test_invalid_year_range(self):
        """Test handling of invalid year range."""
        config = ConsolidatorConfig(
            year_range_start=2025,
            year_range_end=2020  # End before start
        )
        # Configuration should still be created
        assert config.year_range_start == 2025
        assert config.year_range_end == 2020


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def temp_directory(self):
        """Provide temporary directory with test data structure."""
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Create directory structure
        raw_dir = temp_path / "data" / "raw" / "province" / "kota-pontianak"
        raw_dir.mkdir(parents=True)
        
        # Create a simple test Excel file
        test_data = pd.DataFrame({
            'Komoditas (Rp)': ['Beras', 'Telur Ayam'],
            'Jan-23': [12000, 25000],
            'Feb-23': [12500, 26000]
        })
        
        excel_file = raw_dir / "2023.xlsx"
        test_data.to_excel(excel_file, index=False)
        
        yield temp_path
        shutil.rmtree(temp_dir)
    
    def test_end_to_end_consolidation(self, temp_directory):
        """Test complete end-to-end consolidation process."""
        config = ConsolidatorConfig(
            target_commodities=['Beras', 'Telur Ayam'],
            enable_logging=False
        )
        
        pipeline = ConsolidationPipeline(
            data_root=temp_directory / "data",
            config=config
        )
        
        # Run validation
        validation = pipeline.validate_data_structure()
        assert len(validation['valid_files']) > 0
        
        # Run consolidation
        result = pipeline.run_consolidation(save_outputs=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'City' in result.columns
        assert 'Commodities' in result.columns
        assert 'Price' in result.columns
        assert 'Date' in result.columns


@pytest.mark.parametrize("commodity,expected", [
    ("Beras", True),
    ("Telur Ayam", True), 
    ("Unknown Item", False)
])
def test_commodity_filtering(commodity, expected):
    """Parameterized test for commodity filtering."""
    config = ConsolidatorConfig()
    result = commodity in config.target_commodities
    assert result == expected


@pytest.mark.parametrize("filename,expected_year", [
    ("2023.xlsx", 2023),
    ("data_2022.xlsx", 2022),
    ("file_with_2021_year.xlsx", 2021),
    ("no_year_file.xlsx", None)
])
def test_year_extraction(filename, expected_year):
    """Parameterized test for year extraction."""
    config = ConsolidatorConfig()
    loader = DataLoader(config)
    result = loader._extract_year_from_filename(Path(filename))
    assert result == expected_year


if __name__ == "__main__":
    pytest.main([__file__, "-v"])