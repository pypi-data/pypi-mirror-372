"""
Unified Plot Controls Module - Consolidated Plot Control System
============================================================

This module consolidates all plot control panel implementations (plot_controls.py,
compact_controls.py, movable_controls.py) into a single, unified system using the
strategy pattern for different behaviors (windowed, embedded, draggable).

Key Features:
- Strategy pattern for different control behaviors
- Single codebase for all plot control types
- Consistent interface across all modes
- Backward compatibility with existing code
- Configurable appearance and behavior

Classes:
    PlotControlStrategy: Base strategy for control behaviors
    WindowedStrategy: Separate window controls (original plot_controls.py)
    EmbeddedStrategy: Embedded controls (compact_controls.py)
    DraggableStrategy: Draggable controls (movable_controls.py)
    UnifiedPlotControlPanel: Main unified control panel

Author: Multi-Objective Optimization Laboratory
Version: 3.7.0 - Unified Plot Controls System
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class PlotControlStrategy(ABC):
    """Base strategy class for different plot control behaviors."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def create_control_interface(self, parent, control_panel) -> tk.Widget:
        """Create the control interface using this strategy."""
        pass
    
    @abstractmethod
    def show_controls(self, control_panel):
        """Show the controls using this strategy."""
        pass
    
    @abstractmethod
    def hide_controls(self, control_panel):
        """Hide the controls using this strategy."""
        pass
    
    @abstractmethod
    def update_position(self, control_panel, x: int = None, y: int = None):
        """Update control position (if applicable)."""
        pass


class WindowedStrategy(PlotControlStrategy):
    """Strategy for separate window controls (like original plot_controls.py)."""
    
    def __init__(self):
        super().__init__("Windowed")
    
    def create_control_interface(self, parent, control_panel) -> tk.Widget:
        """Create separate window interface."""
        window = tk.Toplevel(parent)
        window.title(f"{control_panel.plot_type.replace('_', ' ').title()} Controls")
        window.geometry("300x400")
        window.withdraw()  # Start hidden
        
        # Create main frame
        main_frame = ttk.Frame(window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add window-specific controls
        self._create_control_widgets(main_frame, control_panel)
        
        return window
    
    def show_controls(self, control_panel):
        """Show the separate window."""
        if hasattr(control_panel, 'control_widget'):
            control_panel.control_widget.deiconify()
            control_panel.control_widget.lift()
    
    def hide_controls(self, control_panel):
        """Hide the separate window."""
        if hasattr(control_panel, 'control_widget'):
            control_panel.control_widget.withdraw()
    
    def update_position(self, control_panel, x: int = None, y: int = None):
        """Update window position."""
        if hasattr(control_panel, 'control_widget') and x is not None and y is not None:
            control_panel.control_widget.geometry(f"+{x}+{y}")
    
    def _create_control_widgets(self, parent, control_panel):
        """Create standard control widgets for windowed mode."""
        # Axis Range Controls
        range_frame = ttk.LabelFrame(parent, text="Axis Ranges")
        range_frame.pack(fill=tk.X, pady=5)
        
        self._create_axis_controls(range_frame, control_panel)
        
        # Plot Options
        options_frame = ttk.LabelFrame(parent, text="Plot Options")
        options_frame.pack(fill=tk.X, pady=5)
        
        self._create_plot_options(options_frame, control_panel)
        
        # Action Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Update Plot", 
                  command=control_panel.trigger_update).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset", 
                  command=control_panel.reset_controls).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Close", 
                  command=self.hide_controls).pack(side=tk.RIGHT, padx=2)
    
    def _create_axis_controls(self, parent, control_panel):
        """Create axis range controls."""
        for i, (axis, label) in enumerate([('x', 'X-Axis'), ('y', 'Y-Axis')]):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT)
            
            # Min value
            ttk.Label(frame, text="Min:").pack(side=tk.LEFT, padx=(10, 2))
            min_entry = ttk.Entry(frame, width=8, 
                                 textvariable=control_panel.axis_ranges[f'{axis}_min']['var'])
            min_entry.pack(side=tk.LEFT, padx=2)
            
            # Max value
            ttk.Label(frame, text="Max:").pack(side=tk.LEFT, padx=(10, 2))
            max_entry = ttk.Entry(frame, width=8,
                                 textvariable=control_panel.axis_ranges[f'{axis}_max']['var'])
            max_entry.pack(side=tk.LEFT, padx=2)
            
            # Auto checkbox
            auto_var = tk.BooleanVar(value=control_panel.axis_ranges[f'{axis}_min']['auto'])
            ttk.Checkbutton(frame, text="Auto", variable=auto_var,
                          command=lambda a=axis, v=auto_var: control_panel.toggle_auto_range(a, v.get())).pack(side=tk.LEFT, padx=(10, 2))
    
    def _create_plot_options(self, parent, control_panel):
        """Create plot-specific options."""
        # Grid
        grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Show Grid", variable=grid_var).pack(anchor=tk.W, padx=5)
        
        # Legend
        legend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Show Legend", variable=legend_var).pack(anchor=tk.W, padx=5)
        
        # Store variables for access
        control_panel.plot_options = {
            'grid': grid_var,
            'legend': legend_var
        }


class EmbeddedStrategy(PlotControlStrategy):
    """Strategy for embedded controls (like compact_controls.py)."""
    
    def __init__(self):
        super().__init__("Embedded")
    
    def create_control_interface(self, parent, control_panel) -> tk.Widget:
        """Create embedded control interface."""
        # Main control frame with border
        control_frame = tk.Frame(parent, bg='lightgray', relief='raised', bd=2)
        
        # Title bar
        title_frame = tk.Frame(control_frame, bg='darkgray')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, 
                              text=f"{control_panel.plot_type.replace('_', ' ').title()}", 
                              bg='darkgray', fg='white', font=('Arial', 8, 'bold'))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Minimize/maximize button
        toggle_button = tk.Button(title_frame, text="−", bg='darkgray', fg='white',
                                 font=('Arial', 8, 'bold'), relief='flat',
                                 command=lambda: self._toggle_minimized(control_panel))
        toggle_button.pack(side=tk.RIGHT, padx=2)
        
        # Content frame
        content_frame = tk.Frame(control_frame, bg='lightgray')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_compact_controls(content_frame, control_panel)
        
        # Store references for toggling
        control_panel._content_frame = content_frame
        control_panel._toggle_button = toggle_button
        control_panel._minimized = False
        
        return control_frame
    
    def show_controls(self, control_panel):
        """Show embedded controls."""
        if hasattr(control_panel, 'control_widget'):
            control_panel.control_widget.pack(fill=tk.X, padx=5, pady=2)
    
    def hide_controls(self, control_panel):
        """Hide embedded controls."""
        if hasattr(control_panel, 'control_widget'):
            control_panel.control_widget.pack_forget()
    
    def update_position(self, control_panel, x: int = None, y: int = None):
        """Position not applicable for embedded controls."""
        pass
    
    def _toggle_minimized(self, control_panel):
        """Toggle minimized state of embedded controls."""
        if control_panel._minimized:
            control_panel._content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            control_panel._toggle_button.config(text="−")
            control_panel._minimized = False
        else:
            control_panel._content_frame.pack_forget()
            control_panel._toggle_button.config(text="+")
            control_panel._minimized = True
    
    def _create_compact_controls(self, parent, control_panel):
        """Create compact control widgets."""
        # Compact axis controls
        axis_frame = tk.Frame(parent, bg='lightgray')
        axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(axis_frame, text="Range:", bg='lightgray', 
                font=('Arial', 8)).pack(side=tk.LEFT)
        
        # X range
        tk.Label(axis_frame, text="X:", bg='lightgray', 
                font=('Arial', 8)).pack(side=tk.LEFT, padx=(10, 2))
        x_entry = tk.Entry(axis_frame, width=6, font=('Arial', 8),
                          textvariable=control_panel.axis_ranges['x_min']['var'])
        x_entry.pack(side=tk.LEFT, padx=1)
        
        # Y range  
        tk.Label(axis_frame, text="Y:", bg='lightgray',
                font=('Arial', 8)).pack(side=tk.LEFT, padx=(5, 2))
        y_entry = tk.Entry(axis_frame, width=6, font=('Arial', 8),
                          textvariable=control_panel.axis_ranges['y_min']['var'])
        y_entry.pack(side=tk.LEFT, padx=1)
        
        # Compact buttons
        button_frame = tk.Frame(parent, bg='lightgray')
        button_frame.pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Update", font=('Arial', 8),
                 command=control_panel.trigger_update).pack(side=tk.LEFT, padx=1)
        tk.Button(button_frame, text="Reset", font=('Arial', 8),
                 command=control_panel.reset_controls).pack(side=tk.LEFT, padx=1)


class DraggableStrategy(PlotControlStrategy):
    """Strategy for draggable controls (like movable_controls.py)."""
    
    def __init__(self):
        super().__init__("Draggable")
    
    def create_control_interface(self, parent, control_panel) -> tk.Widget:
        """Create draggable control interface."""
        # Main control frame with border
        control_frame = tk.Frame(parent, bg='lightsteelblue', relief='raised', bd=2)
        
        # Title bar (draggable)
        title_frame = tk.Frame(control_frame, bg='steelblue', cursor='fleur')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, 
                              text=f"{control_panel.plot_type.replace('_', ' ').title()}", 
                              bg='steelblue', fg='white', font=('Arial', 8, 'bold'))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Close button
        close_button = tk.Button(title_frame, text="×", bg='steelblue', fg='white',
                               font=('Arial', 8, 'bold'), relief='flat',
                               command=lambda: self.hide_controls(control_panel))
        close_button.pack(side=tk.RIGHT, padx=2)
        
        # Content frame
        content_frame = tk.Frame(control_frame, bg='lightsteelblue')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_draggable_controls(content_frame, control_panel)
        self._setup_dragging(title_frame, control_panel)
        
        # Store references
        control_panel._title_frame = title_frame
        
        return control_frame
    
    def show_controls(self, control_panel):
        """Show draggable controls."""
        if hasattr(control_panel, 'control_widget'):
            control_panel.control_widget.place(x=100, y=100)
    
    def hide_controls(self, control_panel):
        """Hide draggable controls."""
        if hasattr(control_panel, 'control_widget'):
            control_panel.control_widget.place_forget()
    
    def update_position(self, control_panel, x: int = None, y: int = None):
        """Update draggable control position."""
        if hasattr(control_panel, 'control_widget') and x is not None and y is not None:
            control_panel.control_widget.place(x=x, y=y)
    
    def _setup_dragging(self, title_frame, control_panel):
        """Setup dragging behavior for the title frame."""
        control_panel._drag_start_x = 0
        control_panel._drag_start_y = 0
        
        def start_drag(event):
            control_panel._drag_start_x = event.x
            control_panel._drag_start_y = event.y
        
        def do_drag(event):
            if hasattr(control_panel, 'control_widget'):
                x = control_panel.control_widget.winfo_x() + event.x - control_panel._drag_start_x
                y = control_panel.control_widget.winfo_y() + event.y - control_panel._drag_start_y
                self.update_position(control_panel, x, y)
        
        title_frame.bind("<Button-1>", start_drag)
        title_frame.bind("<B1-Motion>", do_drag)
        
        # Also bind to title label
        for child in title_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.bind("<Button-1>", start_drag)
                child.bind("<B1-Motion>", do_drag)
    
    def _create_draggable_controls(self, parent, control_panel):
        """Create draggable control widgets."""
        # Similar to embedded but with draggable styling
        axis_frame = tk.Frame(parent, bg='lightsteelblue')
        axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(axis_frame, text="X Range:", bg='lightsteelblue',
                font=('Arial', 8)).pack(side=tk.TOP, anchor=tk.W)
        
        x_frame = tk.Frame(axis_frame, bg='lightsteelblue')
        x_frame.pack(fill=tk.X)
        
        tk.Entry(x_frame, width=8, font=('Arial', 8),
                textvariable=control_panel.axis_ranges['x_min']['var']).pack(side=tk.LEFT, padx=1)
        tk.Entry(x_frame, width=8, font=('Arial', 8),
                textvariable=control_panel.axis_ranges['x_max']['var']).pack(side=tk.LEFT, padx=1)
        
        # Y Range
        tk.Label(axis_frame, text="Y Range:", bg='lightsteelblue',
                font=('Arial', 8)).pack(side=tk.TOP, anchor=tk.W, pady=(5, 0))
        
        y_frame = tk.Frame(axis_frame, bg='lightsteelblue')
        y_frame.pack(fill=tk.X)
        
        tk.Entry(y_frame, width=8, font=('Arial', 8),
                textvariable=control_panel.axis_ranges['y_min']['var']).pack(side=tk.LEFT, padx=1)
        tk.Entry(y_frame, width=8, font=('Arial', 8),
                textvariable=control_panel.axis_ranges['y_max']['var']).pack(side=tk.LEFT, padx=1)
        
        # Buttons
        button_frame = tk.Frame(parent, bg='lightsteelblue')
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="Update", font=('Arial', 8),
                 command=control_panel.trigger_update).pack(side=tk.LEFT, padx=1)
        tk.Button(button_frame, text="Reset", font=('Arial', 8),
                 command=control_panel.reset_controls).pack(side=tk.LEFT, padx=1)


class UnifiedPlotControlPanel:
    """
    Unified plot control panel that supports multiple strategies for different behaviors.
    
    This replaces plot_controls.py, compact_controls.py, and movable_controls.py with
    a single, unified system using the strategy pattern.
    """
    
    def __init__(self, parent, plot_type: str, 
                 strategy: str = 'windowed',
                 params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, 
                 update_callback: Callable = None):
        """
        Initialize unified plot control panel.
        
        Args:
            parent: Parent widget
            plot_type: Type of plot ('pareto_front', 'parallel_coords', etc.)
            strategy: Control strategy ('windowed', 'embedded', 'draggable')
            params_config: Parameter configuration
            responses_config: Response configuration
            update_callback: Callback function for plot updates
        """
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.control_widget = None
        self.plot_options = {}
        
        # Initialize axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        # Set up strategy
        self.strategy = self._create_strategy(strategy)
        self._create_interface()
        
        logger.info(f"Unified plot control panel created: {plot_type} ({strategy} strategy)")
    
    def _create_strategy(self, strategy: str) -> PlotControlStrategy:
        """Create the appropriate strategy instance."""
        strategies = {
            'windowed': WindowedStrategy,
            'embedded': EmbeddedStrategy,
            'draggable': DraggableStrategy
        }
        
        if strategy not in strategies:
            logger.warning(f"Unknown strategy '{strategy}', using 'windowed'")
            strategy = 'windowed'
        
        return strategies[strategy]()
    
    def _create_interface(self):
        """Create the control interface using the selected strategy."""
        self.control_widget = self.strategy.create_control_interface(self.parent, self)
    
    def show(self):
        """Show the plot controls."""
        self.strategy.show_controls(self)
    
    def hide(self):
        """Hide the plot controls."""
        self.strategy.hide_controls(self)
    
    def toggle_visibility(self):
        """Toggle control visibility."""
        # This would need state tracking, simplified for now
        self.show()
    
    def update_position(self, x: int = None, y: int = None):
        """Update control position (if applicable for strategy)."""
        self.strategy.update_position(self, x, y)
    
    def trigger_update(self):
        """Trigger plot update via callback."""
        if self.update_callback:
            try:
                # Gather current settings
                settings = self.get_current_settings()
                self.update_callback(settings)
            except Exception as e:
                logger.error(f"Error in plot update callback: {e}")
    
    def reset_controls(self):
        """Reset controls to default values."""
        for axis_range in self.axis_ranges.values():
            axis_range['var'].set('auto')
            axis_range['auto'] = True
        
        # Reset plot options if they exist
        if hasattr(self, 'plot_options'):
            for option_var in self.plot_options.values():
                if hasattr(option_var, 'set'):
                    option_var.set(True)
    
    def toggle_auto_range(self, axis: str, auto: bool):
        """Toggle auto range for an axis."""
        self.axis_ranges[f'{axis}_min']['auto'] = auto
        self.axis_ranges[f'{axis}_max']['auto'] = auto
        
        if auto:
            self.axis_ranges[f'{axis}_min']['var'].set('auto')
            self.axis_ranges[f'{axis}_max']['var'].set('auto')
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current control settings."""
        settings = {
            'plot_type': self.plot_type,
            'axis_ranges': {},
            'plot_options': {}
        }
        
        # Get axis ranges
        for key, axis_range in self.axis_ranges.items():
            value = axis_range['var'].get()
            if value == 'auto' or axis_range['auto']:
                settings['axis_ranges'][key] = None
            else:
                try:
                    settings['axis_ranges'][key] = float(value)
                except ValueError:
                    settings['axis_ranges'][key] = None
        
        # Get plot options
        if hasattr(self, 'plot_options'):
            for key, option_var in self.plot_options.items():
                if hasattr(option_var, 'get'):
                    settings['plot_options'][key] = option_var.get()
        
        return settings


# Backward compatibility functions and aliases

def create_enhanced_plot_control_panel(parent, plot_type: str, **kwargs):
    """Backward compatibility for enhanced_plot_controls.py"""
    return UnifiedPlotControlPanel(parent, plot_type, strategy='windowed', **kwargs)

def create_compact_plot_control_panel(parent, plot_type: str, **kwargs):
    """Backward compatibility for compact_controls.py"""
    return UnifiedPlotControlPanel(parent, plot_type, strategy='embedded', **kwargs)

def create_movable_plot_control_panel(parent, plot_type: str, **kwargs):
    """Backward compatibility for movable_controls.py"""
    return UnifiedPlotControlPanel(parent, plot_type, strategy='draggable', **kwargs)


# Legacy class aliases for backward compatibility
EnhancedPlotControlPanel = lambda *args, **kwargs: UnifiedPlotControlPanel(*args, strategy='windowed', **kwargs)
CompactPlotControlPanel = lambda *args, **kwargs: UnifiedPlotControlPanel(*args, strategy='embedded', **kwargs)
MovablePlotControlPanel = lambda *args, **kwargs: UnifiedPlotControlPanel(*args, strategy='draggable', **kwargs)