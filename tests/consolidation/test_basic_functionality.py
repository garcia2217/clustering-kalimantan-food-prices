"""Basic functionality tests for the consolidation system."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from clustering_food_prices_kalimantan import (
    ConsolidationPipeline,
    ConsolidatorConfig,
    PathConfig
)


def test_imports():
    """Test that all main components can be imported successfully."""
    from clustering_food_prices_kalimantan import (
        ConsolidationPipeline,
        ConsolidatorConfig,
        PathConfig,
        DataValidator,
        DataLoader,
        DataCleaner,
        DataConsolidator
    )
    
    # If we get here without import errors, the test passes
    assert True


def test_config_creation():
    """Test that configuration objects can be created with default values."""
    config = ConsolidatorConfig()
    paths = PathConfig()
    
    assert config is not None
    assert paths is not None
    assert len(config.target_commodities) > 0
    assert config.file_pattern == "*.xlsx"


def test_pipeline_creation():
    """Test that ConsolidationPipeline can be created."""
    pipeline = ConsolidationPipeline()
    
    assert pipeline is not None
    assert hasattr(pipeline, 'config')
    assert hasattr(pipeline, 'paths')
    assert hasattr(pipeline, 'consolidator')


def test_custom_config():
    """Test creating pipeline with custom configuration."""
    custom_config = ConsolidatorConfig(
        target_commodities=['Beras', 'Telur Ayam'],
        log_level='WARNING',
        enable_logging=False
    )
    
    pipeline = ConsolidationPipeline(config=custom_config)
    
    assert pipeline.config.target_commodities == ['Beras', 'Telur Ayam']
    assert pipeline.config.log_level == 'WARNING'
    assert pipeline.config.enable_logging is False


def test_validation_empty_directory():
    """Test validation with empty directory structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        config = ConsolidatorConfig(enable_logging=False)
        pipeline = ConsolidationPipeline(
            data_root=temp_path,
            config=config
        )
        
        result = pipeline.validate_data_structure()
        
        assert 'valid_files' in result
        assert 'invalid_files' in result
        assert 'issues' in result
        assert len(result['valid_files']) == 0


def test_data_summary_with_empty_dataframe():
    """Test data summary generation with empty DataFrame."""
    pipeline = ConsolidationPipeline()
    empty_df = pd.DataFrame()
    
    summary = pipeline.get_data_summary(empty_df)
    
    # Empty DataFrame returns empty dict
    assert summary == {}
    assert len(summary) == 0


def test_data_summary_with_sample_data():
    """Test data summary generation with sample data."""
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


def test_path_configuration():
    """Test path configuration and directory creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        paths = PathConfig(
            data_root=temp_path / "data",
            raw_data_dir=temp_path / "data" / "raw",
            processed_data_dir=temp_path / "data" / "processed",
            logs_dir=temp_path / "logs"
        )
        
        # Test directory creation
        paths.create_directories()
        
        assert (temp_path / "data").exists()
        assert (temp_path / "data" / "raw").exists()
        assert (temp_path / "data" / "processed").exists()
        assert (temp_path / "logs").exists()


def test_consolidation_with_no_data():
    """Test consolidation process when no data files are available."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        config = ConsolidatorConfig(enable_logging=False)
        pipeline = ConsolidationPipeline(
            data_root=temp_path,
            config=config
        )
        
        # This should return an empty DataFrame without errors
        result = pipeline.run_consolidation(save_outputs=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


@pytest.mark.parametrize("commodity", [
    "Beras", 
    "Telur Ayam", 
    "Daging Ayam", 
    "Bawang Merah", 
    "Bawang Putih"
])
def test_default_commodities(commodity):
    """Test that all default commodities are included in configuration."""
    config = ConsolidatorConfig()
    assert commodity in config.target_commodities


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_log_levels(log_level):
    """Test that different log levels can be set."""
    config = ConsolidatorConfig(log_level=log_level)
    assert config.log_level == log_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])