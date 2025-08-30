# src/contrast_calculus/algebra.py

class Braid:
    """Represents an element of a braid group B_n."""

    def __init__(self, generators):
        # We store the braid as a list of integers, e.g., [1, 2, -1] for sigma_1 * sigma_2 * sigma_1^-1
        self.generators = list(generators)

    def __repr__(self):
        """Provides a developer-friendly representation of the braid."""
        return f"Braid({self.generators})"

    def __mul__(self, other):
        """Defines the multiplication of two braids (concatenation)."""
        if not isinstance(other, Braid):
            return NotImplemented
        return Braid(self.generators + other.generators)

    def inverse(self):
        """Computes the inverse of the braid."""
        inv_gens = [-g for g in reversed(self.generators)]
        return Braid(inv_gens)
