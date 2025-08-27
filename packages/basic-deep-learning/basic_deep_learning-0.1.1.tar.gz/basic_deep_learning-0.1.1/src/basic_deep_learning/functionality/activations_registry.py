"""Module containing the ActivationFunctionsRegistry class."""
import math
from .matrix import Matrix
from ..miscellaneous.decorators import extend_to_matrices

class ActivationFunctionsRegistry:
    """Registry for the most popular activation functions and their deriviatives."""
    @staticmethod
    @extend_to_matrices
    def sigmoid(Z):
        return 1/(1+math.exp(-Z))
    
    @staticmethod
    @extend_to_matrices
    def sigmoid_prime(Z):
        s = ActivationFunctionsRegistry.sigmoid(Z)
        return s * (1 - s)
    
    @staticmethod
    @extend_to_matrices
    def ReLU(Z):
        return max(0, Z)
    
    @staticmethod
    @extend_to_matrices
    def ReLU_prime(Z):
        return float(Z > 0)
    
    @staticmethod
    @extend_to_matrices
    def linear(Z):
        return Z
    
    @staticmethod
    @extend_to_matrices
    def linear_prime(Z):
        return 1
    
    @staticmethod
    @extend_to_matrices
    def tanh(Z):
        return math.tanh(Z)
    
    @staticmethod
    @extend_to_matrices
    def tanh_prime(Z):
        return 1 - (math.tanh(Z))**2
    
    @staticmethod
    def softmax(M: Matrix): #Turns a column vector into a probability distribution.
        if M.format[1] != 1:
            raise ValueError("Must insert a Matrix instance whose format is that of a column vector.")
        values = M.get_column(1)
        max_val = max(values)
        exponents = [math.exp(v - max_val) for v in values]
        total = sum(exponents)
        softmaxed_matrix = Matrix.zero(*M.format)
        for i, exp_val in enumerate(exponents, start=1):
            softmaxed_matrix.set_entry(exp_val / total, i, 1)
        return softmaxed_matrix
    
    Activations = {
        'sigmoid': (sigmoid, sigmoid_prime),
        'ReLU': (ReLU, ReLU_prime),
        'linear': (linear, linear_prime),
        'tanh': (tanh, tanh_prime)
    }