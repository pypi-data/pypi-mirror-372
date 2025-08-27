"""
PyMBO - Python Multi-objective Bayesian Optimization

A comprehensive multi-objective Bayesian optimization framework with advanced visualization
and screening capabilities.

Modules:
    core: Core optimization algorithms and controllers
    gui: Graphical user interface components
    utils: Utility functions for plotting, reporting, and scientific calculations
    screening: SGLBO screening optimization module
"""

__version__ = "3.7.0"
__author__ = "Jakub Jagielski"

# Lazy imports to avoid loading heavy dependencies unless actually needed
# Only import when accessed, not at module load time

def __getattr__(name):
    """Lazy loading of heavy modules."""
    if name == "EnhancedMultiObjectiveOptimizer":
        from .core.optimizer import EnhancedMultiObjectiveOptimizer
        return EnhancedMultiObjectiveOptimizer
    elif name == "SimpleController":
        from .core.controller import SimpleController
        return SimpleController
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "EnhancedMultiObjectiveOptimizer",
    "SimpleController",
]