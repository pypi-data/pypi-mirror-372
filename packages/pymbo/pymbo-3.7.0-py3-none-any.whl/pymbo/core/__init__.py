"""Core Optimization Module.

Contains the main optimization algorithms and control logic.
"""

# Import optimizer from enhanced version when available, fallback to legacy
try:
    from .enhanced_optimizer import create_efficient_optimizer
    from .optimizer import EnhancedMultiObjectiveOptimizer, SimpleParameterTransformer

    ENHANCED_OPTIMIZER_AVAILABLE = True
except ImportError:
    from .optimizer import EnhancedMultiObjectiveOptimizer, SimpleParameterTransformer

    create_efficient_optimizer = None
    ENHANCED_OPTIMIZER_AVAILABLE = False

from .controller import SimpleController

__all__ = [
    "EnhancedMultiObjectiveOptimizer",
    "SimpleController",
    "create_efficient_optimizer",
    "SimpleParameterTransformer",
    "ENHANCED_OPTIMIZER_AVAILABLE",
]