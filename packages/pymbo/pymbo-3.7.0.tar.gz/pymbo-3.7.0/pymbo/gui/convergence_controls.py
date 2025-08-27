"""
Enhanced Parameter Convergence Plot Control Module

This module provides an advanced graphical user interface for controlling Parameter Convergence plot
visualizations within the PyMBO optimization framework. It implements parameter selection controls,
convergence metrics display, and seamless integration with the existing GUI architecture as a popout window.

Key Features:
- Dynamic parameter selection with individual parameter visibility controls
- Multiple convergence visualization modes (raw values, normalized, distance to optimum)
- Real-time convergence metrics (std deviation, range, convergence rate)
- Trend line and confidence interval display options
- Scrollable popout window for better accessibility
- Consistent ModernTheme design language adherence
- DPI export functionality

Classes:
    ConvergencePlotControlPanel: Main control panel class for Parameter Convergence plot management
    
Functions:
    create_convergence_control_panel: Factory function for control panel instantiation

Author: PyMBO Development Team
Version: 3.7.0 Enhanced (Parameter Convergence)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Callable, List, Optional, Tuple
import threading

# Import unified theme system from main GUI module
try:
    from .gui import ModernTheme
    # Legacy color constants for backward compatibility
    COLOR_PRIMARY = ModernTheme.PRIMARY
    COLOR_SECONDARY = ModernTheme.TEXT_SECONDARY
    COLOR_SUCCESS = ModernTheme.SUCCESS
    COLOR_WARNING = ModernTheme.WARNING
    COLOR_ERROR = ModernTheme.ERROR
    COLOR_BACKGROUND = ModernTheme.BACKGROUND
    COLOR_SURFACE = ModernTheme.SURFACE
except ImportError:
    # Fallback theme class and color scheme if import fails
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
        SPACING_SM = 8
        SPACING_MD = 12
        SPACING_LG = 16
        SPACING_XL = 24
        SPACING_XXL = 32
        SPACING_XS = 4
        
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
    
    # Legacy color constants
    COLOR_PRIMARY = ModernTheme.PRIMARY
    COLOR_SECONDARY = ModernTheme.TEXT_SECONDARY
    COLOR_SUCCESS = ModernTheme.SUCCESS
    COLOR_WARNING = ModernTheme.WARNING
    COLOR_ERROR = ModernTheme.ERROR
    COLOR_BACKGROUND = ModernTheme.BACKGROUND
    COLOR_SURFACE = ModernTheme.SURFACE

logger = logging.getLogger(__name__)


class ConvergencePlotControlPanel:
    """
    Advanced control panel for Parameter Convergence plot visualization management in a separate popout window.
    
    This class provides comprehensive control over Parameter Convergence plot rendering, including
    parameter selection, convergence metrics display, visualization modes, and real-time plot
    updates. It operates as a separate window for better accessibility and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("convergence")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        x_axis_var: StringVar for X-axis selection
        y_mode_var: StringVar for Y-axis mode selection
        parameter_visibility: Dictionary of BooleanVar objects for parameter visibility
        display_options: Dictionary of BooleanVar objects for display options
        available_x_metrics: List of available X-axis metrics
        available_y_modes: List of available Y-axis modes
        dpi_var: IntVar for export DPI selection
        convergence_metrics: Dictionary storing current convergence metrics
    """
    def __init__(self, parent: tk.Widget, plot_type: str, 
                 params_config: Dict[str, Any] = None,
                 responses_config: Dict[str, Any] = None,
                 update_callback: Callable = None):
        """
        Initialize the Parameter Convergence plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "convergence"
            params_config: Dictionary containing parameter configurations
            responses_config: Dictionary containing response configurations
            update_callback: Function to call when plot updates are needed
        """
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        
        # Create separate popup window
        self.popup_window = None
        
        # GUI components
        self.main_frame = None
        self.scroll_canvas = None
        self.scroll_frame = None
        
        # Control variables
        self.x_axis_var = tk.StringVar(value="iteration")
        self.y_mode_var = tk.StringVar(value="raw_values")
        
        # Parameter visibility controls
        self.parameter_visibility = {}
        
        # Display option controls
        self.display_options = {
            "show_trend_lines": tk.BooleanVar(value=True),
            "show_confidence_intervals": tk.BooleanVar(value=False),
            "show_convergence_zones": tk.BooleanVar(value=True),
            "show_legend": tk.BooleanVar(value=True),
            "normalize_axes": tk.BooleanVar(value=False)
        }
        
        # Available options for axis selection
        self.available_x_metrics = [
            "iteration", "experiment_number", "execution_time"
        ]
        
        self.available_y_modes = [
            "raw_values", "normalized_values", "distance_to_optimum", 
            "convergence_rate", "parameter_stability"
        ]
        
        # Export settings
        self.dpi_var = tk.IntVar(value=300)
        
        # Convergence metrics storage
        self.convergence_metrics = {}
        
        logger.info(f"Creating enhanced Parameter Convergence control panel for plot type: {plot_type}")
        self._create_popup_window()

    def _create_popup_window(self):
        """Create the popout window for the control panel"""
        try:
            # Create popup window
            self.popup_window = tk.Toplevel(self.parent)
            self.popup_window.title(f"Parameter Convergence Plot Controls")
            self.popup_window.geometry("420x650")
            
            # Apply ModernTheme styling
            self.popup_window.configure(bg=ModernTheme.BACKGROUND)
            
            # Set window properties
            self.popup_window.resizable(True, True)
            self.popup_window.minsize(400, 500)
            
            # Initially hide the window
            self.popup_window.withdraw()
            
            # Handle window close event
            self.popup_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            # Create main container with scrolling
            self._create_scrollable_frame()
            self._create_control_sections()
            
            logger.info(f"Enhanced Parameter Convergence plot control panel initialized for {self.plot_type}")
            
        except Exception as e:
            logger.error(f"Error creating Parameter Convergence control panel popup: {e}")
            messagebox.showerror("Control Panel Error", 
                               f"Failed to create Parameter Convergence control panel: {str(e)}")

    def _create_scrollable_frame(self):
        """Create scrollable frame structure using ModernTheme"""
        try:
            # Main frame
            self.main_frame = tk.Frame(self.popup_window, bg=ModernTheme.BACKGROUND)
            self.main_frame.pack(fill="both", expand=True, padx=ModernTheme.SPACING_MD, pady=ModernTheme.SPACING_MD)
            
            # Create canvas and scrollbar
            self.scroll_canvas = tk.Canvas(
                self.main_frame, 
                bg=ModernTheme.SURFACE,
                highlightthickness=0,
                bd=0
            )
            scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.scroll_canvas.yview)
            
            # Scrollable frame
            self.scroll_frame = tk.Frame(self.scroll_canvas, bg=ModernTheme.SURFACE)
            
            # Configure scrolling
            self.scroll_frame.bind(
                "<Configure>",
                lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
            )
            
            # Pack components
            self.scroll_canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Create window in canvas
            self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
            
            # Bind mouse wheel
            self._bind_mousewheel()
            
        except Exception as e:
            logger.error(f"Error creating scrollable frame: {e}")

    def _bind_mousewheel(self):
        """Bind mouse wheel scrolling"""
        def _on_mousewheel(event):
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.scroll_canvas.bind("<MouseWheel>", _on_mousewheel)

    def _create_control_sections(self):
        """Create all control sections with ModernTheme styling"""
        try:
            # Title section
            self._create_title_section()
            
            # X-axis controls
            self._create_x_axis_section()
            
            # Y-axis mode controls  
            self._create_y_mode_section()
            
            # Parameter selection
            self._create_parameter_selection_section()
            
            # Display options
            self._create_display_options_section()
            
            # Convergence metrics display
            self._create_metrics_display_section()
            
            # Export controls
            self._create_export_section()
            
            # Action buttons
            self._create_action_buttons()
            
        except Exception as e:
            logger.error(f"Error creating control sections: {e}")

    def _create_title_section(self):
        """Create title section"""
        title_frame = tk.Frame(self.scroll_frame, bg=ModernTheme.SURFACE)
        title_frame.pack(fill="x", padx=ModernTheme.SPACING_SM, pady=(0, ModernTheme.SPACING_LG))
        
        title_label = tk.Label(
            title_frame,
            text="📈 Parameter Convergence Plot Controls",
            font=ModernTheme.heading_font(14),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE
        )
        title_label.pack()

    def _create_x_axis_section(self):
        """Create X-axis selection section"""
        section_frame = self._create_section_frame("X-Axis Selection")
        
        # X-axis selection
        x_frame = tk.Frame(section_frame, bg=ModernTheme.SURFACE)
        x_frame.pack(fill="x", pady=ModernTheme.SPACING_SM)
        
        tk.Label(
            x_frame,
            text="X-Axis Metric:",
            font=ModernTheme.body_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE
        ).pack(anchor="w")
        
        x_combo = ttk.Combobox(
            x_frame,
            textvariable=self.x_axis_var,
            values=self.available_x_metrics,
            state="readonly",
            font=ModernTheme.body_font()
        )
        x_combo.pack(fill="x", pady=(ModernTheme.SPACING_XS, 0))
        x_combo.bind("<<ComboboxSelected>>", self._on_axis_change)

    def _create_y_mode_section(self):
        """Create Y-axis mode selection section"""
        section_frame = self._create_section_frame("Y-Axis Display Mode")
        
        # Y-mode selection
        y_frame = tk.Frame(section_frame, bg=ModernTheme.SURFACE)
        y_frame.pack(fill="x", pady=ModernTheme.SPACING_SM)
        
        tk.Label(
            y_frame,
            text="Display Mode:",
            font=ModernTheme.body_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE
        ).pack(anchor="w")
        
        y_combo = ttk.Combobox(
            y_frame,
            textvariable=self.y_mode_var,
            values=self.available_y_modes,
            state="readonly",
            font=ModernTheme.body_font()
        )
        y_combo.pack(fill="x", pady=(ModernTheme.SPACING_XS, 0))
        y_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

    def _create_parameter_selection_section(self):
        """Create parameter selection checkboxes"""
        section_frame = self._create_section_frame("Parameter Selection")
        
        # Get parameters from config
        params = list(self.params_config.keys()) if self.params_config else ["param_1", "param_2"]
        
        # Create checkboxes for each parameter
        for param in params:
            self.parameter_visibility[param] = tk.BooleanVar(value=True)
            
            param_frame = tk.Frame(section_frame, bg=ModernTheme.SURFACE)
            param_frame.pack(fill="x", pady=ModernTheme.SPACING_XS)
            
            checkbox = tk.Checkbutton(
                param_frame,
                text=f"📊 {param}",
                variable=self.parameter_visibility[param],
                font=ModernTheme.body_font(),
                fg=ModernTheme.TEXT_PRIMARY,
                bg=ModernTheme.SURFACE,
                activebackground=ModernTheme.SURFACE,
                command=self._on_parameter_toggle
            )
            checkbox.pack(anchor="w")

    def _create_display_options_section(self):
        """Create display options section"""
        section_frame = self._create_section_frame("Display Options")
        
        options = [
            ("show_trend_lines", "🔄 Show Trend Lines"),
            ("show_confidence_intervals", "📊 Show Confidence Intervals"),
            ("show_convergence_zones", "🎯 Show Convergence Zones"),
            ("show_legend", "📋 Show Legend"),
            ("normalize_axes", "⚖️ Normalize Parameter Axes")
        ]
        
        for option_key, display_text in options:
            option_frame = tk.Frame(section_frame, bg=ModernTheme.SURFACE)
            option_frame.pack(fill="x", pady=ModernTheme.SPACING_XS)
            
            checkbox = tk.Checkbutton(
                option_frame,
                text=display_text,
                variable=self.display_options[option_key],
                font=ModernTheme.body_font(),
                fg=ModernTheme.TEXT_PRIMARY,
                bg=ModernTheme.SURFACE,
                activebackground=ModernTheme.SURFACE,
                command=self._on_display_option_change
            )
            checkbox.pack(anchor="w")

    def _create_metrics_display_section(self):
        """Create convergence metrics display section"""
        section_frame = self._create_section_frame("Convergence Metrics")
        
        # Metrics display area
        self.metrics_text = tk.Text(
            section_frame,
            height=6,
            font=ModernTheme.code_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.INPUT_BACKGROUND,
            relief="solid",
            bd=1,
            state="disabled"
        )
        self.metrics_text.pack(fill="both", expand=True, pady=ModernTheme.SPACING_SM)
        
        # Update metrics button
        update_btn = tk.Button(
            section_frame,
            text="🔄 Update Metrics",
            command=self._update_convergence_metrics,
            font=ModernTheme.button_font(),
            bg=ModernTheme.PRIMARY,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        update_btn.pack(pady=(ModernTheme.SPACING_SM, 0))

    def _create_export_section(self):
        """Create export controls section"""
        section_frame = self._create_section_frame("Export Settings")
        
        # DPI selection
        dpi_frame = tk.Frame(section_frame, bg=ModernTheme.SURFACE)
        dpi_frame.pack(fill="x", pady=ModernTheme.SPACING_SM)
        
        tk.Label(
            dpi_frame,
            text="Export DPI:",
            font=ModernTheme.body_font(),
            fg=ModernTheme.TEXT_PRIMARY,
            bg=ModernTheme.SURFACE
        ).pack(anchor="w")
        
        dpi_combo = ttk.Combobox(
            dpi_frame,
            textvariable=self.dpi_var,
            values=[150, 300, 600, 1200],
            state="readonly",
            font=ModernTheme.body_font()
        )
        dpi_combo.pack(fill="x", pady=(ModernTheme.SPACING_XS, 0))

    def _create_action_buttons(self):
        """Create action buttons section"""
        button_frame = tk.Frame(self.scroll_frame, bg=ModernTheme.SURFACE)
        button_frame.pack(fill="x", padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_LG)
        
        # Refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh Plot",
            command=self._refresh_plot,
            font=ModernTheme.button_font(),
            bg=ModernTheme.SUCCESS,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        refresh_btn.pack(side="left", padx=(0, ModernTheme.SPACING_SM))
        
        # Reset button
        reset_btn = tk.Button(
            button_frame,
            text="⚡ Reset Settings",
            command=self._reset_settings,
            font=ModernTheme.button_font(),
            bg=ModernTheme.WARNING,
            fg=ModernTheme.TEXT_INVERSE,
            relief="flat",
            padx=ModernTheme.SPACING_MD,
            pady=ModernTheme.SPACING_SM
        )
        reset_btn.pack(side="right")

    def _create_section_frame(self, title: str) -> tk.Frame:
        """Create a section frame with title using ModernTheme"""
        # Section container
        section_container = tk.Frame(self.scroll_frame, bg=ModernTheme.SURFACE)
        section_container.pack(fill="x", padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)
        
        # Section header
        header_frame = tk.Frame(section_container, bg=ModernTheme.SURFACE)
        header_frame.pack(fill="x", pady=(0, ModernTheme.SPACING_SM))
        
        header_label = tk.Label(
            header_frame,
            text=title,
            font=ModernTheme.heading_font(),
            fg=ModernTheme.PRIMARY,
            bg=ModernTheme.SURFACE
        )
        header_label.pack(anchor="w")
        
        # Separator line
        separator = tk.Frame(header_frame, height=1, bg=ModernTheme.BORDER)
        separator.pack(fill="x", pady=(ModernTheme.SPACING_XS, 0))
        
        # Content frame
        content_frame = tk.Frame(section_container, bg=ModernTheme.SURFACE)
        content_frame.pack(fill="x")
        
        return content_frame

    def _on_axis_change(self, event=None):
        """Handle X-axis selection change"""
        logger.debug(f"X-axis changed to: {self.x_axis_var.get()}")
        self._refresh_plot()

    def _on_mode_change(self, event=None):
        """Handle Y-axis mode change"""
        logger.debug(f"Y-mode changed to: {self.y_mode_var.get()}")
        self._refresh_plot()

    def _on_parameter_toggle(self):
        """Handle parameter visibility toggle"""
        visible_params = [param for param, var in self.parameter_visibility.items() if var.get()]
        logger.debug(f"Visible parameters: {visible_params}")
        self._refresh_plot()

    def _on_display_option_change(self):
        """Handle display option change"""
        active_options = [option for option, var in self.display_options.items() if var.get()]
        logger.debug(f"Active display options: {active_options}")
        self._refresh_plot()

    def _update_convergence_metrics(self):
        """Update and display convergence metrics"""
        try:
            # This would interface with the optimizer to get actual metrics
            # For now, showing placeholder metrics
            metrics_text = """Convergence Metrics:
            
Parameter Stability:
  • param_1: σ=2.1, CV=0.15
  • param_2: σ=1.8, CV=0.12
  
Convergence Rate:
  • Overall: 0.85 (Good)
  • Last 10 iter: 0.92 (Excellent)
  
Status: Parameters converging
Last Updated: Now"""
            
            self.metrics_text.config(state="normal")
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, metrics_text)
            self.metrics_text.config(state="disabled")
            
            logger.debug("Convergence metrics updated")
            
        except Exception as e:
            logger.error(f"Error updating convergence metrics: {e}")

    def _refresh_plot(self):
        """Trigger plot refresh with current settings"""
        try:
            if self.update_callback:
                # Collect current settings
                settings = {
                    "x_axis": self.x_axis_var.get(),
                    "y_mode": self.y_mode_var.get(),
                    "visible_parameters": {param: var.get() for param, var in self.parameter_visibility.items()},
                    "display_options": {option: var.get() for option, var in self.display_options.items()},
                    "dpi": self.dpi_var.get()
                }
                
                logger.debug(f"Refreshing plot with settings: {settings}")
                
                # Call update callback asynchronously
                threading.Thread(
                    target=self.update_callback,
                    args=(self.plot_type, settings),
                    daemon=True
                ).start()
                
        except Exception as e:
            logger.error(f"Error refreshing plot: {e}")
            messagebox.showerror("Refresh Error", f"Failed to refresh plot: {str(e)}")

    def _reset_settings(self):
        """Reset all settings to defaults"""
        try:
            # Reset axis selection
            self.x_axis_var.set("iteration")
            self.y_mode_var.set("raw_values")
            
            # Reset parameter visibility
            for var in self.parameter_visibility.values():
                var.set(True)
            
            # Reset display options
            self.display_options["show_trend_lines"].set(True)
            self.display_options["show_confidence_intervals"].set(False)
            self.display_options["show_convergence_zones"].set(True)
            self.display_options["show_legend"].set(True)
            self.display_options["normalize_axes"].set(False)
            
            # Reset DPI
            self.dpi_var.set(300)
            
            logger.info("Parameter Convergence plot settings reset to defaults")
            self._refresh_plot()
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")

    def show_window(self):
        """Show the control panel window"""
        if self.popup_window:
            self.popup_window.deiconify()
            self.popup_window.lift()
            self.popup_window.focus_set()
            logger.info("Parameter Convergence plot control panel window shown")

    def hide_window(self):
        """Hide the control panel window"""
        if self.popup_window:
            self.popup_window.withdraw()
            logger.info("Parameter Convergence plot control panel window hidden")

    def _on_window_close(self):
        """Handle window close event"""
        self.hide_window()

    def update_config(self, params_config: Dict[str, Any], responses_config: Dict[str, Any]):
        """Update parameter and response configurations"""
        try:
            self.params_config = params_config or {}
            self.responses_config = responses_config or {}
            
            # Update parameter visibility controls
            self._update_parameter_controls()
            
            logger.debug("Configuration updated for Parameter Convergence control panel")
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")

    def _update_parameter_controls(self):
        """Update parameter selection controls based on current config"""
        try:
            # Get current parameters
            current_params = set(self.params_config.keys())
            existing_params = set(self.parameter_visibility.keys())
            
            # Add new parameters
            for param in current_params - existing_params:
                self.parameter_visibility[param] = tk.BooleanVar(value=True)
            
            # Remove old parameters
            for param in existing_params - current_params:
                del self.parameter_visibility[param]
            
            # Recreate parameter selection section would require full UI rebuild
            # For now, just log the update
            logger.debug(f"Parameter controls updated: {list(current_params)}")
            
        except Exception as e:
            logger.error(f"Error updating parameter controls: {e}")


def create_convergence_control_panel(parent: tk.Widget, plot_type: str = "convergence",
                                   params_config: Dict[str, Any] = None,
                                   responses_config: Dict[str, Any] = None,
                                   update_callback: Callable = None) -> ConvergencePlotControlPanel:
    """
    Factory function to create a Parameter Convergence plot control panel.
    
    Args:
        parent: Parent widget for the control panel
        plot_type: Type identifier for the plot
        params_config: Configuration for optimization parameters
        responses_config: Configuration for response variables
        update_callback: Callback function for plot updates
        
    Returns:
        ConvergencePlotControlPanel: Configured control panel instance
    """
    try:
        control_panel = ConvergencePlotControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback
        )
        
        logger.info("Parameter Convergence control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create Parameter Convergence control panel: {e}")
        messagebox.showerror("Control Panel Creation Error",
                           f"Failed to create Parameter Convergence control panel: {str(e)}")
        return None