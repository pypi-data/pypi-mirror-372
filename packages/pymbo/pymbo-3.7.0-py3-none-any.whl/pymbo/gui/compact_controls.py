"""
Compact Controls Module
Compact implementation of plot control panels that can be embedded in the main interface
with unified modern academic styling.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

# Import unified theme system
try:
    from .gui import ModernTheme
except ImportError:
    # Fallback theme class if import fails
    class ModernTheme:
        PRIMARY = "#2D7A8A"
        PRIMARY_DARK = "#1E5A66"
        PRIMARY_LIGHT = "#E8F4F6"
        SURFACE = "#FDFCFA"
        PANEL = "#F5F3F0"
        TEXT_PRIMARY = "#2F2B26"
        TEXT_SECONDARY = "#6B645C"
        TEXT_INVERSE = "#FDFCFA"
        BORDER = "#D6D1CC"
        INPUT_BACKGROUND = "#FDFCFA"
        INPUT_BORDER = "#C4BEAA"
        SPACING_XS = 4
        SPACING_SM = 8
        SPACING_MD = 12
        
        @classmethod
        def small_font(cls):
            return ("Segoe UI", 9, "normal")
        
        @classmethod
        def button_font(cls):
            return ("Segoe UI", 9, "normal")
        
        @classmethod
        def heading_font(cls, size=10):
            return ("Segoe UI", size, "bold")

logger = logging.getLogger(__name__)


class CompactPlotControlPanel:
    """Compact plot control panel that can be embedded in the main interface"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.control_frame = None
        self.axis_ranges = {}
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        self.create_controls()
        logger.info(f"Compact plot control panel created for {plot_type}")
    
    def create_controls(self):
        """Create the compact control panel with modern academic styling"""
        # Main control frame with professional card styling
        self.control_frame = tk.Frame(
            self.parent,
            bg=ModernTheme.SURFACE,
            relief="flat",
            borderwidth=1,
            highlightbackground=ModernTheme.BORDER,
            highlightthickness=1
        )
        
        # Modern title bar with academic colors
        title_frame = tk.Frame(
            self.control_frame, 
            bg=ModernTheme.PRIMARY,
            height=28
        )
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # Title label with professional typography
        title_label = tk.Label(
            title_frame, 
            text=f"{self.plot_type.replace('_', ' ').title()}", 
            bg=ModernTheme.PRIMARY,
            fg=ModernTheme.TEXT_INVERSE,
            font=ModernTheme.heading_font(10)
        )
        title_label.pack(side=tk.LEFT, padx=ModernTheme.SPACING_SM, pady=4)
        
        # Modern close button with hover effects
        close_btn = tk.Button(
            title_frame, 
            text='✕', 
            command=self.hide,
            bg=ModernTheme.PRIMARY,
            fg=ModernTheme.TEXT_INVERSE,
            bd=0,
            relief="flat",
            font=ModernTheme.small_font(),
            width=3,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=4, pady=4)
        
        # Add hover effects for close button
        def on_close_enter(e):
            close_btn.config(bg=ModernTheme.PRIMARY_DARK)
        
        def on_close_leave(e):
            close_btn.config(bg=ModernTheme.PRIMARY)
        
        close_btn.bind("<Enter>", on_close_enter)
        close_btn.bind("<Leave>", on_close_leave)
        
        # Modern content frame with proper spacing
        content_frame = tk.Frame(
            self.control_frame, 
            bg=ModernTheme.SURFACE
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.SPACING_MD, pady=ModernTheme.SPACING_MD)
        
        # Compact axis controls
        self._create_compact_axis_controls(content_frame)
        
        # Action buttons
        self._create_compact_buttons(content_frame)
    
    def _create_compact_axis_controls(self, parent):
        """Create compact axis range controls with modern styling"""
        # X-axis row with proper academic spacing
        x_frame = tk.Frame(parent, bg=ModernTheme.SURFACE)
        x_frame.pack(fill=tk.X, pady=ModernTheme.SPACING_XS)
        
        # X-axis label with modern typography
        tk.Label(
            x_frame, 
            text="X:", 
            bg=ModernTheme.SURFACE, 
            fg=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.small_font()
        ).pack(side=tk.LEFT)
        
        # X-min entry with modern styling
        x_min_entry = tk.Entry(
            x_frame, 
            textvariable=self.axis_ranges['x_min']['var'],
            width=8,
            font=ModernTheme.small_font(),
            bg=ModernTheme.INPUT_BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            highlightbackground=ModernTheme.INPUT_BORDER,
            highlightthickness=1
        )
        x_min_entry.pack(side=tk.LEFT, padx=ModernTheme.SPACING_XS)
        
        # "to" label
        tk.Label(
            x_frame, 
            text="to", 
            bg=ModernTheme.SURFACE, 
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.small_font()
        ).pack(side=tk.LEFT)
        
        # X-max entry with modern styling
        x_max_entry = tk.Entry(
            x_frame, 
            textvariable=self.axis_ranges['x_max']['var'],
            width=8,
            font=ModernTheme.small_font(),
            bg=ModernTheme.INPUT_BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            highlightbackground=ModernTheme.INPUT_BORDER,
            highlightthickness=1
        )
        x_max_entry.pack(side=tk.LEFT, padx=ModernTheme.SPACING_XS)
        
        # Y-axis row with proper academic spacing
        y_frame = tk.Frame(parent, bg=ModernTheme.SURFACE)
        y_frame.pack(fill=tk.X, pady=ModernTheme.SPACING_XS)
        
        # Y-axis label with modern typography
        tk.Label(
            y_frame, 
            text="Y:", 
            bg=ModernTheme.SURFACE, 
            fg=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.small_font()
        ).pack(side=tk.LEFT)
        
        # Y-min entry with modern styling
        y_min_entry = tk.Entry(
            y_frame, 
            textvariable=self.axis_ranges['y_min']['var'],
            width=8,
            font=ModernTheme.small_font(),
            bg=ModernTheme.INPUT_BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            highlightbackground=ModernTheme.INPUT_BORDER,
            highlightthickness=1
        )
        y_min_entry.pack(side=tk.LEFT, padx=ModernTheme.SPACING_XS)
        
        # "to" label
        tk.Label(
            y_frame, 
            text="to", 
            bg=ModernTheme.SURFACE, 
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.small_font()
        ).pack(side=tk.LEFT)
        
        # Y-max entry with modern styling
        y_max_entry = tk.Entry(
            y_frame, 
            textvariable=self.axis_ranges['y_max']['var'],
            width=8,
            font=ModernTheme.small_font(),
            bg=ModernTheme.INPUT_BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            highlightbackground=ModernTheme.INPUT_BORDER,
            highlightthickness=1
        )
        y_max_entry.pack(side=tk.LEFT, padx=ModernTheme.SPACING_XS)
    
    def _create_compact_buttons(self, parent):
        """Create compact action buttons with modern academic styling"""
        button_frame = tk.Frame(parent, bg=ModernTheme.SURFACE)
        button_frame.pack(fill=tk.X, pady=ModernTheme.SPACING_SM)
        
        # Auto scale button with modern primary styling
        auto_btn = tk.Button(
            button_frame, 
            text="Auto", 
            command=self._auto_scale,
            bg=ModernTheme.PRIMARY,
            fg=ModernTheme.TEXT_INVERSE,
            activebackground=ModernTheme.PRIMARY_DARK,
            activeforeground=ModernTheme.TEXT_INVERSE,
            font=ModernTheme.button_font(),
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            pady=4,
            padx=12,
            width=8
        )
        auto_btn.pack(side=tk.LEFT, padx=ModernTheme.SPACING_XS)
        
        # Add hover effects for auto button
        def on_auto_enter(e):
            auto_btn.config(bg=ModernTheme.PRIMARY_DARK)
        
        def on_auto_leave(e):
            auto_btn.config(bg=ModernTheme.PRIMARY)
        
        auto_btn.bind("<Enter>", on_auto_enter)
        auto_btn.bind("<Leave>", on_auto_leave)
        
        # Refresh button with modern secondary styling
        refresh_btn = tk.Button(
            button_frame, 
            text="Refresh", 
            command=self._refresh_plot,
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.PRIMARY,
            activebackground=ModernTheme.PRIMARY_LIGHT,
            activeforeground=ModernTheme.PRIMARY_DARK,
            font=ModernTheme.button_font(),
            relief="solid",
            borderwidth=1,
            cursor="hand2",
            pady=4,
            padx=12,
            width=8,
            highlightbackground=ModernTheme.BORDER
        )
        refresh_btn.pack(side=tk.RIGHT, padx=ModernTheme.SPACING_XS)
        
        # Add hover effects for refresh button
        def on_refresh_enter(e):
            refresh_btn.config(bg=ModernTheme.PRIMARY_LIGHT)
        
        def on_refresh_leave(e):
            refresh_btn.config(bg=ModernTheme.SURFACE)
        
        refresh_btn.bind("<Enter>", on_refresh_enter)
        refresh_btn.bind("<Leave>", on_refresh_leave)
    
    def _on_axis_change(self, event=None):
        """Handle axis range changes - update plot immediately"""
        logger.info(f"Axis range changed for {self.plot_type}")
        # Update auto flags based on current values
        for axis_key in self.axis_ranges:
            value = self.axis_ranges[axis_key]['var'].get()
            self.axis_ranges[axis_key]['auto'] = value.lower() == 'auto'
        
        # Trigger plot update
        self._refresh_plot()
    
    def _auto_scale(self):
        """Reset axis ranges to auto"""
        for axis in self.axis_ranges:
            self.axis_ranges[axis]['var'].set('auto')
            self.axis_ranges[axis]['auto'] = True
        logger.info(f"Auto scale applied for {self.plot_type}")
        # Immediately refresh plot
        self._refresh_plot()
    
    def _refresh_plot(self):
        """Refresh the plot with current settings"""
        logger.info(f"Plot refresh requested for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Update callback executed for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error calling update callback for {self.plot_type}: {e}")
        else:
            logger.warning(f"No update callback available for {self.plot_type}")
    
    def show(self):
        """Show the compact control panel"""
        if self.control_frame:
            self.control_frame.place(x=10, y=10, width=180, height=100)
        logger.info(f"Compact control panel shown for {self.plot_type}")
    
    def hide(self):
        """Hide the compact control panel"""
        if self.control_frame:
            self.control_frame.place_forget()
        logger.info(f"Compact control panel hidden for {self.plot_type}")
    
    def place(self, **kwargs):
        """Place the control frame"""
        if self.control_frame:
            self.control_frame.place(**kwargs)
    
    def get_axis_ranges(self):
        """Get current axis range settings"""
        ranges = {}
        
        # Collect min/max values for each axis
        x_min_val, x_max_val, x_auto = self._get_axis_value('x_min')
        y_min_val, y_max_val, y_auto = self._get_axis_value('y_min')
        
        # Format for main GUI expectation: (min_val, max_val, is_auto)
        ranges['x_axis'] = (x_min_val, x_max_val, x_auto)
        ranges['y_axis'] = (y_min_val, y_max_val, y_auto)
        
        return ranges
    
    def _get_axis_value(self, axis_key):
        """Helper to get axis values and determine if auto"""
        if axis_key.endswith('_min'):
            base_axis = axis_key[:-4]  # Remove '_min'
            min_value = self.axis_ranges[f'{base_axis}_min']['var'].get()
            max_value = self.axis_ranges[f'{base_axis}_max']['var'].get()
            
            min_auto = min_value.lower() == 'auto'
            max_auto = max_value.lower() == 'auto'
            is_auto = min_auto or max_auto
            
            try:
                min_val = None if min_auto else float(min_value)
                max_val = None if max_auto else float(max_value)
            except ValueError:
                min_val = max_val = None
                is_auto = True
                
            return min_val, max_val, is_auto
        return None, None, True


def create_compact_plot_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                     responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> CompactPlotControlPanel:
    """Factory function to create a compact plot control panel"""
    try:
        # For complex plots like 3D Surface and GP Uncertainty, redirect to window controls
        # since compact controls would be too cramped for all the options
        if plot_type == 'surface_3d' or '3d' in plot_type.lower() or 'surface' in plot_type.lower():
            try:
                from .surface_3d_controls import create_surface_3d_control_panel
                logger.info(f"Using specialized 3D Surface controls instead of compact for {plot_type}")
                return create_surface_3d_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("3D Surface controls not available, using standard compact controls")
        
        elif plot_type == 'gp_uncertainty' or 'uncertainty' in plot_type.lower():
            try:
                from .gp_uncertainty_controls import create_gp_uncertainty_control_panel
                logger.info(f"Using specialized GP Uncertainty controls instead of compact for {plot_type}")
                return create_gp_uncertainty_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("GP Uncertainty controls not available, using standard compact controls")
        
        elif plot_type == 'sensitivity_analysis' or 'sensitivity' in plot_type.lower():
            try:
                from .sensitivity_analysis_controls import create_sensitivity_analysis_control_panel
                logger.info(f"Using specialized Sensitivity Analysis controls instead of compact for {plot_type}")
                return create_sensitivity_analysis_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("Sensitivity Analysis controls not available, using standard compact controls")
        
        # Default to standard compact controls for other plot types
        control_panel = CompactPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created compact plot control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating compact plot control panel for {plot_type}: {e}")
        raise