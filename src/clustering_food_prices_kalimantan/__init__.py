"""Food Price Data Consolidation and Clustering Analysis for Kalimantan.

This package provides tools for consolidating food price data from multiple Excel files
across different cities in Kalimantan and preparing it for clustering analysis.

Main components:
- ConsolidationPipeline: High-level interface for data consolidation
- DataConsolidator: Core consolidation orchestrator
- Data processing modules: DataValidator, DataLoader, DataCleaner
- Configuration: ConsolidatorConfig, PathConfig

Example usage:
    from clustering_food_prices_kalimantan import ConsolidationPipeline
    
    # Simple consolidation
    pipeline = ConsolidationPipeline()
    consolidated_data = pipeline.run_consolidation()
    
    # Custom configuration
    from clustering_food_prices_kalimantan import ConsolidatorConfig
    
    config = ConsolidatorConfig(
        target_commodities=['Beras', 'Telur Ayam'],
        target_years=[2022, 2023, 2024]
    )
    
    pipeline = ConsolidationPipeline(config=config)
    consolidated_data = pipeline.run_consolidation()
"""

from .pipelines import ConsolidationPipeline
from .data import DataConsolidator, DataValidator, DataLoader, DataCleaner
from .config.settings import ConsolidatorConfig, PathConfig, config, paths

__version__ = "0.1.0"
__author__ = "garcia"
__email__ = "emmanoelgarsia@gmail.com"

__all__ = [
    # Main interfaces
    "ConsolidationPipeline",
    "DataConsolidator",
    
    # Data processing components
    "DataValidator", 
    "DataLoader", 
    "DataCleaner",
    
    # Configuration
    "ConsolidatorConfig",
    "PathConfig",
    "config",
    "paths",
]

# Package metadata
__title__ = "clustering-food-prices-kalimantan"
__description__ = "Food price data consolidator and clustering analyzer for Kalimantan cities"
__keywords__ = ["data-analysis", "food-prices", "clustering", "indonesia", "data-consolidation"]
