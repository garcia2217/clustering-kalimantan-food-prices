"""Pipeline modules for different stages of the food price analysis workflow."""

from .consolidation import ConsolidationPipeline

__all__ = ["ConsolidationPipeline"]

# Future pipelines will be added here as the project grows:
# from .eda import EDAPipeline
# from .clustering import ClusteringPipeline  
# from .analysis import AnalysisPipeline
# 
# __all__ = [
#     "ConsolidationPipeline",
#     "EDAPipeline", 
#     "ClusteringPipeline",
#     "AnalysisPipeline"
# ]
