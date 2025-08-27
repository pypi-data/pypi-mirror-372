"""
Empirikos: Python interface to Empirikos.jl for empirical Bayes methods.
"""

from .epb_ttest import epb_ttest, EPBTTestResult

__version__ = "0.1.0"
__all__ = ["epb_ttest", "EPBTTestResult"]