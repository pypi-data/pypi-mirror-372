"""
The Python GSV interface.

.. toctree::
   :hidden:

   self

Subpackages
===========

Built-in and tools and functions.

.. autosummary::
   :toctree: api

   GSVRetriever
"""

try:
    from ._version import __version__
except ModuleNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0.dev0"

from .retriever import GSVRetriever

__all__ = ["__version__"]
__all__ += ["GSVRetriever"]
