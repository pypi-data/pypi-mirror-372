"""Detectors module for OpenEVLN safety pipeline"""

from .regex_detector import RegexDetector
from .behavior_detector import BehaviorDetector

try:
    from .embedding_detector import EmbeddingDetector
except ImportError:
    EmbeddingDetector = None

try:
    from .classifier import Classifier
except ImportError:
    Classifier = None

__all__ = [
    "RegexDetector",
    "BehaviorDetector",
    "EmbeddingDetector",
    "Classifier",
]
