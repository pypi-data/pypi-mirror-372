# src/contrast_calculus/category.py
import numpy as np

class FusionCategory:
    """
    Represents a pointed fusion category, defined by a finite group G
    and a 3-cocycle alpha on that group.
    """

    def __init__(self, group_elements, cocycle_function):
        """
        Initializes the fusion category.

        Args:
            group_elements (list): A list of the elements of the group G.
            cocycle_function (function): A function alpha(g1, g2, g3) that returns a phase.
        """
        if not callable(cocycle_function):
            raise TypeError("cocycle_function must be a callable function.")

        self.objects = set(group_elements)
        self.cocycle = cocycle_function
        print("Fusion Category initialized successfully.")

    def __repr__(self):
        return f"FusionCategory(based on a group with {len(self.objects)} elements)"

    def associator(self, g1, g2, g3):
        """
        The F-move (associator) for a pointed category is directly given by the 3-cocycle.
        It describes how to re-bracket a product of three objects.
        (g1 ⊗ g2) ⊗ g3  -->  g1 ⊗ (g2 ⊗ g3)
        """
        if not all(g in self.objects for g in [g1, g2, g3]):
            raise ValueError("All elements must be objects in the category.")

        return self.cocycle(g1, g2, g3)

