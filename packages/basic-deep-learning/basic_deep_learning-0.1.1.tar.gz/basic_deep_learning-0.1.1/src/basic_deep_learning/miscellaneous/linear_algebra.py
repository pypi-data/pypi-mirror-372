"""Module containing the LinearAlgebraUtils class."""
class LinearAlgebraUtils:
    """Utilities from linear algebra."""
    @staticmethod
    def dot(u: list[int|float],
            v: list[int|float]) -> int|float:
        """Takes two lists as arguments, treats them as vectors and returns their dot product."""
        if len(u) == 0 or len(v) == 0:
            raise ValueError("Cannot pass empty vectors.")
        if len(u) != len(v):
            raise ValueError("Cannot pass vectors of different dimensions.")
        return sum(x*y for x, y in zip(u,v))