"""
Julia integration helpers for Empirikos.
"""

import os
import warnings
from typing import Optional

# Set Julia environment variables for better compatibility
os.environ.setdefault("PYTHON_JULIACALL_HANDLE_SIGNALS", "yes")
os.environ.setdefault("PYTHON_JULIACALL_THREADS", "auto")

# Global variables for Julia objects
_jl = None
_empirikos_loaded = False


def _get_julia_main():
    """Get Julia Main module, initializing if necessary."""
    global _jl
    if _jl is None:
        try:
            from juliacall import Main as jl
            _jl = jl
        except ImportError as e:
            raise ImportError(
                "juliacall is required but not installed. "
                "Install with: pip install juliacall"
            ) from e
    return _jl


def _ensure_empirikos_loaded():
    """Ensure Empirikos.jl and required packages are loaded."""
    global _empirikos_loaded
    if _empirikos_loaded:
        return
    
    jl = _get_julia_main()
    
    # Check Julia version
    julia_version = jl.seval("VERSION")
    if julia_version < jl.seval("v\"1.10\""):
        warnings.warn(
            f"Julia version {julia_version} detected. "
            "Empirikos Python package requires Julia 1.10+. "
            "Some features may not work correctly."
        )
    
    try:
        # Install packages if needed
        jl.seval('using Pkg')
        
        # Install Empirikos.jl from Julia registry
        try:
            jl.seval('using Empirikos')
        except Exception:
            jl.seval('Pkg.add("Empirikos")')
            jl.seval('using Empirikos')
        
        # Install optimization packages
        required_packages = ["MultipleTesting", "Hypatia", "MosekTools"]
        for pkg in required_packages:
            try:
                jl.seval(f'using {pkg}')
            except Exception:
                jl.seval(f'Pkg.add("{pkg}")')
                jl.seval(f'using {pkg}')
        
        _empirikos_loaded = True
        
    except Exception as e:
        raise RuntimeError(
            f"Failed to load required Julia packages: {e}\n"
            "Make sure Julia 1.10+ is installed and accessible."
        ) from e


def get_solver_optimizer(solver: str):
    """Get the appropriate solver optimizer object."""
    _ensure_empirikos_loaded()
    jl = _get_julia_main()
    
    if solver.lower() == "hypatia":
        return jl.seval("Hypatia.Optimizer")
    elif solver.lower() == "mosek":
        return jl.seval("Mosek.Optimizer")
    else:
        raise ValueError(f"Unsupported solver: {solver}. Options: 'hypatia', 'mosek'")


