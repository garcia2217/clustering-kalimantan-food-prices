"""Working tests for the consolidation system - verified to pass."""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path

from clustering_food_prices_kalimantan import (
    ConsolidationPipeline,
    ConsolidatorConfig,
    PathConfig
)


class TestWorkingFunctionality:
    """Tests that are verified to work with the current implementation."""
    
    def test_import_all_components(self):
        """Test that all components can be imported."""
        from clustering_food_prices_kalimantan import (
            ConsolidationPipeline,
            ConsolidatorConfig,
            PathConfig,
            DataValidator,
            DataLoader,
            DataCleaner,
            DataConsolidator
        )
        assert True  # If we get here, imports worked
    
    def test_config_creation_and_defaults(self):
        """Test configuration creation with default values."""
        config = ConsolidatorConfig()
        
        assert config is not None
        assert len(config.target_commodities) == 5
        assert "Beras" in config.target_commodities
        assert "Telur Ayam" in config.target_commodities
        assert config.file_pattern == "*.xlsx"
        assert config.log_level == "INFO"
        assert config.enable_logging is True
    
    def test_path_config_defaults(self):
        """Test path configuration defaults."""
        paths = PathConfig()
        
        assert paths.data_root == Path("data")
        assert paths.raw_data_dir == Path("data/raw")
        assert paths.processed_data_dir == Path("data/processed")
        assert paths.logs_dir == Path("logs")
    
    def test_path_config_directory_creation(self):
        """Test that path config can create directories."""
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
    
    def test_pipeline_creation_default(self):
        """Test pipeline creation with defaults."""
        pipeline = ConsolidationPipeline()
        
        assert pipeline is not None
        assert hasattr(pipeline, 'config')
        assert hasattr(pipeline, 'paths')
        assert hasattr(pipeline, 'consolidator')
        assert hasattr(pipeline, 'data_root')
    
    def test_pipeline_creation_custom_config(self):
        """Test pipeline creation with custom config."""
        custom_config = ConsolidatorConfig(
            target_commodities=['Beras', 'Telur Ayam'],
            log_level='WARNING',
            enable_logging=False
        )
        
        pipeline = ConsolidationPipeline(config=custom_config)
        
        assert pipeline.config.target_commodities == ['Beras', 'Telur Ayam']
        assert pipeline.config.log_level == 'WARNING'
        assert pipeline.config.enable_logging is False
    
    def test_validate_data_structure_empty_directory(self):
        """Test validation with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            config = ConsolidatorConfig(enable_logging=False)
            pipeline = ConsolidationPipeline(
                data_root=temp_path,
                config=config
            )
            
            result = pipeline.validate_data_structure()
            
            assert isinstance(result, dict)
            assert 'valid_files' in result
            assert 'invalid_files' in result
            assert 'issues' in result
            assert len(result['valid_files']) == 0
    
    def test_data_summary_empty_dataframe(self):
        """Test data summary with empty DataFrame."""
        pipeline = ConsolidationPipeline()
        empty_df = pd.DataFrame()
        
        summary = pipeline.get_data_summary(empty_df)
        
        # Empty DataFrame returns empty dict
        assert summary == {}
    
    def test_data_summary_with_data(self):
        """Test data summary with actual data."""
        pipeline = ConsolidationPipeline()
        
        sample_df = pd.DataFrame({
            'City': ['pontianak', 'banjarmasin', 'pontianak'],
            'Commodities': ['Beras', 'Telur Ayam', 'Beras'],
            'Price': [12000, 25000, 12500],
            'Date': pd.date_range('2023-01-01', periods=3)
        })
        
        summary = pipeline.get_data_summary(sample_df)
        
        assert summary['total_records'] == 3
        assert summary['num_cities'] == 2
        assert summary['num_commodities'] == 2
        assert 'pontianak' in summary['cities']
        assert 'banjarmasin' in summary['cities']
        assert 'Beras' in summary['commodities']
        assert 'Telur Ayam' in summary['commodities']
    
    def test_consolidation_no_data_files(self):
        """Test consolidation when no data files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            config = ConsolidatorConfig(enable_logging=False)
            pipeline = ConsolidationPipeline(
                data_root=temp_path,
                config=config
            )
            
            # Should return empty DataFrame without errors
            result = pipeline.run_consolidation(save_outputs=False)
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_custom_commodities_config(self):
        """Test configuration with custom commodities."""
        custom_commodities = ['Beras', 'Gula', 'Minyak']
        config = ConsolidatorConfig(target_commodities=custom_commodities)
        
        assert config.target_commodities == custom_commodities
        assert len(config.target_commodities) == 3
    
    def test_custom_year_filtering(self):
        """Test configuration with year filtering."""
        config = ConsolidatorConfig(
            target_years=[2022, 2023, 2024],
            year_range_start=2020,
            year_range_end=2024
        )
        
        assert config.target_years == [2022, 2023, 2024]
        assert config.year_range_start == 2020
        assert config.year_range_end == 2024
    
    def test_custom_city_filtering(self):
        """Test configuration with city filtering."""
        custom_cities = ['kota-pontianak', 'kota-banjarmasin']
        config = ConsolidatorConfig(target_cities=custom_cities)
        
        assert config.target_cities == custom_cities
        assert len(config.target_cities) == 2


class TestEndToEndWorkflow:
    """Test complete workflows that we know work."""
    
    def test_complete_workflow_no_data(self):
        """Test complete workflow with no data files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 1. Create configuration
            config = ConsolidatorConfig(
                target_commodities=['Beras', 'Telur Ayam'],
                enable_logging=False
            )
            
            # 2. Create pipeline
            pipeline = ConsolidationPipeline(
                data_root=temp_path,
                config=config
            )
            
            # 3. Validate structure
            validation = pipeline.validate_data_structure()
            assert len(validation['valid_files']) == 0
            
            # 4. Run consolidation (should handle no files gracefully)
            result = pipeline.run_consolidation(save_outputs=False)
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            
            # 5. Get summary
            summary = pipeline.get_data_summary(result)
            assert summary == {}  # Empty for empty DataFrame
    
    def test_logging_directory_configuration(self):
        """Test that logging directory is configured correctly."""
        paths = PathConfig()
        
        # Verify logs directory is configured
        assert paths.logs_dir == Path("logs")
        
        # Test directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_paths = PathConfig(logs_dir=temp_path / "logs")
            test_paths.create_directories()
            
            assert (temp_path / "logs").exists()


@pytest.mark.parametrize("commodity", [
    "Beras", 
    "Telur Ayam", 
    "Daging Ayam", 
    "Bawang Merah", 
    "Bawang Putih"
])
def test_default_commodities_parametrized(commodity):
    """Test that all default commodities are present."""
    config = ConsolidatorConfig()
    assert commodity in config.target_commodities


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_log_levels_parametrized(log_level):
    """Test that different log levels can be configured."""
    config = ConsolidatorConfig(log_level=log_level)
    assert config.log_level == log_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])