"""Core tools for the functionality of basic-deep-learning, including 
encapsulation of matrices and activation function."""

from .matrix import Matrix
from .activations_registry import ActivationFunctionsRegistry

__all__ = ['Matrix', 'ActivationFunctionsRegistry']