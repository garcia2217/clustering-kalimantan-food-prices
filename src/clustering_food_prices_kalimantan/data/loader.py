"""Data loading utilities."""

import logging
import pandas as pd
from pathlib import Path
from typing import List, Optional

from ..config.settings import ConsolidatorConfig


class DataLoader:
    """Handles loading data from Excel files."""
    
    def __init__(self, config: ConsolidatorConfig, logger: Optional[logging.Logger] = None):
        """Initialize loader with configuration."""
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    def load_excel_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load a single Excel file.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            DataFrame or None if loading failed
        """
        try:
            df = pd.read_excel(file_path)
            self.logger.debug(f"Successfully loaded {file_path.name}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load {file_path.name}: {str(e)}")
            return None
    
    def find_excel_files(self, root_directory: Path) -> List[Path]:
        """
        Find all Excel files in the directory structure, filtered by criteria.
        
        Args:
            root_directory: Root directory to search
            
        Returns:
            List of Excel file paths
        """
        if not root_directory.exists():
            raise FileNotFoundError(f"Directory not found: {root_directory}")
            
        # Get all Excel files first
        all_excel_files = list(root_directory.rglob(self.config.file_pattern))
        
        # Apply filtering
        filtered_files = self._filter_files_by_criteria(all_excel_files)
        
        if not filtered_files:
            self.logger.warning(f"No Excel files found matching criteria in {root_directory}")
            self._log_filtering_info()
        else:
            self.logger.info(f"Found {len(filtered_files)} files after filtering (out of {len(all_excel_files)} total)")
            
        return filtered_files
    
    def _filter_files_by_criteria(self, files: List[Path]) -> List[Path]:
        """
        Filter files based on year and city criteria.
        
        Args:
            files: List of file paths to filter
            
        Returns:
            Filtered list of file paths
        """
        filtered_files = []
        
        for file_path in files:
            # Check year filtering
            if not self._should_process_year(file_path):
                continue
                
            # Check city filtering  
            if not self._should_process_city(file_path):
                continue
                
            filtered_files.append(file_path)
            
        return filtered_files
    
    def _should_process_year(self, file_path: Path) -> bool:
        """
        Check if the file should be processed based on year filtering.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            True if file should be processed, False otherwise
        """
        # Extract year from filename (e.g., "2023.xlsx" -> 2023)
        try:
            year_str = file_path.stem  # Gets filename without extension
            year = int(year_str)
        except ValueError:
            # If filename is not a year, include it (might be older format)
            self.logger.debug(f"Could not extract year from filename: {file_path.name}")
            return True
        
        # Check specific target years first
        if self.config.target_years is not None:
            return year in self.config.target_years
        
        # Check year range
        if self.config.year_range_start is not None or self.config.year_range_end is not None:
            start_year = self.config.year_range_start or float('-inf')
            end_year = self.config.year_range_end or float('inf')
            return start_year <= year <= end_year
        
        # No year filtering configured, include all
        return True
    
    def _should_process_city(self, file_path: Path) -> bool:
        """
        Check if the file should be processed based on city filtering.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            True if file should be processed, False otherwise
        """
        if self.config.target_cities is None:
            return True  # No city filtering, include all
        
        # Extract city name from path (second to last directory)
        city_name = self._extract_city_from_path(file_path)
        return city_name in self.config.target_cities
    
    def _extract_city_from_path(self, file_path: Path) -> str:
        """
        Extract city name from file path.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            City name extracted from path
        """
        return file_path.parts[-2]
    
    def _log_filtering_info(self) -> None:
        """Log information about current filtering criteria."""
        filters = []
        
        if self.config.target_years is not None:
            filters.append(f"Years: {self.config.target_years}")
        elif self.config.year_range_start is not None or self.config.year_range_end is not None:
            start = self.config.year_range_start or "any"
            end = self.config.year_range_end or "any" 
            filters.append(f"Year range: {start} to {end}")
        
        if self.config.target_cities is not None:
            filters.append(f"Cities: {self.config.target_cities}")
        
        if filters:
            self.logger.info(f"Applied filters: {', '.join(filters)}")
        else:
            self.logger.info("No filtering applied - processing all available files")
