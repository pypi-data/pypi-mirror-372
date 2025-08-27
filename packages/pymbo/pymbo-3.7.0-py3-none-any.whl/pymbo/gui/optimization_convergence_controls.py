"""
Optimization Convergence Control Module

This module provides a GUI interface for monitoring and configuring convergence detection
in Bayesian optimization. It allows users to view convergence status, adjust thresholds,
and make decisions about when to stop optimization.

Key Features:
- Real-time convergence status display
- Configurable convergence thresholds
- Multi-criteria convergence visualization
- Manual override controls
- Convergence history tracking
- Integration with convergence detector system

Classes:
    OptimizationConvergencePanel: Main convergence monitoring panel
    ConvergenceStatusWidget: Real-time status display widget
    ConvergenceConfigWidget: Configuration controls widget

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Callable, Optional
import threading
import time

# Import unified theme system
try:
    from .gui import ModernTheme
except ImportError:
    # Fallback theme class
    class ModernTheme:
        PRIMARY = "#2D7A8A"
        PRIMARY_DARK = "#1E5A66"
        PRIMARY_LIGHT = "#E8F4F6"
        SURFACE = "#FDFCFA"
        BACKGROUND = "#F7F5F2"
        TEXT_PRIMARY = "#2F2B26"
        TEXT_SECONDARY = "#6B645C"
        TEXT_INVERSE = "#FDFCFA"
        BORDER = "#D6D1CC"
        SUCCESS = "#5A8F5A"
        WARNING = "#C4934A"
        ERROR = "#B85454"
        INPUT_BACKGROUND = "#F9F7F4"
        
        # Complete spacing system
        SPACING_XS = 4    # Extra small spacing
        SPACING_SM = 8    # Small spacing  
        SPACING_MD = 12   # Medium spacing
        SPACING_LG = 16   # Large spacing
        SPACING_XL = 24   # Extra large spacing
        SPACING_XXL = 32  # Extra extra large spacing
        
        @classmethod
        def body_font(cls, size=10):
            return ("Segoe UI", size, "normal")
        
        @classmethod
        def heading_font(cls, size=12):
            return ("Segoe UI", size, "bold")
        
        @classmethod
        def code_font(cls, size=9):
            return ("Consolas", size, "normal")
        
        @classmethod
        def button_font(cls, size=10):
            return ("Segoe UI", size, "normal")

logger = logging.getLogger(__name__)


class ConvergenceStatusWidget:
    """Widget for displaying real-time convergence status."""
    
    def __init__(self, parent: tk.Widget):
        """Initialize convergence status widget."""
        self.parent = parent
        
        # Status variables
        self.converged_var = tk.BooleanVar(value=False)
        self.convergence_score_var = tk.DoubleVar(value=0.0)
        self.recommendation_var = tk.StringVar(value="Continue optimization")
        self.iteration_var = tk.IntVar(value=0)
        
        # Create UI components
        self._create_status_display()
    
    def _create_status_display(self):
        """Create status display components."""
        # Main status frame
        self.status_frame = tk.LabelFrame(
            self.parent,
            text="🎯 Convergence Status",
            font=ModernTheme.heading_font(),
            fg=ModernTheme.PRIMARY,
            bg=ModernTheme.SURFACE,
            relief="solid",
            bd=1
        )
        self.status_frame.pack(fill="x", padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)
        
        # Status indicator
        status_indicator_frame = tk.Frame(self.status_frame, bg=ModernTheme.SURFACE)
        status_indicator_frame.pack(fill="x", padx=ModernTheme.SPACING_MD, pady=ModernTheme.SPACING_SM)
        
        self.status_label = tk.Label(
            status_indicator_frame,
            text="🔄 Optimization in Progress",
            font=ModernTheme.body_font(11),
            fg=ModernTheme.PRIMARY,
            bg=ModernTheme.SURFACE
        )
        self.status_label.pack(side="left")
        
        self.iteration_label = tk.Label(
            status_indicator_frame,
            text="Iteration: 0",
            font=ModernTheme.body_font(),
            fg=ModernTheme.TEXT_SECONDARY,
            bg=ModernTheme.SURFACE
        )
        self.iteration_label.pack(side="right")
        
        # Convergence score bar
        score_frame = tk.Frame(self.status_frame, bg=ModernTheme.SURFACE)
        score_frame.pack(fill="x", padx=ModernTheme.SPACING_MD, pady=(0, ModernTheme.SPACING_SM))
        
        tk.Label(
            score_frame,
            text="Convergence Score:",
            font=ModernTheme.body_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE
        ).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(
            score_frame,
            mode="determinate",
            maximum=100,
            value=0
        )
        self.progress_bar.pack(fill="x", pady=(ModernTheme.SPACING_XS, 0))
        
        self.score_label = tk.Label(
            score_frame,
            text="0.000 / 0.800 (0%)",
            font=ModernTheme.code_font(),
            fg=ModernTheme.TEXT_SECONDARY,
            bg=ModernTheme.SURFACE
        )
        self.score_label.pack(anchor="w")
        
        # Recommendation text
        self.recommendation_label = tk.Label(
            self.status_frame,
            text="Continue: Insufficient data for convergence analysis",
            font=ModernTheme.body_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE,
            wraplength=400,
            justify="left"
        )
        self.recommendation_label.pack(padx=ModernTheme.SPACING_MD, pady=(0, ModernTheme.SPACING_SM), anchor="w")
    
    def update_status(self, convergence_metrics: Dict[str, Any]):
        """Update status display with new convergence metrics."""
        try:
            # Update iteration count
            iteration = convergence_metrics.get('iteration', 0)
            self.iteration_var.set(iteration)
            self.iteration_label.config(text=f"Iteration: {iteration}")
            
            # Update convergence status
            converged = convergence_metrics.get('converged', False)
            self.converged_var.set(converged)
            
            # Update convergence score
            overall_score = convergence_metrics.get('overall_score', 0.0)
            self.convergence_score_var.set(overall_score)
            
            # Update progress bar
            progress_percent = min(overall_score * 100, 100)
            self.progress_bar['value'] = progress_percent
            
            # Update score label
            threshold = 0.8  # Default threshold
            score_text = f"{overall_score:.3f} / {threshold:.3f} ({progress_percent:.1f}%)"
            self.score_label.config(text=score_text)
            
            # Update status indicator
            if converged:
                self.status_label.config(
                    text="✅ Optimization Converged",
                    fg=ModernTheme.SUCCESS
                )
            elif overall_score > 0.6:
                self.status_label.config(
                    text="🟡 Approaching Convergence",
                    fg=ModernTheme.WARNING
                )
            else:
                self.status_label.config(
                    text="🔄 Optimization in Progress",
                    fg=ModernTheme.PRIMARY
                )
            
            # Update recommendation
            recommendation = convergence_metrics.get('recommendation', 'Continue optimization')
            self.recommendation_var.set(recommendation)
            self.recommendation_label.config(text=recommendation)
            
        except Exception as e:
            logger.error(f"Error updating convergence status: {e}")


class ConvergenceConfigWidget:
    """Widget for configuring convergence detection parameters."""
    
    def __init__(self, parent: tk.Widget, config_callback: Callable = None):
        """Initialize convergence configuration widget."""
        self.parent = parent
        self.config_callback = config_callback
        
        # Configuration variables
        self.ei_threshold_var = tk.DoubleVar(value=0.01)
        self.hv_threshold_var = tk.DoubleVar(value=1e-6)
        self.variance_threshold_var = tk.DoubleVar(value=1e-4)
        self.regret_threshold_var = tk.DoubleVar(value=0.01)
        self.convergence_threshold_var = tk.DoubleVar(value=0.8)
        self.min_iterations_var = tk.IntVar(value=10)
        
        # Create UI components
        self._create_config_controls()
    
    def _create_config_controls(self):
        """Create configuration control components."""
        # Configuration frame
        self.config_frame = tk.LabelFrame(
            self.parent,
            text="⚙️ Convergence Configuration",
            font=ModernTheme.heading_font(),
            fg=ModernTheme.PRIMARY,
            bg=ModernTheme.SURFACE,
            relief="solid",
            bd=1
        )
        self.config_frame.pack(fill="x", padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)
        
        # Create scrollable frame for config options
        canvas = tk.Canvas(self.config_frame, height=200, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)
        scrollbar.pack(side="right", fill="y")
        
        # Configuration controls
        self._create_threshold_controls(scrollable_frame)
        
        # Apply button
        apply_btn = tk.Button(
            self.config_frame,
            text="✅ Apply Configuration",
            command=self._apply_config,
            font=ModernTheme.button_font(),
            bg=ModernTheme.SUCCESS,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        apply_btn.pack(pady=ModernTheme.SPACING_SM)
    
    def _create_threshold_controls(self, parent):
        """Create threshold control inputs."""
        configs = [
            ("EI Threshold Factor:", self.ei_threshold_var, "Expected Improvement threshold as fraction of objective range"),
            ("HV Threshold:", self.hv_threshold_var, "Minimum hypervolume improvement for convergence"),
            ("Variance Threshold:", self.variance_threshold_var, "Variance threshold for parameter stability"),
            ("Regret Threshold Factor:", self.regret_threshold_var, "Simple regret improvement threshold"),
            ("Overall Threshold:", self.convergence_threshold_var, "Overall convergence score threshold"),
            ("Min Iterations:", self.min_iterations_var, "Minimum iterations before convergence possible")
        ]
        
        for i, (label_text, var, tooltip) in enumerate(configs):
            # Control frame
            control_frame = tk.Frame(parent, bg=ModernTheme.SURFACE)
            control_frame.pack(fill="x", pady=ModernTheme.SPACING_XS)
            
            # Label
            label = tk.Label(
                control_frame,
                text=label_text,
                font=ModernTheme.body_font(),
                fg=ModernTheme.TEXT_PRIMARY,
                bg=ModernTheme.SURFACE,
                width=20,
                anchor="w"
            )
            label.pack(side="left")
            
            # Entry
            entry = tk.Entry(
                control_frame,
                textvariable=var,
                font=ModernTheme.code_font(),
                width=12,
                justify="right"
            )
            entry.pack(side="right", padx=(ModernTheme.SPACING_SM, 0))
            
            # Tooltip (simplified - just label)
            if tooltip:
                tooltip_label = tk.Label(
                    parent,
                    text=f"  ℹ️ {tooltip}",
                    font=ModernTheme.body_font(8),
                    fg=ModernTheme.TEXT_SECONDARY,
                    bg=ModernTheme.SURFACE,
                    anchor="w"
                )
                tooltip_label.pack(fill="x", padx=ModernTheme.SPACING_LG)
    
    def _apply_config(self):
        """Apply configuration changes."""
        try:
            if self.config_callback:
                config = {
                    'ei_threshold_factor': self.ei_threshold_var.get(),
                    'hv_threshold': self.hv_threshold_var.get(),
                    'variance_threshold': self.variance_threshold_var.get(),
                    'regret_threshold_factor': self.regret_threshold_var.get(),
                    'convergence_threshold': self.convergence_threshold_var.get(),
                    'min_iterations': self.min_iterations_var.get()
                }
                
                success = self.config_callback(config)
                if success:
                    messagebox.showinfo("Configuration Applied", 
                                       "Convergence detection configuration updated successfully!")
                else:
                    messagebox.showerror("Configuration Error", 
                                        "Failed to apply convergence configuration.")
            
        except Exception as e:
            logger.error(f"Error applying convergence configuration: {e}")
            messagebox.showerror("Configuration Error", f"Error applying configuration: {str(e)}")


class OptimizationConvergencePanel:
    """Main panel for monitoring and controlling optimization convergence."""
    
    def __init__(self, parent: tk.Widget, optimizer_interface: Any = None):
        """
        Initialize optimization convergence panel.
        
        Args:
            parent: Parent Tkinter widget
            optimizer_interface: Interface to optimizer with convergence detection
        """
        self.parent = parent
        self.optimizer_interface = optimizer_interface
        
        # Create popup window
        self.popup_window = None
        self._monitoring_active = False
        self._monitoring_thread = None
        
        # GUI components
        self.status_widget = None
        self.config_widget = None
        
        # Create interface
        self._create_popup_window()
    
    def _create_popup_window(self):
        """Create popup window for convergence monitoring."""
        try:
            # Create popup window
            self.popup_window = tk.Toplevel(self.parent)
            self.popup_window.title("🎯 Optimization Convergence Monitor")
            self.popup_window.geometry("500x700")
            
            # Apply ModernTheme styling
            self.popup_window.configure(bg=ModernTheme.BACKGROUND)
            
            # Set window properties
            self.popup_window.resizable(True, True)
            self.popup_window.minsize(450, 600)
            
            # Initially hide the window
            self.popup_window.withdraw()
            
            # Handle window close event
            self.popup_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            # Create main frame
            main_frame = tk.Frame(self.popup_window, bg=ModernTheme.BACKGROUND)
            main_frame.pack(fill="both", expand=True, padx=ModernTheme.SPACING_MD, pady=ModernTheme.SPACING_MD)
            
            # Title
            title_label = tk.Label(
                main_frame,
                text="🎯 Optimization Convergence Monitor",
                font=ModernTheme.heading_font(14),
                fg=ModernTheme.TEXT_PRIMARY,
                bg=ModernTheme.BACKGROUND
            )
            title_label.pack(pady=(0, ModernTheme.SPACING_LG))
            
            # Create status widget
            self.status_widget = ConvergenceStatusWidget(main_frame)
            
            # Create config widget
            self.config_widget = ConvergenceConfigWidget(
                main_frame, 
                config_callback=self._apply_convergence_config
            )
            
            # Control buttons
            self._create_control_buttons(main_frame)
            
            # Convergence history
            self._create_history_section(main_frame)
            
            logger.info("Convergence monitoring panel created successfully")
            
        except Exception as e:
            logger.error(f"Error creating convergence panel: {e}")
            messagebox.showerror("Panel Error", f"Failed to create convergence panel: {str(e)}")
    
    def _create_control_buttons(self, parent):
        """Create control buttons."""
        button_frame = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        button_frame.pack(fill="x", pady=ModernTheme.SPACING_LG)
        
        # Start monitoring button
        self.monitor_btn = tk.Button(
            button_frame,
            text="▶️ Start Monitoring",
            command=self._toggle_monitoring,
            font=ModernTheme.button_font(),
            bg=ModernTheme.SUCCESS,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        self.monitor_btn.pack(side="left")
        
        # Force stop button
        stop_btn = tk.Button(
            button_frame,
            text="🛑 Force Stop Optimization",
            command=self._force_stop_optimization,
            font=ModernTheme.button_font(),
            bg=ModernTheme.ERROR,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        stop_btn.pack(side="right")
        
        # Reset button
        reset_btn = tk.Button(
            button_frame,
            text="🔄 Reset Convergence",
            command=self._reset_convergence,
            font=ModernTheme.button_font(),
            bg=ModernTheme.WARNING,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        reset_btn.pack()
    
    def _create_history_section(self, parent):
        """Create convergence history section."""
        history_frame = tk.LabelFrame(
            parent,
            text="📊 Convergence History",
            font=ModernTheme.heading_font(),
            fg=ModernTheme.PRIMARY,
            bg=ModernTheme.SURFACE,
            relief="solid",
            bd=1
        )
        history_frame.pack(fill="both", expand=True, padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)
        
        # History text area
        self.history_text = tk.Text(
            history_frame,
            height=8,
            font=ModernTheme.code_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE,
            relief="solid",
            bd=1,
            state="disabled"
        )
        
        # Scrollbar for history
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_text.pack(side="left", fill="both", expand=True, padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)
        history_scrollbar.pack(side="right", fill="y", pady=ModernTheme.SPACING_SM)
    
    def _toggle_monitoring(self):
        """Toggle convergence monitoring."""
        if self._monitoring_active:
            self._stop_monitoring()
        else:
            self._start_monitoring()
    
    def _start_monitoring(self):
        """Start convergence monitoring."""
        try:
            self._monitoring_active = True
            self.monitor_btn.config(text="⏸️ Stop Monitoring", bg=ModernTheme.WARNING)
            
            # Start monitoring thread
            self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
            
            self._add_history_entry("🟢 Convergence monitoring started")
            logger.info("Convergence monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self._monitoring_active = False
            self.monitor_btn.config(text="▶️ Start Monitoring", bg=ModernTheme.SUCCESS)
    
    def _stop_monitoring(self):
        """Stop convergence monitoring."""
        self._monitoring_active = False
        self.monitor_btn.config(text="▶️ Start Monitoring", bg=ModernTheme.SUCCESS)
        
        self._add_history_entry("🔴 Convergence monitoring stopped")
        logger.info("Convergence monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                if self.optimizer_interface and hasattr(self.optimizer_interface, 'get_convergence_summary'):
                    # Get convergence metrics
                    summary = self.optimizer_interface.get_convergence_summary()
                    
                    if 'current_status' in summary:
                        # Update status widget
                        self.popup_window.after(0, self.status_widget.update_status, summary['current_status'])
                        
                        # Log significant changes
                        if summary['current_status'].get('converged', False):
                            self._add_history_entry("✅ Optimization has converged!")
                            break
                
                # Sleep for monitoring interval
                time.sleep(2.0)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _apply_convergence_config(self, config: Dict[str, Any]) -> bool:
        """Apply convergence configuration."""
        try:
            if self.optimizer_interface and hasattr(self.optimizer_interface, 'configure_convergence_detection'):
                success = self.optimizer_interface.configure_convergence_detection(**config)
                
                if success:
                    self._add_history_entry(f"⚙️ Configuration applied: threshold={config.get('convergence_threshold', 0.8)}")
                    return True
                else:
                    self._add_history_entry("❌ Configuration failed to apply")
                    return False
            else:
                self._add_history_entry("❌ No optimizer interface available")
                return False
                
        except Exception as e:
            logger.error(f"Error applying convergence config: {e}")
            self._add_history_entry(f"❌ Configuration error: {str(e)}")
            return False
    
    def _force_stop_optimization(self):
        """Force stop optimization."""
        try:
            if self.optimizer_interface and hasattr(self.optimizer_interface, '_should_stop_optimization'):
                self.optimizer_interface._should_stop_optimization = True
                self.optimizer_interface._convergence_reason = "Manually stopped by user"
                
                self._add_history_entry("🛑 Optimization manually stopped")
                messagebox.showinfo("Optimization Stopped", "Optimization has been manually stopped.")
            else:
                messagebox.showwarning("No Optimizer", "No active optimizer to stop.")
                
        except Exception as e:
            logger.error(f"Error forcing stop: {e}")
            messagebox.showerror("Stop Error", f"Error stopping optimization: {str(e)}")
    
    def _reset_convergence(self):
        """Reset convergence detection."""
        try:
            if self.optimizer_interface and hasattr(self.optimizer_interface, 'reset_convergence_detection'):
                self.optimizer_interface.reset_convergence_detection()
                self._add_history_entry("🔄 Convergence detection reset")
                messagebox.showinfo("Reset Complete", "Convergence detection has been reset.")
            else:
                messagebox.showwarning("No Optimizer", "No active optimizer to reset.")
                
        except Exception as e:
            logger.error(f"Error resetting convergence: {e}")
            messagebox.showerror("Reset Error", f"Error resetting convergence: {str(e)}")
    
    def _add_history_entry(self, message: str):
        """Add entry to convergence history."""
        try:
            timestamp = time.strftime("%H:%M:%S")
            entry = f"[{timestamp}] {message}\n"
            
            # Update in main thread
            self.popup_window.after(0, self._update_history_text, entry)
            
        except Exception as e:
            logger.error(f"Error adding history entry: {e}")
    
    def _update_history_text(self, entry: str):
        """Update history text widget."""
        try:
            self.history_text.config(state="normal")
            self.history_text.insert(tk.END, entry)
            self.history_text.see(tk.END)  # Scroll to bottom
            self.history_text.config(state="disabled")
        except Exception as e:
            logger.error(f"Error updating history text: {e}")
    
    def show_window(self):
        """Show the convergence panel window."""
        if self.popup_window:
            self.popup_window.deiconify()
            self.popup_window.lift()
            self.popup_window.focus_set()
            logger.info("Convergence monitoring panel shown")
    
    def hide_window(self):
        """Hide the convergence panel window."""
        if self.popup_window:
            self.popup_window.withdraw()
            logger.info("Convergence monitoring panel hidden")
    
    def _on_window_close(self):
        """Handle window close event."""
        self._stop_monitoring()
        self.hide_window()
    
    def set_optimizer_interface(self, optimizer_interface: Any):
        """Set optimizer interface for convergence monitoring."""
        self.optimizer_interface = optimizer_interface
        logger.info("Optimizer interface set for convergence monitoring")


def create_convergence_panel(parent: tk.Widget, optimizer_interface: Any = None) -> OptimizationConvergencePanel:
    """
    Factory function to create optimization convergence panel.
    
    Args:
        parent: Parent widget
        optimizer_interface: Interface to optimizer with convergence detection
        
    Returns:
        OptimizationConvergencePanel instance
    """
    try:
        panel = OptimizationConvergencePanel(parent, optimizer_interface)
        logger.info("Convergence panel created successfully")
        return panel
    except Exception as e:
        logger.error(f"Error creating convergence panel: {e}")
        messagebox.showerror("Panel Creation Error", f"Failed to create convergence panel: {str(e)}")
        return None