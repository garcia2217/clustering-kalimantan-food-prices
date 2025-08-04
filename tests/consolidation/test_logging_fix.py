"""Test the logging directory fix."""

import pytest
import tempfile
import shutil
from pathlib import Path

from clustering_food_prices_kalimantan import ConsolidatorConfig, PathConfig
from clustering_food_prices_kalimantan.data.consolidator import DataConsolidator


def test_logging_uses_logs_directory():
    """Test that logging files are created in the logs directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a config with logging enabled
        config = ConsolidatorConfig(
            enable_logging=True,
            log_level="INFO"
        )
        
        # Change working directory to temp directory for this test
        import os
        original_cwd = os.getcwd()
        
        try:
            os.chdir(temp_path)
            
            # Create consolidator (this should set up logging)
            consolidator = DataConsolidator(
                root_directory=temp_path / "data",
                config=config
            )
            
            # Check that logs directory was created
            logs_dir = temp_path / "logs"
            assert logs_dir.exists(), "Logs directory should be created"
            
            # Check that log file exists in logs directory
            log_file = logs_dir / "food_price_consolidation.log"
            assert log_file.exists(), "Log file should be created in logs directory"
            
            # Verify the log file is not in the root directory
            root_log_file = temp_path / "food_price_consolidation.log"
            assert not root_log_file.exists(), "Log file should NOT be in root directory"
            
        finally:
            # Restore original working directory
            os.chdir(original_cwd)


def test_path_config_logs_directory():
    """Test that PathConfig properly configures logs directory."""
    paths = PathConfig()
    
    # Default logs directory should be 'logs'
    assert paths.logs_dir == Path("logs")
    
    # Test with custom logs directory
    custom_paths = PathConfig(logs_dir=Path("custom_logs"))
    assert custom_paths.logs_dir == Path("custom_logs")


def test_create_directories_includes_logs():
    """Test that create_directories method creates logs directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        paths = PathConfig(
            data_root=temp_path / "data",
            raw_data_dir=temp_path / "data" / "raw",
            processed_data_dir=temp_path / "data" / "processed",
            logs_dir=temp_path / "logs"
        )
        
        # Create all directories
        paths.create_directories()
        
        # Verify logs directory was created
        assert (temp_path / "logs").exists()
        assert (temp_path / "logs").is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])