"""
Convergence Detection System for Multi-Objective Bayesian Optimization

This module implements a comprehensive convergence detection system that determines
when optimization should terminate based on multiple statistical and heuristic criteria.
Implements established Bayesian optimization stopping protocols from academic literature.

Key Features:
- Expected Improvement threshold-based stopping
- Hypervolume stagnation detection for multi-objective optimization
- Statistical variance-based convergence monitoring
- Simple regret plateau detection
- Weighted multi-criteria decision making
- Configurable thresholds and windows
- Comprehensive logging and monitoring

Classes:
    ConvergenceDetector: Main convergence detection system
    ConvergenceConfig: Configuration for convergence thresholds
    ConvergenceMetrics: Current convergence state metrics

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

import numpy as np
import pandas as pd
import torch
from typing_extensions import Literal

# Import hypervolume utilities
try:
    from ..utils.unified_hypervolume import calculate_hypervolume_indicator
    HYPERVOLUME_AVAILABLE = True
except ImportError:
    HYPERVOLUME_AVAILABLE = False
    warnings.warn("Hypervolume utilities not available. Multi-objective convergence detection limited.", UserWarning)

logger = logging.getLogger(__name__)


@dataclass
class ConvergenceConfig:
    """Configuration class for convergence detection parameters."""
    
    # Expected Improvement threshold parameters
    ei_threshold_factor: float = 0.01  # EI threshold as fraction of objective range
    ei_stagnation_window: int = 5      # Number of iterations to check for low EI
    
    # Hypervolume stagnation parameters  
    hv_threshold: float = 1e-6         # Minimum hypervolume improvement
    hv_stagnation_window: int = 10     # Number of iterations for HV plateau
    
    # Statistical convergence parameters
    variance_threshold: float = 1e-4   # Variance threshold for recent objectives
    variance_window: int = 10          # Window size for variance calculation
    
    # Simple regret parameters
    regret_threshold_factor: float = 0.01  # Regret threshold as fraction of best value
    regret_stagnation_window: int = 15     # Number of iterations for regret plateau
    
    # Multi-criteria decision weights
    ei_weight: float = 0.3
    hv_weight: float = 0.3
    variance_weight: float = 0.2
    regret_weight: float = 0.2
    
    # Overall convergence threshold
    convergence_threshold: float = 0.8  # Weighted score threshold for convergence
    
    # Safety parameters
    min_iterations: int = 10           # Minimum iterations before convergence possible
    max_iterations: int = 1000         # Maximum iterations (safety override)
    
    # Resource-based termination parameters
    max_wall_time_hours: Optional[float] = None  # Maximum wall-clock time in hours
    max_function_evaluations: Optional[int] = None  # Maximum function evaluations


@dataclass
class ConvergenceMetrics:
    """Container for current convergence state metrics."""
    
    # Current metric values
    current_ei: float = 0.0
    current_hv: float = 0.0
    current_variance: float = 0.0
    current_regret: float = 0.0
    
    # Convergence indicators (0-1 scale)
    ei_convergence_score: float = 0.0
    hv_convergence_score: float = 0.0
    variance_convergence_score: float = 0.0
    regret_convergence_score: float = 0.0
    
    # Overall convergence score
    overall_score: float = 0.0
    
    # Status flags
    ei_converged: bool = False
    hv_converged: bool = False
    variance_converged: bool = False
    regret_converged: bool = False
    
    # Overall convergence decision
    converged: bool = False
    
    # Resource tracking
    wall_time_hours: float = 0.0
    resource_limit_reached: bool = False
    
    # Metadata
    iteration: int = 0
    timestamp: float = 0.0
    recommendation: str = "Continue optimization"


class ConvergenceDetector:
    """
    Multi-criteria convergence detection system for Bayesian optimization.
    
    Implements academic best practices for determining when optimization should terminate
    by combining multiple statistical and heuristic stopping criteria.
    """
    
    def __init__(self, config: Optional[ConvergenceConfig] = None):
        """
        Initialize convergence detector with configuration.
        
        Args:
            config: Convergence detection configuration. Uses defaults if None.
        """
        self.config = config or ConvergenceConfig()
        
        # History tracking
        self.ei_history: List[float] = []
        self.hv_history: List[float] = []
        self.objective_history: List[np.ndarray] = []
        self.best_value_history: List[float] = []
        self.convergence_history: List[ConvergenceMetrics] = []
        
        # State tracking
        self.iteration_count = 0
        self.start_time = time.time()
        self._last_check_time = 0.0
        
        # Objective space bounds for threshold calculations
        self._objective_range: Optional[float] = None
        self._current_best: Optional[float] = None
        
        logger.info(f"Convergence detector initialized with config: {self.config}")
    
    def update_data(self, 
                   experimental_data: pd.DataFrame,
                   objective_names: List[str],
                   optimization_direction: Dict[str, str]) -> None:
        """
        Update convergence detector with new experimental data.
        
        Args:
            experimental_data: Current experimental dataset
            objective_names: Names of objective columns
            optimization_direction: Direction for each objective ('minimize' or 'maximize')
        """
        try:
            if experimental_data.empty:
                return
                
            self.iteration_count = len(experimental_data)
            
            # Extract objective values
            objective_data = experimental_data[objective_names].values
            
            # Update objective history
            self.objective_history.append(objective_data[-1])  # Add latest point
            
            # Calculate objective range for threshold scaling
            if len(objective_data) > 1:
                obj_min = np.min(objective_data, axis=0)
                obj_max = np.max(objective_data, axis=0)
                self._objective_range = np.mean(obj_max - obj_min)  # Average range across objectives
            
            # Update best value tracking (for single-objective regret)
            if len(objective_names) == 1:
                objective_col = objective_names[0]
                if optimization_direction[objective_col] == 'minimize':
                    current_best = experimental_data[objective_col].min()
                else:
                    current_best = experimental_data[objective_col].max()
                
                self.best_value_history.append(current_best)
                self._current_best = current_best
            
            logger.debug(f"Updated convergence data: iteration {self.iteration_count}, "
                        f"objective_range={self._objective_range}")
                        
        except Exception as e:
            logger.error(f"Error updating convergence data: {e}")
    
    def check_convergence(self, 
                         acquisition_value: Optional[float] = None,
                         hypervolume_value: Optional[float] = None) -> ConvergenceMetrics:
        """
        Perform comprehensive convergence check using all criteria.
        
        Args:
            acquisition_value: Current acquisition function value (e.g., EI)
            hypervolume_value: Current hypervolume indicator
            
        Returns:
            ConvergenceMetrics object with detailed convergence analysis
        """
        try:
            current_time = time.time()
            self._last_check_time = current_time
            
            # Initialize metrics
            metrics = ConvergenceMetrics(
                iteration=self.iteration_count,
                timestamp=current_time,
                wall_time_hours=(current_time - self.start_time) / 3600
            )
            
            # Safety check: minimum iterations
            if self.iteration_count < self.config.min_iterations:
                metrics.recommendation = f"Continue: Only {self.iteration_count} iterations (min: {self.config.min_iterations})"
                return metrics
            
            # Resource check: maximum wall time
            if (self.config.max_wall_time_hours is not None and 
                metrics.wall_time_hours >= self.config.max_wall_time_hours):
                metrics.converged = True
                metrics.overall_score = 1.0
                metrics.resource_limit_reached = True
                metrics.recommendation = f"Stop: Maximum time reached ({metrics.wall_time_hours:.1f}h >= {self.config.max_wall_time_hours:.1f}h)"
                return metrics
            
            # Resource check: maximum function evaluations
            if (self.config.max_function_evaluations is not None and 
                self.iteration_count >= self.config.max_function_evaluations):
                metrics.converged = True
                metrics.overall_score = 1.0
                metrics.resource_limit_reached = True
                metrics.recommendation = f"Stop: Maximum evaluations reached ({self.iteration_count} >= {self.config.max_function_evaluations})"
                return metrics
            
            # Safety check: maximum iterations
            if self.iteration_count >= self.config.max_iterations:
                metrics.converged = True
                metrics.overall_score = 1.0
                metrics.recommendation = f"Stop: Maximum iterations reached ({self.config.max_iterations})"
                return metrics
            
            # Check each convergence criterion
            self._check_ei_convergence(metrics, acquisition_value)
            self._check_hv_convergence(metrics, hypervolume_value)  
            self._check_variance_convergence(metrics)
            self._check_regret_convergence(metrics)
            
            # Calculate weighted overall score
            metrics.overall_score = (
                self.config.ei_weight * metrics.ei_convergence_score +
                self.config.hv_weight * metrics.hv_convergence_score +
                self.config.variance_weight * metrics.variance_convergence_score +
                self.config.regret_weight * metrics.regret_convergence_score
            )
            
            # Make convergence decision
            metrics.converged = metrics.overall_score >= self.config.convergence_threshold
            
            # Generate recommendation
            if metrics.converged:
                metrics.recommendation = f"Stop: Convergence achieved (score: {metrics.overall_score:.3f})"
            else:
                metrics.recommendation = f"Continue: Convergence score {metrics.overall_score:.3f} < {self.config.convergence_threshold}"
            
            # Store in history
            self.convergence_history.append(metrics)
            
            # Log convergence status
            logger.info(f"Convergence check [iter={self.iteration_count}]: "
                       f"EI={metrics.ei_convergence_score:.3f}, "
                       f"HV={metrics.hv_convergence_score:.3f}, "
                       f"Var={metrics.variance_convergence_score:.3f}, "
                       f"Regret={metrics.regret_convergence_score:.3f}, "
                       f"Overall={metrics.overall_score:.3f} -> {metrics.recommendation}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in convergence check: {e}")
            # Return safe default
            return ConvergenceMetrics(
                iteration=self.iteration_count,
                timestamp=time.time(),
                recommendation=f"Continue: Error in convergence check ({e})"
            )
    
    def _check_ei_convergence(self, metrics: ConvergenceMetrics, acquisition_value: Optional[float]) -> None:
        """Check Expected Improvement based convergence."""
        try:
            if acquisition_value is None or self._objective_range is None:
                return
            
            metrics.current_ei = acquisition_value
            self.ei_history.append(acquisition_value)
            
            # Calculate EI threshold based on objective range
            ei_threshold = self.config.ei_threshold_factor * self._objective_range
            
            # Check if EI is below threshold for specified window
            if len(self.ei_history) >= self.config.ei_stagnation_window:
                recent_ei = self.ei_history[-self.config.ei_stagnation_window:]
                low_ei_count = sum(1 for ei in recent_ei if ei < ei_threshold)
                
                metrics.ei_convergence_score = low_ei_count / self.config.ei_stagnation_window
                metrics.ei_converged = metrics.ei_convergence_score >= 0.8  # 80% of recent EI values below threshold
                
                logger.debug(f"EI convergence: threshold={ei_threshold:.6f}, recent_low_count={low_ei_count}, score={metrics.ei_convergence_score:.3f}")
            
        except Exception as e:
            logger.debug(f"Error in EI convergence check: {e}")
    
    def _check_hv_convergence(self, metrics: ConvergenceMetrics, hypervolume_value: Optional[float]) -> None:
        """Check hypervolume stagnation based convergence."""
        try:
            if not HYPERVOLUME_AVAILABLE or hypervolume_value is None:
                return
            
            metrics.current_hv = hypervolume_value
            self.hv_history.append(hypervolume_value)
            
            # Check hypervolume improvement over window
            if len(self.hv_history) >= self.config.hv_stagnation_window:
                window_start = len(self.hv_history) - self.config.hv_stagnation_window
                hv_window = self.hv_history[window_start:]
                
                # Calculate improvement over window
                hv_improvement = max(hv_window) - min(hv_window)
                
                # Score based on improvement relative to threshold
                if hv_improvement <= self.config.hv_threshold:
                    metrics.hv_convergence_score = 1.0  # Converged (no improvement)
                else:
                    # Scale score: less improvement = higher convergence score
                    metrics.hv_convergence_score = max(0.0, 1.0 - (hv_improvement / (10 * self.config.hv_threshold)))
                
                metrics.hv_converged = hv_improvement <= self.config.hv_threshold
                
                logger.debug(f"HV convergence: improvement={hv_improvement:.8f}, threshold={self.config.hv_threshold}, score={metrics.hv_convergence_score:.3f}")
            
        except Exception as e:
            logger.debug(f"Error in HV convergence check: {e}")
    
    def _check_variance_convergence(self, metrics: ConvergenceMetrics) -> None:
        """Check statistical variance based convergence."""
        try:
            if len(self.objective_history) < self.config.variance_window:
                return
            
            # Get recent objective values
            recent_objectives = self.objective_history[-self.config.variance_window:]
            recent_array = np.array(recent_objectives)
            
            # Calculate variance across recent objectives
            if len(recent_array.shape) > 1:
                # Multi-objective: mean variance across objectives
                variances = np.var(recent_array, axis=0)
                mean_variance = np.mean(variances)
            else:
                # Single objective
                mean_variance = np.var(recent_array)
            
            metrics.current_variance = mean_variance
            
            # Score based on variance relative to threshold
            if mean_variance <= self.config.variance_threshold:
                metrics.variance_convergence_score = 1.0
                metrics.variance_converged = True
            else:
                # Scale score: lower variance = higher convergence score
                metrics.variance_convergence_score = max(0.0, 1.0 - (mean_variance / (10 * self.config.variance_threshold)))
            
            logger.debug(f"Variance convergence: variance={mean_variance:.8f}, threshold={self.config.variance_threshold}, score={metrics.variance_convergence_score:.3f}")
            
        except Exception as e:
            logger.debug(f"Error in variance convergence check: {e}")
    
    def _check_regret_convergence(self, metrics: ConvergenceMetrics) -> None:
        """Check simple regret plateau based convergence."""
        try:
            if len(self.best_value_history) < self.config.regret_stagnation_window or self._current_best is None:
                return
            
            # Calculate regret improvement over window
            window_start = len(self.best_value_history) - self.config.regret_stagnation_window
            best_window = self.best_value_history[window_start:]
            
            regret_improvement = abs(max(best_window) - min(best_window))
            regret_threshold = self.config.regret_threshold_factor * abs(self._current_best)
            
            metrics.current_regret = regret_improvement
            
            # Score based on regret improvement
            if regret_improvement <= regret_threshold:
                metrics.regret_convergence_score = 1.0
                metrics.regret_converged = True
            else:
                # Scale score: less improvement = higher convergence score
                metrics.regret_convergence_score = max(0.0, 1.0 - (regret_improvement / (10 * regret_threshold)))
            
            logger.debug(f"Regret convergence: improvement={regret_improvement:.6f}, threshold={regret_threshold:.6f}, score={metrics.regret_convergence_score:.3f}")
            
        except Exception as e:
            logger.debug(f"Error in regret convergence check: {e}")
    
    def get_convergence_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive convergence analysis summary.
        
        Returns:
            Dictionary with convergence history, statistics, and recommendations
        """
        try:
            if not self.convergence_history:
                return {"status": "No convergence data available"}
            
            latest = self.convergence_history[-1]
            
            return {
                "current_status": {
                    "converged": latest.converged,
                    "iteration": latest.iteration,
                    "overall_score": latest.overall_score,
                    "recommendation": latest.recommendation
                },
                "criteria_scores": {
                    "expected_improvement": latest.ei_convergence_score,
                    "hypervolume": latest.hv_convergence_score,
                    "variance": latest.variance_convergence_score,
                    "regret": latest.regret_convergence_score
                },
                "individual_convergence": {
                    "ei_converged": latest.ei_converged,
                    "hv_converged": latest.hv_converged,
                    "variance_converged": latest.variance_converged,
                    "regret_converged": latest.regret_converged
                },
                "history_length": len(self.convergence_history),
                "total_runtime": time.time() - self.start_time,
                "config": {
                    "convergence_threshold": self.config.convergence_threshold,
                    "min_iterations": self.config.min_iterations,
                    "max_iterations": self.config.max_iterations
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating convergence summary: {e}")
            return {"status": "Error generating summary", "error": str(e)}
    
    def plot_convergence_history(self) -> Optional[Dict[str, Any]]:
        """
        Generate convergence history data for plotting.
        
        Returns:
            Dictionary with plot data or None if insufficient data
        """
        try:
            if len(self.convergence_history) < 2:
                return None
            
            iterations = [m.iteration for m in self.convergence_history]
            overall_scores = [m.overall_score for m in self.convergence_history]
            ei_scores = [m.ei_convergence_score for m in self.convergence_history]
            hv_scores = [m.hv_convergence_score for m in self.convergence_history]
            variance_scores = [m.variance_convergence_score for m in self.convergence_history]
            regret_scores = [m.regret_convergence_score for m in self.convergence_history]
            
            return {
                "iterations": iterations,
                "overall_convergence": overall_scores,
                "ei_convergence": ei_scores,
                "hv_convergence": hv_scores,
                "variance_convergence": variance_scores,
                "regret_convergence": regret_scores,
                "convergence_threshold": self.config.convergence_threshold
            }
            
        except Exception as e:
            logger.error(f"Error generating convergence plot data: {e}")
            return None
    
    def reset(self) -> None:
        """Reset convergence detector to initial state."""
        try:
            self.ei_history.clear()
            self.hv_history.clear()
            self.objective_history.clear()
            self.best_value_history.clear()
            self.convergence_history.clear()
            
            self.iteration_count = 0
            self.start_time = time.time()
            self._last_check_time = 0.0
            self._objective_range = None
            self._current_best = None
            
            logger.info("Convergence detector reset to initial state")
            
        except Exception as e:
            logger.error(f"Error resetting convergence detector: {e}")


# Utility functions for integration
def create_default_convergence_config(**kwargs) -> ConvergenceConfig:
    """
    Create a convergence configuration with custom overrides.
    
    Args:
        **kwargs: Configuration parameters to override defaults
        
    Returns:
        ConvergenceConfig with specified parameters
    """
    config = ConvergenceConfig()
    
    # Apply overrides
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown convergence config parameter: {key}")
    
    return config


def quick_convergence_check(experimental_data: pd.DataFrame,
                          objective_names: List[str],
                          optimization_direction: Dict[str, str],
                          acquisition_value: Optional[float] = None) -> bool:
    """
    Perform a quick convergence check with default settings.
    
    Args:
        experimental_data: Current experimental dataset
        objective_names: Names of objective columns
        optimization_direction: Direction for each objective
        acquisition_value: Current acquisition function value
        
    Returns:
        True if optimization should stop, False if it should continue
    """
    try:
        detector = ConvergenceDetector()
        detector.update_data(experimental_data, objective_names, optimization_direction)
        metrics = detector.check_convergence(acquisition_value=acquisition_value)
        
        return metrics.converged
        
    except Exception as e:
        logger.error(f"Error in quick convergence check: {e}")
        return False  # Default to continue optimization on error