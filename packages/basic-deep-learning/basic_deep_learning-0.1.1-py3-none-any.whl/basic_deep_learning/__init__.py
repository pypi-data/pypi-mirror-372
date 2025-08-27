"""Simple module for creating deep learning tools, with its own linear algebra and matrices utilities."""
from .functionality import Matrix, ActivationFunctionsRegistry
from .miscellaneous import extend_to_matrices, LinearAlgebraUtils
from .models import MultiLayerPerceptron

__version__ = "0.1.0"
__author__ = "Diaa Eddine ZAINI <zainidiaaeddine@gmail.com>"

__all__ = [
    'Matrix',
    'ActivationFunctionsRegistry',
    'extend_to_matrices',
    'LinearAlgebraUtils',
    'MultiLayerPerceptron'
]