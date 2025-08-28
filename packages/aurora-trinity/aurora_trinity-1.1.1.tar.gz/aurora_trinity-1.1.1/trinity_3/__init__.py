
"""
Aurora Trinity-3 Package
========================

Fractal, Ethical, Free Electronic Intelligence
"""

from .core import (
    FractalTensor,
    Evolver,
    Extender,
    FractalKnowledgeBase,
    Armonizador,
    TensorPoolManager,
    Trigate,
    TernaryLogic,
    Transcender,
    pattern0_create_fractal_cluster
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Aurora Alliance"
__license__ = "Apache-2.0 + CC-BY-4.0"

def get_model_info():
    """Get Aurora Trinity-3 model information."""
    return {
        "name": "Aurora Trinity-3",
        "version": __version__,
        "description": "Fractal, Ethical, Free Electronic Intelligence",
        "architecture": "Ternary Logic + Fractal Tensors",
        "author": __author__,
        "license": __license__,
        "capabilities": [
            "Ternary logic operations",
            "Fractal tensor synthesis", 
            "Knowledge base management",
            "Ethical harmonization",
            "Symbolic reasoning"
        ]
    }

# Main exports
__all__ = [
    'FractalTensor',
    'Trigate', 
    'TernaryLogic',
    'Evolver',
    'Extender', 
    'FractalKnowledgeBase',
    'Armonizador',
    'TensorPoolManager',
    'Transcender',
    'pattern0_create_fractal_cluster',
    'get_model_info',
    '__version__'
]
