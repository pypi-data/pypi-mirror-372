"""
Hypervolume Calculator - Legacy Compatibility Wrapper

DEPRECATED: This module is now a compatibility wrapper around the unified
hypervolume calculation system in pymbo.utils.unified_hypervolume.

For new code, please use:
    from pymbo.utils.unified_hypervolume import UnifiedHypervolumeCalculator

This wrapper maintains backward compatibility with existing code.
"""

import logging
import warnings
from typing import Any, Dict, List, Optional

import numpy as np
import torch

# Import the unified hypervolume calculator
from ..utils.unified_hypervolume import (
    UnifiedHypervolumeCalculator, 
    HypervolumeConfig,
    get_hypervolume_calculator
)

logger = logging.getLogger(__name__)


class HypervolumeCalculator:
    """
    DEPRECATED: Legacy wrapper around UnifiedHypervolumeCalculator.
    
    This class is maintained for backward compatibility. New code should use
    UnifiedHypervolumeCalculator directly.
    """
    
    def __init__(self, device: torch.device = None, dtype: torch.dtype = torch.double):
        """
        Initialize the hypervolume calculator.
        
        Args:
            device: PyTorch device for computations
            dtype: Data type for tensor operations
        """
        warnings.warn(
            "HypervolumeCalculator is deprecated. Use UnifiedHypervolumeCalculator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Create unified calculator with appropriate config
        config = HypervolumeConfig(
            use_gpu=(device is None or device.type != "cpu"),
            cache_results=True
        )
        self._unified_calculator = UnifiedHypervolumeCalculator(config)
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype
        
        logger.info(f"HypervolumeCalculator (legacy) initialized, using unified calculator")
    
    def calculate_adaptive_reference_point(self, clean_Y: torch.Tensor) -> torch.Tensor:
        """Legacy method: Calculate adaptive reference point."""
        points_np = clean_Y.detach().cpu().numpy() if isinstance(clean_Y, torch.Tensor) else clean_Y
        ref_point_np = self._unified_calculator._calculate_reference_point(points_np)
        return torch.tensor(ref_point_np, dtype=self.dtype, device=self.device)
    
    def calculate_hypervolume(self, train_Y: torch.Tensor, objective_names: List[str]) -> Dict[str, float]:
        """Legacy method: Calculate hypervolume using unified calculator."""
        try:
            result = self._unified_calculator.calculate_hypervolume(train_Y, objective_names)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error in legacy calculate_hypervolume: {e}")
            return {
                "raw_hypervolume": 0.0,
                "normalized_hypervolume": 0.0,
                "reference_point_adaptive": True,
                "data_points_used": 0,
            }
    
    def check_hypervolume_convergence(
        self, 
        iteration_history: List[Dict[str, Any]], 
        window_size: int = 5, 
        threshold: float = 0.01, 
        use_normalized: bool = True
    ) -> Dict[str, Any]:
        """Legacy method: Check hypervolume convergence."""
        # Keep original convergence logic for compatibility
        convergence_result = {
            "converged": False,
            "progress_stagnant": False,
            "iterations_stable": 0,
            "relative_improvement": 0.0,
            "recommendation": "continue",
            "confidence": "low",
        }

        try:
            if len(iteration_history) < window_size:
                convergence_result["recommendation"] = "continue - insufficient data"
                return convergence_result

            # Extract hypervolume values from recent iterations
            hv_key = "normalized_hypervolume" if use_normalized else "hypervolume"

            recent_hvs = []
            for iteration in iteration_history[-window_size:]:
                hv_value = iteration.get("hypervolume", 0.0)
                if isinstance(hv_value, dict):
                    recent_hvs.append(hv_value.get(hv_key, 0.0))
                else:
                    recent_hvs.append(hv_value)

            if not recent_hvs or all(hv == 0.0 for hv in recent_hvs):
                convergence_result["recommendation"] = "continue - no valid hypervolume data"
                return convergence_result

            # Calculate relative improvement
            max_hv = max(recent_hvs)
            min_hv = min(recent_hvs)

            if max_hv > 1e-12:
                relative_improvement = (max_hv - min_hv) / max_hv
            else:
                relative_improvement = 0.0

            convergence_result["relative_improvement"] = relative_improvement

            # Check for convergence
            if relative_improvement < threshold:
                convergence_result["converged"] = True
                convergence_result["iterations_stable"] = window_size
                convergence_result["confidence"] = "high" if window_size >= 10 else "medium"
                convergence_result["recommendation"] = "consider_stopping"
            else:
                convergence_result["recommendation"] = "continue"

            return convergence_result

        except Exception as e:
            logger.error(f"Error in convergence check: {e}")
            convergence_result["recommendation"] = "continue - error in analysis"
            return convergence_result
    
    def get_optimization_progress_summary(
        self, 
        iteration_history: List[Dict[str, Any]], 
        experimental_data_count: int
    ) -> Dict[str, Any]:
        """Legacy method: Get optimization progress summary."""
        summary = {
            "total_iterations": len(iteration_history),
            "total_experiments": experimental_data_count,
            "current_hypervolume": None,
            "hypervolume_trend": "unknown",
            "convergence_status": "unknown",
            "efficiency_metrics": {},
            "recommendations": [],
        }

        try:
            if not iteration_history:
                summary["recommendations"].append("Start optimization by adding experimental data")
                return summary

            # Get current hypervolume
            latest_iteration = iteration_history[-1]
            hv_value = latest_iteration.get("hypervolume", 0.0)

            if isinstance(hv_value, dict):
                summary["current_hypervolume"] = {
                    "raw": hv_value.get("raw_hypervolume", 0.0),
                    "normalized": hv_value.get("normalized_hypervolume", 0.0),
                    "data_points_used": hv_value.get("data_points_used", 0),
                }
            else:
                summary["current_hypervolume"] = {"raw": hv_value, "normalized": None}

            # Check convergence
            convergence_result = self.check_hypervolume_convergence(iteration_history)
            summary["convergence_status"] = convergence_result["recommendation"]
            summary["convergence_details"] = convergence_result

            return summary

        except Exception as e:
            logger.error(f"Error generating progress summary: {e}")
            summary["recommendations"].append("Error in progress analysis - continue with caution")
            return summary
    
    def clear_cache(self) -> None:
        """Clear the hypervolume computation cache."""
        self._unified_calculator.clear_cache()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the hypervolume cache."""
        stats = self._unified_calculator.get_cache_stats()
        # Convert to legacy format
        return {
            "cache_size": stats.get("cache_size", 0),
            "cache_hits": 0,  # Not tracked in unified calculator
            "cache_misses": 0  # Not tracked in unified calculator
        }