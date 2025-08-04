"""Data validation utilities."""

import pandas as pd
from pathlib import Path
from typing import List, Tuple

from ..config.settings import ConsolidatorConfig


class DataValidator:
    """Validates data quality and structure."""
    
    def __init__(self, config: ConsolidatorConfig):
        """Initialize validator with configuration."""
        self.config = config
    
    def validate_dataframe(self, df: pd.DataFrame, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame structure and content.
        
        Args:
            df: DataFrame to validate
            file_path: Source file path for error reporting
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if df.empty:
            issues.append(f"Empty DataFrame from {file_path.name}")
            
        if self.config.original_commodity_col not in df.columns:
            issues.append(f"Missing '{self.config.original_commodity_col}' column in {file_path.name}")
            
        # Check for minimum expected columns (commodity + at least one date column)
        if len(df.columns) < self.config.min_expected_columns:
            issues.append(f"Insufficient columns in {file_path.name}")
            
        return len(issues) == 0, issues
    
    def validate_file_path(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate file path and accessibility.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not file_path.exists():
            issues.append(f"File does not exist: {file_path}")
        
        if not file_path.is_file():
            issues.append(f"Path is not a file: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            issues.append(f"File is not an Excel file: {file_path}")
            
        return len(issues) == 0, issues
