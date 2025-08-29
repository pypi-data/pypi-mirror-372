"""
torch_swan
----------

swan - A PyTorch implementation of the classic "Swan" algorithm.
"""

from .swan import Swan

__all__ = ["Swan"]
__version__ = "0.0.1"

# Optional convenience function
def sing() -> str:
    return Swan().sing()

