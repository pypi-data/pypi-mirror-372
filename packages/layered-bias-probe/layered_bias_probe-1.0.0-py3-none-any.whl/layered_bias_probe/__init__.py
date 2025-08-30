"""
Layered Bias Probe - A comprehensive toolkit for layer-wise bias analysis in language models.

This package provides tools for:
- Layer-wise bias analysis using WEAT methodology
- Fine-tuning with bias tracking
- Multi-language and multi-model support
- Results analysis and visualization
"""

__version__ = "1.0.0"
__author__ = "DebK"
__email__ = "your.email@example.com"

from .core.bias_probe import BiasProbe
from .core.fine_tuner import FineTuner
from .core.batch_processor import BatchProcessor
from .core.results_analyzer import ResultsAnalyzer
from .utils.weat_category import WEATCategory
from .utils.model_manager import ModelManager
from .utils.weathub_loader import WEATHubLoader
from .utils.embedding_extractor import LayerEmbeddingExtractor
from .utils.bias_quantifier import BiasQuantifier

__all__ = [
    "BiasProbe",
    "FineTuner", 
    "BatchProcessor",
    "ResultsAnalyzer",
    "WEATCategory",
    "ModelManager",
    "WEATHubLoader",
    "LayerEmbeddingExtractor",
    "BiasQuantifier",
]
