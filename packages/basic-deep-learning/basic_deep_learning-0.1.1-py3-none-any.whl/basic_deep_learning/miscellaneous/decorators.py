"""Module containing the extend_to_matrices decorator."""
def extend_to_matrices(f):
    """Decorator for real-valued functions to extend them for Matrix instances component-wise."""
    def wrapper(M):
        from ..functionality.matrix import Matrix
        if isinstance(M, Matrix):
            return Matrix([wrapper(R) for R in M.matrix])
        elif isinstance(M, list):
            return [wrapper(x) for x in M]
        else:
            return f(M)
    return wrapper