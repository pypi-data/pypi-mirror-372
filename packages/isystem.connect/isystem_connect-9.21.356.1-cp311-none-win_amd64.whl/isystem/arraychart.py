#!/usr/bin/env python3
"""
Array Chart Plotter for Embedded Applications

This script provides a GUI for plotting arrays from embedded applications
using winIDEA SDK, PySide6, and matplotlib.
"""
import dataclasses
import sys
import argparse
import logging
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import yaml

DEFAULT_NUM_ELEMENTS = '1'

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QPushButton, QDialog, QComboBox, QLabel, QLineEdit, QCheckBox,
        QDialogButtonBox, QMessageBox, QInputDialog, QProgressDialog
    )
    from PySide6.QtCore import Qt, Signal, QThread, QObject
    from PySide6.QtGui import QCloseEvent
except ImportError:
    logging.error("PySide6 not available. Please install with: pip install PySide6")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.patches as patches
    import numpy as np
except ImportError:
    logging.error("matplotlib not available. Please install with: pip install matplotlib")
    sys.exit(1)

try:
    import isystem.connect as ic
except ImportError:
    logging.error("isystem.connect not available. Please install with: pip install isystem.connect")
    sys.exit(1)


# Global constants
ZOOM_FACTOR = 1.7
CONFIG_FILE = "arraychart_config.yaml"


@dataclass
class PlottedArray:
    """Configuration for an array to be plotted"""
    name: str
    start_index: str  # Can be numeric string as dec or hex, or variable name
    num_elements: str  # Can be numeric string as dec or hex, or variable name. Empty string means
    # get value from winIDEA.
    display_name: str = '' # For display in legend

    # these values are evaluated when the above strings change to optimize performance
    start_idx_int: int = 0
    num_elems_int: int = 1
    values: List[float] = dataclasses.field(default_factory=list)
    
    def __post_init__(self):
        self.display_name = (f"{self.name}[{self.start_index}={self.start_idx_int} : "
                             f"'{self.num_elements}'={self.num_elems_int}]")


@dataclass
class ViewSettings:
    """Data class for storing view settings"""
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    grid_enabled: bool = True
    points_enabled: bool = False
    crosshair_x: Optional[float] = None
    

def exc_to_ui_str(e: Exception) -> str:
    current = e
    msg = ''
    while current:
        if msg:
            msg += 'Caused by:\n'
        msg += (f"{type(current).__name__}: {current}\n")
        # Prefer __cause__ over __context__
        current = current.__cause__ or current.__context__

    return msg


class EmbeddedArrays:
    """Class to manage array data from embedded target"""
    
    def __init__(self):
        self.data_ctrl: Optional[ic.CDataController] = None
        self.data_ctrl2: ic.CDataController2 | None = None
        self.ide_ctrl: Optional[ic.CIDEController] = None
        self.connection_manager: Optional[ic.ConnectionMgr] = None
        self.target_arrays: List[PlottedArray] = []
        self.logger = logging.getLogger(__name__)  # TODO configure logger to use colors and source location
        
    def connect(self) -> bool:
        """Connect to embedded target"""
        try:
            self.connection_manager = ic.ConnectionMgr()
            self.connection_manager.connect()
            
            self.data_ctrl = ic.CDataController(self.connection_manager)
            self.data_ctrl2 = ic.CDataController2(self.connection_manager)
            self.ide_ctrl = ic.CIDEController(self.connection_manager)
            
            self.logger.info("Successfully connected to embedded target")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to embedded target: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from embedded target"""
        if self.connection_manager:
            try:
                self.connection_manager.disconnect()
                self.logger.info("Disconnected from embedded target")
            except Exception as e:
                self.logger.warning(f"Error during disconnect: {e}")
    
    def get_config_dir(self) -> str:
        """Get directory for saving configuration file"""
        if self.ide_ctrl:
            try:
                return self.ide_ctrl.getPath(ic.CIDEController.WORKSPACE_DIR)
            except Exception as e:
                self.logger.warning(f"Could not get IDE directory: {e}")
        return os.path.expanduser("~")

    def evaluate(self, plotted_arrays: List[PlottedArray], parent_widget=None) -> List[str]:
        """
        Checks for all arrays if size is not specified, max size is used as default.
        Then values are evaluated and cached.
        """
        if not plotted_arrays:
            return
            
        # Show progress dialog for large operations (>50 elements total)
        total_elements = 0
        for arr in plotted_arrays:
            if arr.num_elements:
                total_elements += self.resolve_array_size(arr.num_elements)
            else:
                # Assume large array if size not specified
                total_elements += 100

        show_progress = total_elements > 50
        
        progress_dialog = None
        if show_progress and parent_widget:
            progress_dialog = ProgressDialog(parent_widget)
            progress_dialog.setRange(0, 100)
            progress_dialog.show()
        
        try:
            errors = []
            for i, plotted_array in enumerate(plotted_arrays):
                if plotted_array.num_elements == '':
                    try:
                        expr = self.data_ctrl2.getExpressionType(0, plotted_array.name)
                    except Exception as e:
                        errors.append(f"Error for array '{plotted_array.name}': {exc_to_ui_str(e)}")
                        continue
                    ivar = expr.Expression()
                    if ivar.Type() == ic.IVariable.tArray:
                        plotted_array.num_elements = str(self.get_array_size(plotted_array.name) -
                                                         self.resolve_expression(plotted_array.start_index))
                    else:
                        plotted_array.num_elements = DEFAULT_NUM_ELEMENTS
                    self.data_ctrl2.release(expr)

                # Create progress callback for this array (fix closure issue)
                def make_progress_callback(array_name):
                    def progress_callback(current, total):
                        if progress_dialog:
                            progress_dialog.update_progress(array_name, current, total)
                    return progress_callback
                
                progress_cb = make_progress_callback(plotted_array.name) if progress_dialog else None
                self.cache_values_for_plotted_array(plotted_array, progress_cb)
                
        finally:
            if progress_dialog:
                progress_dialog.close()

    def get_array_size(self, array_name: str) -> int:
        """
        Calculates the size (number of elements) of an array on the target.

        This is done by evaluating the C expression 'sizeof(array) / sizeof(array[0])'.

        Args:
            data_ctrl: The isystem.connect DataController object.
            array_name: The name of the array variable (e.g., "g_myArray").

        Returns:
            The number of elements in the array as an integer, or None if the
            expression fails to evaluate (e.g., array does not exist).
        """
        # The C expression to calculate the number of elements in an array
        expression = f"sizeof({array_name}) / sizeof({array_name}[0])"
        self.logger.debug(f"Evaluating expression for size: '{expression}'")

        expression_result = self.data_ctrl.evaluate(ic.IConnectDebug.fRealTime, expression)
        array_size = expression_result.getInt()
        return array_size


    def read_array_values(self, array_name: str, start_index: int, count: int, 
                         progress_callback=None) -> list[float]:
        """
        Reads a specified number of values from an array on the target.

        It reads the values one by one starting from the given index.

        Args:
            array_name: The name of the array variable.
            start_index: The starting index from which to read.
            count: The number of elements to read.
            progress_callback: Optional callback function to report progress (current, total)

        Returns:
            A list of floats, where each float is the value of an array element.
            Returns an empty list if reading fails.
        """
        values = []
        self.logger.debug(f"Reading {count} element(s) from '{array_name}', "
                          f"starting at index {start_index}...")

        for i in range(start_index, start_index + count):
            expression = f"{array_name}[{i}]"
            try:
                expression_result = self.data_ctrl.evaluate(ic.IConnectDebug.fRealTime, expression)
                # getValue() returns the formatted string representation of the value,
                # which is robust for different data types (int, float, etc.).
                value = expression_result.getDouble()
                values.append(value)
                
                # Report progress if callback provided
                if progress_callback and (i % 100) == 0:
                    progress_callback(i - start_index, count)
                    
            except Exception as e:
                raise ValueError(f"Error reading element from array '{array_name}' at index {i}.")

        return values

    def read_available_arrays(self) -> List[PlottedArray]:
        """
        Get list of all available arrays in embedded application. This f.
        returns only names of global variables declared as arrays. It does not
        return pointers, arrays in structs, or local arrays in functions.
        """
        if not self.data_ctrl:
            return []
        try:
            # Get all global variables
            array_vars = ic.VariableVector()
            # TODO walk all partitions
            self.data_ctrl.getVariables(0, array_vars)
            embedded_array_names = []
            for c_var in array_vars:
                try:
                    array_size = c_var.getArrayDimension()  # always zero before SDK 2025-08-08
                    logging.debug(f"Reading array '{c_var.getName()}', num elements = {array_size}")
                    if c_var.getTypeAsEnum() == ic.IVariable.tArray:
                        num_elements = self.get_array_size(c_var.getName())
                        embedded_array_names.append(PlottedArray(name=c_var.getName(),
                                                                 start_index='0',  # default start
                                                                 num_elements=str(num_elements)))
                except Exception:
                    # Skip variables that can't be queried TODO make them known to the user
                    continue
            
            return embedded_array_names
        except Exception as e:
            self.logger.error(f"Error getting available arrays: {e}")
            return []

    def resolve_expression(self, expression: str) -> int:
        """Resolve expression to integer value - can be numeric or variable name"""
        try:
            # First try to parse as integer
            return int(expression)
        except ValueError:
            # If not numeric, try to evaluate as expression on target
            try:
                result = self.data_ctrl.evaluate(ic.IConnectDebug.fRealTime, expression)
                return result.getInt()
            except Exception as e:
                self.logger.error(f"Failed to resolve expression '{expression}': {e}")
                raise ValueError(f"Cannot resolve expression: {expression}")

    def resolve_array_size(self, num_elements: str) -> int:
        if num_elements:
            return self.resolve_expression(num_elements)
        return int(DEFAULT_NUM_ELEMENTS)

    # TODO read values only when start address or num elements change, add values to PlottedArray.
    def cache_values_for_plotted_array(self, array: PlottedArray, progress_callback=None):
        """Read array values based on ArrayConfig"""
        array.start_idx_int = self.resolve_expression(array.start_index)
        array.num_elems_int = self.resolve_array_size(array.num_elements)
        array.values = self.read_array_values(array.name, array.start_idx_int,
                                            array.num_elems_int, progress_callback)

    def get_array_config_size(self, config: PlottedArray) -> int:
        """Get effective size of array config"""
        try:
            return self.resolve_array_size(config.num_elements)
        except Exception:
            return 0


class ProgressDialog(QProgressDialog):
    """Custom progress dialog for array reading operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reading Array Data")
        self.setLabelText("Initializing...")
        self.setModal(True)
        self.setAutoClose(True)
        self.setAutoReset(False)
        self.setCancelButton(None)  # No cancel button for now
        self.setMinimumDuration(500)  # Show after 500ms
        
    def update_progress(self, array_name: str, current: int, total: int):
        """Update progress for current array being read"""
        self.setLabelText(f"Reading {array_name}: {current}/{total} elements")
        self.setValue(int(100 * current / total) if total > 0 else 0)
        QApplication.processEvents()  # Allow UI updates


class CrosshairCanvas(FigureCanvas):
    """Custom matplotlib canvas with crosshair functionality"""
    
    crosshair_moved = Signal(float, float)
    zoom_requested = Signal(float, float, bool)  # x, y, zoom_in
    pan_requested = Signal(str, float)  # direction ('vertical' or 'horizontal'), step
    
    def __init__(self, figure):
        super().__init__(figure)
        self.crosshair_x = None
        self.crosshair_y = None
        self.crosshair_lines = []
        self.text_annotations = []
        self.preview_mode = False
        
        # Mouse drag panning state
        self.panning = False
        self.pan_start_x = None
        self.pan_start_y = None
        self.pan_start_xlim = None
        self.pan_start_ylim = None
        
        # Data points for snapping
        self.plotted_arrays = []
        
        self.mpl_connect('button_press_event', self.on_button_press)
        self.mpl_connect('button_release_event', self.on_button_release)
        self.mpl_connect('motion_notify_event', self.on_motion)
        self.mpl_connect('scroll_event', self.on_scroll)
    
    def set_plotted_arrays(self, plotted_arrays):
        """Set the plotted arrays for crosshair snapping"""
        self.plotted_arrays = plotted_arrays
    
    def find_nearest_point(self, x: float, y: float) -> tuple[float, float]:
        """Find the nearest data point to the given coordinates"""
        if not self.plotted_arrays:
            return x, y

        index = int(round(x))
        min_delta = float('inf')
        closest_y_val = y

        for array in self.plotted_arrays:
            if array.start_idx_int <= index < (array.start_idx_int + array.num_elems_int):
                array_val = array.values[index - array.start_idx_int]
                delta = abs(y - array_val)
                if delta < min_delta:
                    min_delta = delta
                    closest_y_val = array_val

        return index, closest_y_val

        # min_distance = float('inf')
        # nearest_x = x
        # nearest_y = y
        #
        # # Get current axis limits for normalization
        # ax = self.figure.get_axes()[0] if self.figure.get_axes() else None
        # if not ax:
        #     return x, y
        #
        # xlim = ax.get_xlim()
        # ylim = ax.get_ylim()
        # x_range = xlim[1] - xlim[0]
        # y_range = ylim[1] - ylim[0]
        #
        # if x_range == 0 or y_range == 0:
        #     return x, y
        #
        # for array in self.plotted_arrays:
        #     if not array.values:
        #         continue
        #
        #     for i, value in enumerate(array.values):
        #         # Calculate the data point coordinates
        #         data_x = array.start_idx_int + i
        #         data_y = value
        #
        #         # Check if point is within reasonable range
        #         if xlim[0] <= data_x <= xlim[1] and ylim[0] <= data_y <= ylim[1]:
        #             # Calculate normalized distance (account for different scales)
        #             dx_norm = (x - data_x) / x_range
        #             dy_norm = (y - data_y) / y_range
        #             distance = dx_norm**2 + dy_norm**2
        #
        #             if distance < min_distance:
        #                 min_distance = distance
        #                 nearest_x = data_x
        #                 nearest_y = data_y
        #
        # return nearest_x, nearest_y

    def on_button_press(self, event):
        """Handle mouse button press events"""
        if event.inaxes and event.button == 1:  # Left click
            # Start panning mode
            self.panning = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata
            self.pan_start_xlim = event.inaxes.get_xlim()
            self.pan_start_ylim = event.inaxes.get_ylim()
            
            # Also update crosshair for single clicks
            if not hasattr(self, '_drag_started'):
                self._drag_started = False
    
    def on_button_release(self, event):
        """Handle mouse button release events"""
        if event.button == 1:  # Left click release
            # If we didn't drag (just a click), update crosshair with snapping
            if self.panning and not getattr(self, '_drag_started', False):
                if event.inaxes and event.xdata is not None and event.ydata is not None:
                    # Find nearest data point and snap to it
                    snap_x, snap_y = self.find_nearest_point(event.xdata, event.ydata)
                    self.update_crosshair(snap_x, snap_y)
                    self.crosshair_moved.emit(snap_x, snap_y)
            
            # End panning mode
            self.panning = False
            self.pan_start_x = None
            self.pan_start_y = None
            self.pan_start_xlim = None
            self.pan_start_ylim = None
            self._drag_started = False
    
    def on_motion(self, event):
        """Handle mouse motion for crosshair preview and panning"""
        if event.inaxes:
            if self.panning and self.pan_start_x is not None and self.pan_start_y is not None:
                # Dragging - perform panning
                self._drag_started = True

                # Calculate drag distance in data coordinates
                if event.xdata is not None and event.ydata is not None:
                    # take into account changed limits on draw()
                    current_xlim = event.inaxes.get_xlim()
                    current_ylim = event.inaxes.get_ylim()
                    xlim_delta = current_xlim[0] - self.pan_start_xlim[0]
                    ylim_delta = current_ylim[0] - self.pan_start_ylim[0]
                    dx = self.pan_start_x - event.xdata + xlim_delta
                    dy = self.pan_start_y - event.ydata + ylim_delta

                    # Apply pan to both axes
                    new_xlim = (self.pan_start_xlim[0] + dx, self.pan_start_xlim[1] + dx)
                    new_ylim = (self.pan_start_ylim[0] + dy, self.pan_start_ylim[1] + dy)
                    print(self.pan_start_xlim, self.pan_start_ylim, ' : ', new_xlim, new_ylim, dx, dy)
                    
                    event.inaxes.set_xlim(new_xlim)
                    event.inaxes.set_ylim(new_ylim)
                    self.draw()
            
            elif self.preview_mode:
                # Preview mode for crosshair
                self.update_crosshair(event.xdata, event.ydata, preview=True)
    
    def on_scroll(self, event):
        """Handle mouse scroll events for zooming and panning"""
        if not event.inaxes:
            return
            
        modifiers = event.modifiers or set()

        if not event.modifiers:
            # Plain scroll: pan vertically
            self.pan_requested.emit('vertical', event.step)
        elif 'shift' in modifiers:
            # Shift + scroll: pan vertically
            # when alt is pressed, no on_scroll event is triggered, so we have to use SHIFT key
            self.pan_requested.emit('horizontal', event.step)
        elif 'ctrl' in modifiers:
            # Ctrl + scroll: zoom in/out at mouse position
            zoom_in = event.step > 0
            self.zoom_requested.emit(event.xdata, event.ydata, zoom_in)

    def remove_crosshair_lines(self):
        for line in self.crosshair_lines:
            line.remove()
        for annotation in self.text_annotations:
            annotation.remove()

        self.crosshair_lines.clear()
        self.text_annotations.clear()


    def update_crosshair(self, x, y, preview=False):
        """Update crosshair position"""
        if not preview:
            self.crosshair_x = x
            self.crosshair_y = y
        
        self.remove_crosshair_lines()

        if x is not None and y is not None:
            ax = self.figure.get_axes()[0] if self.figure.get_axes() else None
            if ax:
                # Draw crosshair lines
                h_line = ax.axhline(y=y, color='red', linestyle='--', alpha=0.7)
                v_line = ax.axvline(x=x, color='red', linestyle='--', alpha=0.7)
                
                # Add a circle marker at the snapped point to show it's snapped to data
                snap_marker = ax.plot(x, y, 'ro', markersize=8, markerfacecolor='red', 
                                    markeredgecolor='white', markeredgewidth=2, alpha=0.8)[0]
                
                self.crosshair_lines = [h_line, v_line, snap_marker]
                
                # Add text annotation with coordinates
                text = f'Index: {int(x)}, Y: {y:.3f}'
                annotation = ax.annotate(text, xy=(x, y), xytext=(10, 10),
                                       textcoords='offset points',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
                self.text_annotations = [annotation]
        
        self.draw()


class AddArrayDialog(QDialog):
    """Dialog for adding arrays to the chart"""
    
    def __init__(self, available_arrays: List[PlottedArray], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Array")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Array name field (editable combo box)
        layout.addWidget(QLabel("Array name:"))
        self.combo_box = QComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.addItems([array.name for array in available_arrays])
        layout.addWidget(self.combo_box)
        
        # Start index field
        layout.addWidget(QLabel("Start index (number or variable name):"))
        self.start_index_edit = QLineEdit()
        self.start_index_edit.setText("0")
        self.start_index_edit.setPlaceholderText("e.g. 0, start_idx, sizeof(header)")
        layout.addWidget(self.start_index_edit)
        
        # Size field
        layout.addWidget(QLabel("Number of elements (number or variable name):"))
        self.size_edit = QLineEdit()
        self.size_edit.setPlaceholderText("e.g. 100, array_size, MAX_ELEMENTS")
        layout.addWidget(self.size_edit)
        
        # Help text
        help_label = QLabel("Note: For size, you can use expressions like 'sizeof(array)/sizeof(array[0])' "
                           " or target expressions (variables) to automatically calculate array size.")
        help_label.setStyleSheet("QLabel { color: gray; font-size: 9px; }")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Set default size when array name changes
        self.combo_box.currentTextChanged.connect(self.on_array_name_changed)
    
    def on_array_name_changed(self, array_name: str):
        """Update default size when array name changes"""
        if array_name and not self.size_edit.text():
            # Suggest automatic size calculation
            self.size_edit.setText(f"")  # empty value means get value from winIDEA for arrays
    
    def get_array(self) -> PlottedArray:
        """Get the configured ArrayConfig"""
        array_name = self.combo_box.currentText().strip()
        start_index = self.start_index_edit.text().strip() or "0"
        size = self.size_edit.text().strip()
        
        if not array_name:
            raise ValueError("Array name cannot be empty")
        if not start_index:
            start_index = 0

        return PlottedArray(
            name=array_name,
            start_index=start_index,
            num_elements=size
        )


class RemoveArrayDialog(QDialog):
    """Dialog for removing arrays from the chart"""
    
    def __init__(self, plotted_configs: List[PlottedArray], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove Array")
        self.setModal(True)
        self.plotted_configs = plotted_configs
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select an array to remove:"))
        
        self.combo_box = QComboBox()
        display_names = [config.display_name for config in plotted_configs]
        self.combo_box.addItems(display_names)
        layout.addWidget(self.combo_box)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_selected_array(self) -> PlottedArray:
        """Get the selected ArrayConfig"""
        index = self.combo_box.currentIndex()
        if 0 <= index < len(self.plotted_configs):
            return self.plotted_configs[index]
        return None


class ArrayChartWindow(QMainWindow):
    """Main window for the array chart application"""
    
    def __init__(self, initial_arrays: List[str], log_level: int):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.array_data = EmbeddedArrays()
        self.view_settings = ViewSettings()
        
        # Convert initial array names to ArrayConfig objects
        self.plotted_arrays: List[PlottedArray] = []
        for array_name in (initial_arrays or []):
            config = PlottedArray(
                name=array_name,
                start_index="0", 
                num_elements=f""
            )
            self.plotted_arrays.append(config)
        
        self.config_file_path = ""
        
        self.init_ui()
        self.setup_logging(log_level)
        
        if not self.connect_to_target():
            QMessageBox.critical(self, "Connection Error", 
                               "Failed to connect to winIDEA.")
            sys.exit(1)

        self.config_file_path = os.path.join(self.array_data.get_config_dir(), CONFIG_FILE)
        try:
            self.load_configuration()
            self.array_data.evaluate(self.plotted_arrays, self)
            self.update_plot(True)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 f"Exception: {exc_to_ui_str(e)}")

    
    def setup_logging(self, log_level: int):
        """Setup logging configuration"""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('arraychart.log')
            ]
        )
    
    def connect_to_target(self) -> bool:
        """Connect to the embedded target"""
        return self.array_data.connect()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Array Chart Plotter")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(12, 8))
        self.crosshair_canvas = CrosshairCanvas(self.figure)
        self.crosshair_canvas.crosshair_moved.connect(self.on_crosshair_moved)
        self.crosshair_canvas.zoom_requested.connect(self.on_zoom_requested)
        self.crosshair_canvas.pan_requested.connect(self.on_pan_requested)
        main_layout.addWidget(self.crosshair_canvas)
        
        # Create control buttons
        self.create_control_buttons(main_layout)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
    
    def create_control_buttons(self, main_layout):
        """Create all control buttons"""
        # First row of buttons
        button_layout1 = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_array)
        self.add_btn.setToolTip("Add a new array to the plot with custom range and size options")
        button_layout1.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_array)
        self.remove_btn.setToolTip("Remove an array from the current plot")
        button_layout1.addWidget(self.remove_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_plot)
        self.refresh_btn.setToolTip("Refresh array data from embedded target")
        button_layout1.addWidget(self.refresh_btn)
        
        self.goto_btn = QPushButton("Goto")
        self.goto_btn.clicked.connect(self.goto_index)
        self.goto_btn.setToolTip("Pan chart to show specific array index on the left side")
        button_layout1.addWidget(self.goto_btn)
        
        self.find_btn = QPushButton("Find")
        self.find_btn.clicked.connect(self.find_value)
        self.find_btn.setToolTip("Search for a specific value in all plotted arrays and mark with '*'")
        button_layout1.addWidget(self.find_btn)
        
        main_layout.addLayout(button_layout1)
        
        # Second row of buttons (zoom controls)
        button_layout2 = QHBoxLayout()
        
        self.zoom_h_in_btn = QPushButton(" 🔍←→")
        self.zoom_h_in_btn.clicked.connect(self.zoom_horizontal_in)
        self.zoom_h_in_btn.setToolTip("Zoom in horizontally")
        button_layout2.addWidget(self.zoom_h_in_btn)
        
        self.zoom_h_out_btn = QPushButton(" 🔍→←")
        self.zoom_h_out_btn.clicked.connect(self.zoom_horizontal_out)
        self.zoom_h_out_btn.setToolTip("Zoom out horizontally")
        button_layout2.addWidget(self.zoom_h_out_btn)
        
        self.zoom_h_full_btn = QPushButton("All ↔")
        self.zoom_h_full_btn.clicked.connect(self.zoom_horizontal_full)
        self.zoom_h_full_btn.setToolTip("Show full horizontal range of all plotted arrays")
        button_layout2.addWidget(self.zoom_h_full_btn)

        self.zoom_v_in_btn = QPushButton("🔍+ ↕")
        self.zoom_v_in_btn.clicked.connect(self.zoom_vertical_in)
        self.zoom_v_in_btn.setToolTip("Zoom in vertically")
        button_layout2.addWidget(self.zoom_v_in_btn)
        
        self.zoom_v_out_btn = QPushButton("🔍- ↕")
        self.zoom_v_out_btn.clicked.connect(self.zoom_vertical_out)
        self.zoom_v_out_btn.setToolTip("Zoom out vertically")
        button_layout2.addWidget(self.zoom_v_out_btn)
        
        self.zoom_v_full_btn = QPushButton("All ↕")
        self.zoom_v_full_btn.clicked.connect(self.zoom_vertical_full)
        self.zoom_v_full_btn.setToolTip("Show full vertical range of all plotted arrays")
        button_layout2.addWidget(self.zoom_v_full_btn)
        
        self.grid_checkbox = QCheckBox("Grid")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.toggled.connect(self.toggle_grid)
        self.grid_checkbox.setToolTip("Toggle grid lines on/off")
        button_layout2.addWidget(self.grid_checkbox)
        
        self.points_checkbox = QCheckBox("Points")
        self.points_checkbox.setChecked(False)
        self.points_checkbox.toggled.connect(self.toggle_points)
        self.points_checkbox.setToolTip("Show '+' markers at each data point")
        button_layout2.addWidget(self.points_checkbox)
        
        main_layout.addLayout(button_layout2)
        
        # Add help text for mouse controls
        help_text = QLabel("left click - crosshair (snaps to data), mouse drag - pan, mouse wheel - pan vert., Shift + mouse wheel - pan horiz., Ctrl + mouse wheel - zoom in/out")
        help_text.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        help_text.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(help_text)
    
    def add_array(self):
        """Add an array to the plot"""
        available_arrays = self.array_data.read_available_arrays()
        
        dialog = AddArrayDialog(available_arrays, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                new_plotted_array = dialog.get_array()
                
                # Check if this exact config already exists
                existing_config = next((array for array in self.plotted_arrays
                                      if (array.name == new_plotted_array.name)), None)
                
                if existing_config:
                    QMessageBox.information(self, "Array Already Added", 
                            f"Array configuration '{new_plotted_array.display_name}' is "
                            f"already being plotted")
                else:
                    self.array_data.evaluate([new_plotted_array], self)
                    self.plotted_arrays.append(new_plotted_array)
                    self.logger.info(f"Added array config: {new_plotted_array.display_name}")
                    self.update_plot()
            except ValueError as e:
                QMessageBox.warning(self, "Value Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add array: {e}")
    
    def remove_array(self):
        """Remove an array from the plot"""
        if not self.plotted_arrays:
            QMessageBox.warning(self, "No Arrays", "No arrays are currently plotted")
            return
        
        dialog = RemoveArrayDialog(self.plotted_arrays, self)
        if dialog.exec() == QDialog.Accepted:
            array_to_remove = dialog.get_selected_array()
            if array_to_remove and array_to_remove in self.plotted_arrays:
                self.plotted_arrays.remove(array_to_remove)
                self.logger.info(f"Removed array config: {array_to_remove.display_name}")
                self.update_plot(True)
    
    def refresh_plot(self):
        """Refresh the plot with current data"""
        self.logger.info("Refreshing plot")
        try:
            self.array_data.evaluate(self.plotted_arrays, self)
            # Store current view limits
            if self.ax.get_xlim() != (0.0, 1.0):  # Default limits
                self.view_settings.x_min, self.view_settings.x_max = self.ax.get_xlim()
            if self.ax.get_ylim() != (0.0, 1.0):  # Default limits
                self.view_settings.y_min, self.view_settings.y_max = self.ax.get_ylim()

            self.update_plot(True)
        except Exception as e:
            QMessageBox.critical(self, "Refresh plot error", f"{exc_to_ui_str(e)}")

    def goto_index(self):
        """Pan to a specific array index"""
        index, ok = QInputDialog.getInt(self, "Go To Index", 
                                       "Enter array index to start with:",
                                       value=0, minValue=0)
        if ok:
            self.logger.info(f"Going to index: {index}")
            current_xlim = self.ax.get_xlim()
            range_size = current_xlim[1] - current_xlim[0]
            self.ax.set_xlim(index, index + range_size)
            self.crosshair_canvas.draw()
    
    def find_value(self):
        """Find a value in the arrays and mark it"""
        value, ok = QInputDialog.getDouble(self, "Find Value",
                                          "Enter value to find in arrays:",
                                          decimals=6)
        if ok:
            self.logger.info(f"Finding value: {value}")
            self.mark_value_in_plot(value)
    
    def mark_value_in_plot(self, target_value: float):
        """Mark occurrences of a value in the plot"""
        # Clear previous markers
        for child in self.ax.get_children():
            if isinstance(child, plt.Line2D) and child.get_marker() == '*':
                child.remove()

        found_any = False
        for array in self.plotted_arrays:
            try:
                indices = []
                found_values = []

                for i, val in enumerate(array.values):
                    if abs(val - target_value) < 1e-6:  # Close enough for floating point
                        indices.append(i)
                        found_values.append(val)
                        found_any = True

                if indices:
                    self.ax.scatter(indices, found_values, marker='*', s=100,
                                  color='red', linewidths=2, label=f'{array.display_name} matches')
            except Exception as e:
                self.logger.warning(f"Error searching in {array.display_name}: {e}")
        
        if found_any:
            self.ax.legend()
            self.crosshair_canvas.draw()
        else:
            QMessageBox.information(self, "Value Not Found", 
                                  f"Value {target_value} not found in any plotted arrays")
    
    def zoom_horizontal_in(self):
        """Zoom in horizontally"""
        self._zoom_horizontal(1/ZOOM_FACTOR)
    
    def zoom_horizontal_out(self):
        """Zoom out horizontally"""
        self._zoom_horizontal(ZOOM_FACTOR)
    
    def zoom_horizontal_full(self):
        """Full zoom out horizontally"""
        if self.plotted_arrays:
            max_size = 0
            for array in self.plotted_arrays:
                try:
                    size = self.array_data.get_array_config_size(array)
                    if size > 0:
                        max_size = max(max_size, size)
                except Exception as e:
                    self.logger.warning(f"Error getting size for {array.display_name}: {e}")
            if max_size > 0:
                self.ax.set_xlim(0, max_size - 1)
                self.crosshair_canvas.draw()
    
    def zoom_vertical_in(self):
        """Zoom in vertically"""
        self._zoom_vertical(1/ZOOM_FACTOR)
    
    def zoom_vertical_out(self):
        """Zoom out vertically"""
        self._zoom_vertical(ZOOM_FACTOR)
    
    def zoom_vertical_full(self):
        """Full zoom out vertically"""
        if self.plotted_arrays:
            all_values = []
            for array in self.plotted_arrays:
                try:
                    all_values.extend(array.values)
                except Exception as e:
                    self.logger.warning(f"Error reading values for {array.display_name}: {e}")
            
            if all_values:
                min_val = min(all_values)
                max_val = max(all_values)
                margin = (max_val - min_val) * 0.1  # 10% margin
                self.ax.set_ylim(min_val - margin, max_val + margin)
                self.crosshair_canvas.draw()
    
    def _zoom_horizontal(self, factor: float):
        """Apply horizontal zoom by factor"""
        xlim = self.ax.get_xlim()
        center = (xlim[0] + xlim[1]) / 2
        range_size = (xlim[1] - xlim[0]) * factor
        self.ax.set_xlim(center - range_size/2, center + range_size/2)
        self.crosshair_canvas.draw()
    
    def _zoom_vertical(self, factor: float):
        """Apply vertical zoom by factor"""
        ylim = self.ax.get_ylim()
        center = (ylim[0] + ylim[1]) / 2
        range_size = (ylim[1] - ylim[0]) * factor
        self.ax.set_ylim(center - range_size/2, center + range_size/2)
        self.crosshair_canvas.draw()
    
    def _zoom_around_point(self, center_x: float, center_y: float, factor: float):
        """Zoom both axes around a specific point"""
        # Zoom horizontally around center_x
        xlim = self.ax.get_xlim()
        x_range = (xlim[1] - xlim[0]) * factor
        x_left_ratio = (center_x - xlim[0]) / (xlim[1] - xlim[0])
        new_x_min = center_x - x_range * x_left_ratio
        new_x_max = center_x + x_range * (1 - x_left_ratio)
        self.ax.set_xlim(new_x_min, new_x_max)
        
        # Zoom vertically around center_y
        ylim = self.ax.get_ylim()
        y_range = (ylim[1] - ylim[0]) * factor
        y_bottom_ratio = (center_y - ylim[0]) / (ylim[1] - ylim[0])
        new_y_min = center_y - y_range * y_bottom_ratio
        new_y_max = center_y + y_range * (1 - y_bottom_ratio)
        self.ax.set_ylim(new_y_min, new_y_max)
        
        self.crosshair_canvas.draw()
    
    def _pan_vertical(self, step: float):
        """Pan vertically based on scroll step"""
        ylim = self.ax.get_ylim()
        y_range = ylim[1] - ylim[0]
        # Scale pan distance to be proportional to current view range
        pan_distance = -step * y_range * 0.1  # 10% of visible range per scroll step
        new_y_min = ylim[0] - pan_distance
        new_y_max = ylim[1] - pan_distance
        self.ax.set_ylim(new_y_min, new_y_max)
        self.crosshair_canvas.draw()
    
    def _pan_horizontal(self, step: float):
        """Pan horizontally based on scroll step"""
        xlim = self.ax.get_xlim()
        x_range = xlim[1] - xlim[0]
        # Scale pan distance to be proportional to current view range
        pan_distance = step * x_range * 0.1  # 10% of visible range per scroll step
        new_x_min = xlim[0] - pan_distance
        new_x_max = xlim[1] - pan_distance
        self.ax.set_xlim(new_x_min, new_x_max)
        self.crosshair_canvas.draw()
    
    def toggle_grid(self, checked: bool):
        """Toggle grid on/off"""
        self.ax.grid(checked)
        self.view_settings.grid_enabled = checked
        self.crosshair_canvas.draw()
        self.logger.info(f"Grid {'enabled' if checked else 'disabled'}")
    
    def toggle_points(self, checked: bool):
        """Toggle data point markers on/off"""
        self.view_settings.points_enabled = checked
        self.update_plot(True)
        self.logger.info(f"Data points {'enabled' if checked else 'disabled'}")
    
    def on_crosshair_moved(self, x: float, y: float):
        """Handle crosshair movement"""
        if x is not None:
            self.view_settings.crosshair_x = x
            # Update crosshair annotation with values from all arrays
            # self.update_crosshair_annotation(x)
    
    def on_zoom_requested(self, x: float, y: float, zoom_in: bool):
        """Handle zoom requests from mouse wheel with Ctrl"""
        if x is not None and y is not None:
            factor = 1/ZOOM_FACTOR if zoom_in else ZOOM_FACTOR
            self._zoom_around_point(x, y, factor)
            self.logger.info(f"{'Zoomed in' if zoom_in else 'Zoomed out'} at ({x:.1f}, {y:.3f})")
    
    def on_pan_requested(self, direction: str, step: float):
        """Handle pan requests from mouse wheel"""
        if direction == 'vertical':   # TODO use enum
            self._pan_vertical(step)
        elif direction == 'horizontal':
            self._pan_horizontal(step)
    
    def update_crosshair_annotation(self, x: float):
        """Update crosshair annotation with array values at x position"""
        index = int(round(x))
        text_lines = [f"Index: {index}"]
        
        for array in self.plotted_arrays:
            try:
                # Check if the index falls within this array's range
                local_index = index - array.start_idx_int
                if 0 <= local_index < len(array.values):
                    value = array.values[local_index]
                    text_lines.append(f"{array.display_name}: {value:.6f}")
            except Exception as e:
                self.logger.debug(f"Error reading crosshair value for {array.display_name}: {e}")
        
        # Update the annotation text
        if hasattr(self.crosshair_canvas, 'text_annotations') and self.crosshair_canvas.text_annotations:
            self.crosshair_canvas.text_annotations[-1].set_text('\n'.join(text_lines))
            self.crosshair_canvas.draw()
    
    def update_plot(self, is_preserve_zoom: bool = False):
        """Update the plot with current array data"""
        if (is_preserve_zoom and self.ax.get_xlim() != (0.0, 1.0)
                and self.ax.get_xlim() != (0.0, 1.0)):  # Default limits
            self.view_settings.x_min, self.view_settings.x_max = self.ax.get_xlim()
            self.view_settings.y_min, self.view_settings.y_max = self.ax.get_ylim()

        self.crosshair_canvas.remove_crosshair_lines()
        self.ax.clear()
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Value")
        self.ax.grid(self.view_settings.grid_enabled)

        try:
            # Filter configs that can be read (basic validation)
            valid_arrays = []
            colors = ["red", "green", "blue", "violet", "cyan", "black", "gray",
                      "saddlebrown", "orange"]
            for i, array in enumerate(self.plotted_arrays):
                try:
                    # Test if we can resolve the config expressions
                    start_index = self.array_data.resolve_expression(array.start_index)
                    num_elements = self.array_data.resolve_array_size(array.num_elements)
                    valid_arrays.append(array)
                except Exception as e:
                    self.logger.warning(f"Removing invalid config {array.display_name}: {e}")
                    continue

                try:
                    if array.values:
                        indices = range(start_index, start_index + num_elements)
                        
                        # Determine plot style based on points setting
                        if self.view_settings.points_enabled:
                            # Plot line with '+' markers
                            self.ax.plot(indices, array.values, label=array.display_name,
                                       color=colors[i % len(colors)], linewidth=1,
                                       marker='+', markersize=10, markerfacecolor='black')
                        else:
                            # Plot line only
                            self.ax.plot(indices, array.values, label=array.display_name,
                                       color=colors[i % len(colors)], linewidth=1.5)
                except Exception as e:
                    self.logger.warning(f"Error plotting {array.display_name}: {e}")

            self.plotted_arrays = valid_arrays

            if self.plotted_arrays:
                self.ax.legend()

            # Restore view settings if preserving zoom
            if is_preserve_zoom and self.view_settings.x_min is not None:
                self.ax.set_xlim(self.view_settings.x_min, self.view_settings.x_max)
            if is_preserve_zoom and self.view_settings.y_min is not None:
                self.ax.set_ylim(self.view_settings.y_min, self.view_settings.y_max)

            # Restore crosshair if it was set
            if self.view_settings.crosshair_x is not None:
                self.crosshair_canvas.update_crosshair(self.view_settings.crosshair_x,
                                                       self.view_settings.crosshair_x)  # Use x for y as placeholder

            # Update crosshair canvas with plotted arrays for snapping
            self.crosshair_canvas.set_plotted_arrays(self.plotted_arrays)
            
            self.crosshair_canvas.draw()
            self.logger.info(f"Plot updated with {len(self.plotted_arrays)} arrays.")
        except Exception as e:
            logging.error("Error updating plot.", exc_info=e)
            QMessageBox.critical(self, "Update Plot Error", f"{exc_to_ui_str(e)}")

    
    def save_configuration(self):
        """Save current view settings to YAML file"""
        try:
            # Update view settings before saving
            if self.ax.get_xlim() != (0.0, 1.0):
                self.view_settings.x_min, self.view_settings.x_max = self.ax.get_xlim()
            if self.ax.get_ylim() != (0.0, 1.0):
                self.view_settings.y_min, self.view_settings.y_max = self.ax.get_ylim()
            # Convert ArrayConfig objects to dict for serialization
            array_list = []
            for config in self.plotted_arrays:
                array_list.append({
                    'name': config.name,
                    'start_index': config.start_index,
                    'size': config.num_elements,
                    'display_name': config.display_name
                })
            
            config_data = {  # TODO use pydantic
                'view_settings': {
                    # convert to py float, numpy float is stored with tags in yaml
                    'x_min': float(self.view_settings.x_min),
                    'x_max': float(self.view_settings.x_max),
                    'y_min': float(self.view_settings.y_min),
                    'y_max': float(self.view_settings.y_max),
                    'arrays': array_list,
                    'grid_enabled': self.view_settings.grid_enabled,
                    'points_enabled': self.view_settings.points_enabled,
                    'crosshair_x': self.view_settings.crosshair_x
                }
            }
            
            with open(self.config_file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            self.logger.info(f"Configuration saved to {self.config_file_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def load_configuration(self):
        """Load view settings from YAML file"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data and 'view_settings' in config_data:
                    vs = config_data['view_settings']
                    self.view_settings.x_min = vs.get('x_min')
                    self.view_settings.x_max = vs.get('x_max')
                    self.view_settings.y_min = vs.get('y_min')
                    self.view_settings.y_max = vs.get('y_max')
                    arrays = vs.get('arrays', [])
                    self.view_settings.grid_enabled = vs.get('grid_enabled', True)
                    self.view_settings.points_enabled = vs.get('points_enabled', False)
                    self.view_settings.crosshair_x = vs.get('crosshair_x')
                    
                    # Convert loaded array dicts back to ArrayConfig objects
                    for plotted_array in arrays:
                        if isinstance(plotted_array, dict):
                            # New format with ArrayConfig data
                            array = PlottedArray(
                                name=plotted_array.get('name', ''),
                                start_index=plotted_array.get('start_index', '0'),
                                num_elements=plotted_array.get('size', '1'),
                                display_name=plotted_array.get('display_name')
                            )
                        else:
                            # Legacy format - just array name strings
                            array_name = str(plotted_array)
                            array = PlottedArray(
                                name=array_name,
                                start_index="0",
                                num_elements="1"
                            )
                        
                        # Add if not already in plotted configs
                        existing = next((c for c in self.plotted_arrays
                                         if (c.name == array.name)), None)
                        if not existing:
                            self.plotted_arrays.append(array)
                    
                    # Update grid and points checkboxes
                    self.grid_checkbox.setChecked(self.view_settings.grid_enabled)
                    self.points_checkbox.setChecked(self.view_settings.points_enabled)
                    
                    self.logger.info(f"Configuration loaded from {self.config_file_path}")
        except Exception as e:
            self.logger.warning(f"Error loading configuration: {e}")
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        self.save_configuration()
        self.array_data.disconnect()
        event.accept()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Array Chart Plotter for Embedded Applications")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("arrays", nargs="*", help="Array names to plot")

    args = parser.parse_args()
    
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    app = QApplication(sys.argv)
    
    window = ArrayChartWindow(initial_arrays=args.arrays, log_level=log_level)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()