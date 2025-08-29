# src/contrast_calculus/cocycle.py
import numpy as np

def get_z2_cocycle():
    """
    Returns a function representing a non-trivial 3-cocycle for the group Z_2 = {0, 1}.

    This cocycle defines the associativity constraints in the Z_2 pointed fusion category,
    leading to interesting physical models like the Toric Code.

    The value is non-trivial only for alpha(1, 1, 1) = -1.

    Returns:
        function: A callable function alpha(g1, g2, g3) that returns a phase.
    """
    def alpha(g1, g2, g3):
        # Ensure elements are from Z_2
        if not all(g in [0, 1] for g in [g1, g2, g3]):
            raise ValueError("Elements must be in Z_2 ({0, 1}).")

        # The cocycle is non-trivial only for the case (1, 1, 1)
        if g1 == 1 and g2 == 1 and g3 == 1:
            return -1.0
        else:
            return 1.0

    return alpha


