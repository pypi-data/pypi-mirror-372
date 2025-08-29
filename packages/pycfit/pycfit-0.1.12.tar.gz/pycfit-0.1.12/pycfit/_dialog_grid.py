import re
import numpy as np
import pyqtgraph as pg
from copy import deepcopy
from qtpy.uic import loadUi
from qtpy import QtCore, QtWidgets
from pyqtspinner import WaitingSpinner
from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QApplication, QWidget
from qtpy.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from ._dialog import FitDialog
from ._function import FunctionFitter

class mySpinWorker(QtCore.QThread):
    finished = QtCore.Signal()  # Signal emitted when work is done

    def __init__(self, long_task):
        super().__init__()
        self.long_task = long_task

    def run(self):
        self.long_task()
        self.finished.emit()  # Notify when done


class GridDialog(QDialog):
    """ Dialog box to edit function and fit to data """
    def __init__(self, grid_model, parent=None, init_ap=None):
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/GridFit.ui'), self)
        # self.setFixedSize(self.size())
        self.make_responsive()
        self._current_screen = QApplication.screenAt(self.pos())   # Track current screen for DPI changes

        self.GM = grid_model
        if init_ap is None:
            data_shape = self.GM._intensity.shape
            init_lambda = int(data_shape[0] / 2)
            init_x = int(data_shape[1] / 2)
            init_y = int(data_shape[2] / 2)
            self.lambda_index.setText(f'{init_lambda}')
            self.x_index.setText(f'{init_x}')
            self.y_index.setText(f'{init_y}')
            self.GM._analysis_point.set_point((init_lambda, init_x, init_y)) # Midpoint inidices, rounded down when odd
        else:
            self.GM._analysis_point.set_point(init_ap)
        
        self.generate_mask_list()
        self.initial_mask = self.mask_list.copy()
        self.set_range_labels()
        self.populate_comboBox_centralColumn()
        self.generate_graphs_all()
        self.draw_all_ap_crosshairs()

        # Attach the spinner to the dialog
        self.spinner = WaitingSpinner(
                self,
                disable_parent_when_spinning = True,
                roundness = 100.0,
                fade = 80.0,
                lines = 20,
                line_length = 16,
                line_width = 5,
                radius = 17,
                color = 'orange')

        # Connect controllers
        self.button_setPoint.clicked.connect(self.set_point)
        self.checkBox_maskPoint.clicked.connect(self.mask_point)
        self.button_redoFit_point.clicked.connect(self.redo_fit_point)
        self.button_redoFit_grid.clicked.connect(self.start_redo_fit_grid)
        self.button_showMaskedPoints.clicked.connect(self.view_masked_points)

        self.comboBox_origdata_slice_varx.currentTextChanged.connect(self.new_slice_axis)
        self.comboBox_origdata_slice_vary.currentTextChanged.connect(self.new_slice_axis)
        self.comboBox_selectvar_slice_varx.currentTextChanged.connect(self.new_slice_axis)
        self.comboBox_selectvar_slice_vary.currentTextChanged.connect(self.new_slice_axis)
        self.comboBox_residuals_slice_varx.currentTextChanged.connect(self.new_slice_axis)
        self.comboBox_residuals_slice_vary.currentTextChanged.connect(self.new_slice_axis)

        self.comboBox_origdata_line_varx.currentTextChanged.connect(self.new_line_axis)
        self.comboBox_selectvar_line_varx.currentTextChanged.connect(self.new_line_axis)
        self.comboBox_residuals_line_varx.currentTextChanged.connect(self.new_line_axis)

        self.comboBox_centralColumn_displayChoice.currentTextChanged.connect(self.generate_central_column)

        # self.graph_spectra_fit.scene().sigMouseClicked.connect(self.click_event)
        self.graph_origdata_slice.scene().sigMouseClicked.connect(self.click_event)
        self.graph_selectvar_slice.scene().sigMouseClicked.connect(self.click_event)
        self.graph_residuals_slice.scene().sigMouseClicked.connect(self.click_event)
        self.graph_origdata_line.scene().sigMouseClicked.connect(self.click_event)
        self.graph_selectvar_line.scene().sigMouseClicked.connect(self.click_event)
        self.graph_residuals_line.scene().sigMouseClicked.connect(self.click_event)

    
    def get_dpi_scale_factor(self):
        """Get current screen's DPI scaling factor"""
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        return screen.logicalDotsPerInch() / 96.0  # 96 DPI is the standard baseline
    
    def get_effective_screen_size(self):
        """Get screen size adjusted for DPI"""
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        dpi_scale = self.get_dpi_scale_factor()
        
        # Return "logical" screen size (what the user perceives)
        return {
            'width': int(geometry.width() / dpi_scale),
            'height': int(geometry.height() / dpi_scale),
            'physical_width': geometry.width(),  # Actual pixels
            'physical_height': geometry.height(),
            'dpi_scale': dpi_scale
        }
    
    def make_responsive(self):
        self.setFixedSize(16777215, 16777215)
        
        for widget in self.findChildren(QWidget):
            widget.setMaximumSize(16777215, 16777215)
        
        # Use DPI-aware sizing
        screen_info = self.get_effective_screen_size()
        
        # Base your sizing on "logical" dimensions
        logical_width = int(screen_info['width'] * 0.7)
        logical_height = int(screen_info['height'] * 0.8)
        
        # But apply using physical pixels
        physical_width = int(logical_width * screen_info['dpi_scale'])
        physical_height = int(logical_height * screen_info['dpi_scale'])
        
        self.resize(physical_width, physical_height)


    def adjust_internal_widgets(self):
        """Adjust internal widgets with DPI awareness"""
        dpi_scale = self.get_dpi_scale_factor()

        base_button_height = 30  # "logical" pixels
        physical_button_height = int(base_button_height * dpi_scale)
        y_margin = int(0.25 * physical_button_height)
        x_margin = y_margin
        
        # Dynamic Layouts
        main_height = self.height() - (3*y_margin) - physical_button_height
        btn_width = self.buttonBox.width()
        self.layoutWidget.setGeometry(x_margin, y_margin, self.width() - (2*x_margin), 
                                      main_height)
        self.buttonBox.move(self.width() - btn_width - x_margin,
                            main_height + y_margin + y_margin)

        # # Size elements that need consistent "physical" size across monitors (Buttons, Textboxes)
        self.buttonBox.setFixedHeight(physical_button_height)

    def resizeEvent(self, event):
            """Override the built-in resize event handler"""
            self.adjust_internal_widgets()

    def moveEvent(self, event):
        """Handle moving between screens with different DPI"""
        current_screen = QApplication.screenAt(self.pos())
        
        # Recalculate sizes for new screen's DPI
        if current_screen and current_screen != self._current_screen:
            self.make_responsive()
            self.adjust_internal_widgets()
            self._current_screen = current_screen


    def get_results(self):
        """
        Return a simple structure holding the model description and the 
        parameter arrays for each x,y grid point.
        Masked points will have np.nan parameter values
        """
        return self.GM.get_results()


    def set_point(self, lambda_index=None, x_index=None, y_index=None, from_text=True):
        if from_text:
            # TODO: Add check for valid input
            lambda_index = int(self.lambda_index.text())
            x_index = int(self.x_index.text())
            y_index = int(self.y_index.text())
        else:
            if lambda_index is None:
                lambda_index = self.GM._analysis_point.get_index('lambda_index')
            if x_index is None:
                x_index = self.GM._analysis_point.get_index('x_index')
            if y_index is None:
                y_index = self.GM._analysis_point.get_index('y_index')
            self.lambda_index.setText(f'{lambda_index}')
            self.x_index.setText(f'{x_index}')
            self.y_index.setText(f'{y_index}')
        
        self.GM._analysis_point.set_point([lambda_index, x_index, y_index])        
        self.set_current_point_label()
        self.generate_graphs_all()
        self.draw_all_ap_crosshairs()
        self.set_mask_checkbox_state()
    
    def mask_point(self):
        _, mask_x, mask_y = self.GM._analysis_point.get_point()
        self.GM._toggle_mask((mask_x, mask_y))
        if (mask_x, mask_y) not in self.mask_list:
            self.mask_list.append((mask_x, mask_y))
        else:
            self.mask_list.remove((mask_x, mask_y))

    def set_mask_checkbox_state(self):
        ap = self.GM._analysis_point.get_point()
        ap_xy = (ap[1], ap[2])
        if ap_xy in self.mask_list:
            self.checkBox_maskPoint.setChecked(True)
            # if ap_xy in self.initial_mask:
            #     self.checkBox_maskPoint.setEnabled(False)
            # else:
            #     self.checkBox_maskPoint.setEnabled(True)
        else:
            self.checkBox_maskPoint.setChecked(False)
            # self.checkBox_maskPoint.setEnabled(True)

    def generate_mask_list(self):   #TODO -- remove looping?
        mask_shape = self.GM.shape
        self.mask_list = []
        for li in range(mask_shape[0]):
            for xi in range(mask_shape[1]):
                    if self.GM._user_mask[li, xi] :
                        self.mask_list.append((li, xi)) 

    def set_current_point_label(self):
        lambda_index = self.GM._analysis_point.get_index('lambda_index')
        x_index = self.GM._analysis_point.get_index('x_index')
        y_index = self.GM._analysis_point.get_index('y_index')
        self.label_current_point_coords.setText('({}, {}, {})'.format(lambda_index, x_index, y_index))

    def set_range_labels(self):
        self.set_range_label(self.label_lambda_range)
        self.set_range_label(self.label_x_range)
        self.set_range_label(self.label_y_range)

    def set_range_label(self, range_label):
        split_text = range_label.text().split(sep=' range:')
        if not split_text[1].startswith('<'): # Clear existing range values. Currently not needed
            temp_text = split_text[1].split(sep='<')
            split_text[1] = '<' + '<'.join(temp_text[1:])
        data_shape = self.GM._intensity.shape
        if split_text[0].endswith('x'):
            last_index = data_shape[1] - 1
        elif split_text[0].endswith('y'):
            last_index = data_shape[2] - 1
        else: # λ
            last_index = data_shape[0] - 1
        range_label.setText(split_text[0] + ' range: 0 - {}'.format(last_index) + split_text[1])

    def populate_comboBox_centralColumn(self):
        submodel_types = self.get_submodel_types()
        for param in self.GM.param_names:
            submodel_index = int(param.split(sep='_')[-1])
            if self.GM._model[submodel_index].name is None:
                display_string = f'{param} ({submodel_types[submodel_index]})'
            else:
                display_string = f'{param} [{self.GM._model[submodel_index].name}] ({submodel_types[submodel_index]})'
            self.comboBox_centralColumn_displayChoice.addItem(display_string)

    def get_submodel_types(self):
        submodel_types = []
        for i in range(self.GM._model.n_submodels):
            submodel_info = str(self.GM._model[i])
            submodel_type_info = submodel_info.split(sep='\n')[0]
            submodel_types.append(submodel_type_info.removeprefix('Model: '))
        return submodel_types

    def get_grid(self):
        return deepcopy(self.GM)

    def new_slice_axis(self):
        if self.GM._analysis_point.get_index('lambda_index') is None: # Index choice to check is arbitrary. If one is None, all will be None
            return # Nothing needs to be done yet
        graph = self.find_associated_graph(self.sender())
        graph_name = graph.objectName()
        if graph_name == 'graph_origdata_slice':
            self.generate_origdata_slice()
        elif graph_name == 'graph_selectvar_slice':
            self.generate_selectvar_slice()
        elif graph_name == 'graph_residuals_slice':
            self.generate_residuals_slice()
        self.draw_ap_crosshair(graph)

    def new_line_axis(self):
        if self.GM._analysis_point.get_index('lambda_index') is None: # Index choice to check is arbitrary. If one is None, all will be None
            return # Nothing needs to be done yet
        graph = self.find_associated_graph(self.sender())
        graph_name = graph.objectName()
        if graph_name == 'graph_origdata_line':
            self.generate_origdata_line()
        elif graph_name == 'graph_selectvar_line':
            self.generate_selectvar_line()
        elif graph_name == 'graph_residuals_line':
            self.generate_residuals_line()
        self.draw_ap_crosshair(graph)

    def generate_central_column(self):
        if self.GM._analysis_point.get_index('lambda_index') is None:  # Index choice to check is arbitrary. If one is None, all will be None
            return # Nothing needs to be done yet
        self.generate_selectvar_slice()
        self.generate_selectvar_line()

    def generate_origdata_line(self):
        self.graph_origdata_line.clear()
        x_axis = self.comboBox_origdata_line_varx.currentText()
        if x_axis == 'X':
            y_data = self.GM._get_data_subset(self.GM._intensity, fixed_lambda=True, fixed_y=True)
        elif x_axis == 'Y':
            y_data = self.GM._get_data_subset(self.GM._intensity, fixed_lambda=True, fixed_x=True)
        else: # λ
            y_data = self.GM._get_data_subset(self.GM._intensity, fixed_x=True, fixed_y=True)
        self.graph_origdata_line.setLabel(axis='bottom', text=x_axis)
        self.graph_origdata_line.setLabel(axis='left', text='Intensity')
        self.generate_graph_line(self.graph_origdata_line, list(range(len(y_data))), y_data)

    def generate_selectvar_line(self):
        self.graph_selectvar_line.clear()
        x_axis = self.comboBox_selectvar_line_varx.currentText()
        parts = re.split(r" \(| \[", self.comboBox_centralColumn_displayChoice.currentText())
        selectvar = parts[0]        
        # selectvar = self.comboBox_centralColumn_displayChoice.currentText().split(sep=' (')[0]
        data = self.GM.__getattr__(selectvar).value
        if x_axis == 'X':
            y_data = self.GM._get_data_subset(data, fixed_y=True)
        else: # Y
            y_data = self.GM._get_data_subset(data, fixed_x=True)
        self.graph_selectvar_line.setLabel(axis='bottom', text=x_axis)
        self.graph_selectvar_line.setLabel(axis='left', text=selectvar)
        self.generate_graph_line(self.graph_selectvar_line, list(range(len(y_data))), y_data)

    def generate_residuals_line(self):
        self.graph_residuals_line.clear()
        x_axis = self.comboBox_residuals_line_varx.currentText()
        if x_axis == 'X':
            y_data = self.GM._get_data_subset(self.GM._residual_vals, fixed_lambda=True, fixed_y=True)
        elif x_axis == 'Y':
            y_data = self.GM._get_data_subset(self.GM._residual_vals, fixed_lambda=True, fixed_x=True)
        else: # λ
            y_data = self.GM._get_data_subset(self.GM._residual_vals, fixed_x=True, fixed_y=True)
        self.graph_residuals_line.setLabel(axis='bottom', text=x_axis)
        self.graph_residuals_line.setLabel(axis='left', text='Intensity')
        self.generate_graph_line(self.graph_residuals_line, list(range(len(y_data))), y_data)

    def generate_graph_line(self, graph_object, var_x, var_y, gridx=True, gridy=True, **kwargs):
        graph_object.showGrid(x=gridx, y=gridy)
        graph_object.plot(var_x, var_y, **kwargs)
    
    def generate_origdata_slice(self):
        self.graph_origdata_slice.clear()
        x_axis = self.comboBox_origdata_slice_varx.currentText()
        y_axis = self.comboBox_origdata_slice_vary.currentText()
        if x_axis == y_axis:
            return # Do nothing
        axes_list = [x_axis, y_axis]
        if 'X' not in axes_list:
            data_for_image = self.GM._get_data_subset(self.GM._intensity, fixed_x=True)
        elif 'Y' not in axes_list:
            data_for_image = self.GM._get_data_subset(self.GM._intensity, fixed_y=True)
        else: # lambda (λ)
            data_for_image = self.GM._get_data_subset(self.GM._intensity, fixed_lambda=True)
            if y_axis == 'X':
                data_for_image = np.swapaxes(data_for_image, 0, 1)
        if y_axis == 'λ': # By default, if present, λ is always the x-axis after using get_data_subset()
            data_for_image = np.swapaxes(data_for_image, 0, 1)
        self.graph_origdata_slice.setLabel(axis='bottom', text=x_axis)
        self.graph_origdata_slice.setLabel(axis='left', text=y_axis)
        self.generate_graph_slice(self.graph_origdata_slice, data_for_image)

    def generate_selectvar_slice(self):
        self.graph_selectvar_slice.clear()
        x_axis = self.comboBox_selectvar_slice_varx.currentText()
        y_axis = self.comboBox_selectvar_slice_vary.currentText()
        parts = re.split(r" \(| \[", self.comboBox_centralColumn_displayChoice.currentText())
        selectvar = parts[0]
        # selectvar = self.comboBox_centralColumn_displayChoice.currentText().split(sep=' (')[0]
        if x_axis == y_axis:
            return # Do nothing
        data_for_image = self.GM.__getattr__(selectvar).value
        if y_axis == 'X':
            np.swapaxes(data_for_image, 0, 1)
        self.graph_selectvar_slice.setLabel(axis='bottom', text=x_axis)
        self.graph_selectvar_slice.setLabel(axis='left', text=y_axis)
        self.generate_graph_slice(self.graph_selectvar_slice, data_for_image)

    def generate_residuals_slice(self):
        self.graph_residuals_slice.clear()
        x_axis = self.comboBox_residuals_slice_varx.currentText()
        y_axis = self.comboBox_residuals_slice_vary.currentText()
        if x_axis == y_axis:
            return # Do nothing
        axes_list = [x_axis, y_axis]
        if 'X' not in axes_list:
            data_for_image = self.GM._get_data_subset(self.GM._residual_vals, fixed_x=True)
        elif 'Y' not in axes_list:
            data_for_image = self.GM._get_data_subset(self.GM._residual_vals, fixed_y=True)
        else: # lambda (λ)
            data_for_image = self.GM._get_data_subset(self.GM._residual_vals, fixed_lambda=True)
            if y_axis == 'X':
                data_for_image = np.swapaxes(data_for_image, 0, 1)
        if y_axis == 'λ': # By default, if present, λ is always the x-axis after using get_data_subset()
            data_for_image = np.swapaxes(data_for_image, 0, 1)
        self.graph_residuals_slice.setLabel(axis='bottom', text=x_axis)
        self.graph_residuals_slice.setLabel(axis='left', text=y_axis)
        self.generate_graph_slice(self.graph_residuals_slice, data_for_image)

    def generate_graph_slice(self, graph_object, data_for_image):
        img = pg.ImageItem(image=data_for_image)
        graph_object.addItem(img)
    
    def generate_graphs_all(self):
        ap_model = self.GM.__getitem__(None) # None gets model at AP
        if ap_model is None:  # Case for a masked (X,Y)
            model_vals = np.full(self.GM._wavelength.shape, np.nan)
        else:
            model_vals = ap_model(self.GM._wavelength)
        self.graph_spectra_fit.clear()
        self.generate_graph_line(self.graph_spectra_fit, self.GM._wavelength, self.GM._get_data_subset(self.GM._intensity, fixed_x=True, fixed_y=True),
                                 symbol='o', pen=None)
        self.graph_spectra_fit.setLabel(axis='bottom', text='λ')
        self.graph_spectra_fit.setLabel(axis='left', text='Intensity')
        self.generate_graph_line(self.graph_spectra_fit, self.GM._wavelength, model_vals)
        
        self.generate_origdata_slice()
        self.generate_selectvar_slice()
        self.generate_residuals_slice()
        
        self.generate_origdata_line()
        self.generate_selectvar_line()
        self.generate_residuals_line()

    def redo_fit_point(self):  # Opens a single spectra dialog box to adjust the fit at one (X,Y) point
        nanvals_mask = self.GM._get_data_subset(self.GM._data_mask, fixed_x=True, fixed_y=True).copy()
        fitter_xvals = (self.GM._wavelength.copy())[~nanvals_mask]
        fitter_yvals = (self.GM._get_data_subset(self.GM._intensity, fixed_x=True, fixed_y=True).copy())[~nanvals_mask]
        if self.GM._uncertainty is None:
            fitter_uncer = None 
        else:
            fitter_uncer = (self.GM._get_data_subset(self.GM._uncertainty, fixed_x=True, fixed_y=True).copy())[~nanvals_mask]

        grid_key = (self.GM._analysis_point.get_index('x_index'), self.GM._analysis_point.get_index('y_index'))
        key_3d = (slice(None),) + grid_key
        self.GM._dof[grid_key] = np.sum(~nanvals_mask) - self.GM._free_param_count # Degrees of freedom        # Could probably remove this. It should already be set
        
        fitter = FunctionFitter(fitter_xvals, fitter_yvals, uncertainty=fitter_uncer, function=self.GM.__getitem__(None))
        redo_fit_dialog = FitDialog(fitter, limited_adjustment=True)
        if redo_fit_dialog.exec():
            this_fit_info = redo_fit_dialog.get_fit_info()
            this_chi_sq = redo_fit_dialog.get_chi_sq()
            this_model = redo_fit_dialog.get_model()
            these_vals = this_model(self.GM._wavelength)
            self.GM._model_vals[key_3d] = these_vals
            self.GM._residual_vals[key_3d] = self.GM._intensity[key_3d] - these_vals
            self.GM.__setitem__(grid_key, (this_model, this_chi_sq, this_fit_info))
            self.generate_graphs_all()

    def start_redo_fit_grid(self):
        """ Start this long task with spinner in a separate thread. """
        self.spinner.start() # Show the spinner

        self.worker = mySpinWorker(self.redo_fit_grid)
        self.worker.finished.connect(self.task_done)
        self.worker.start()  # Start the worker thread

    def task_done(self):
        """ Stop the spinner when the task is done. """
        self.spinner.stop()
        self.generate_graphs_all()

    def redo_fit_grid(self):
        # parallel = self.checkBox_fitGridParallel.isChecked()
        # parallel = True
        self.GM.fit()
        # self.generate_graphs_all()
    
    def get_var_index_label(self, var_axis_label):
        if var_axis_label == 'X':
            return 'x_index'
        elif var_axis_label == 'Y':
            return 'y_index'
        else: # λ
            return 'lambda_index'

    def click_event(self, event):
        if not event.double():
            return
        if self.GM._analysis_point.get_index('lambda_index') is None: # Index choice to check is arbitrary. If one is None, all will be None
            return # Nothing needs to be done yet
        # TODO: if/else block should be changed to use the new find_associated_axis_label function
        graph = self.sender().parent()
        var_x_axis = self.find_associated_axis_label(graph, axis='x')
        x_axis_index_label = self.get_var_index_label(var_x_axis)
        vb = graph.plotItem.vb
        pos = event.scenePos()
        coords_from_plot = vb.mapSceneToView(pos)
        coords_to_set = {x_axis_index_label: int(coords_from_plot.x())}
        if 'slice' in graph.objectName():
            var_y_axis = self.find_associated_axis_label(graph, axis='y')
            y_axis_index_label = self.get_var_index_label(var_y_axis)
            coords_to_set[y_axis_index_label] = int(coords_from_plot.y())
        self.set_point(lambda_index=coords_to_set.get('lambda_index'), x_index=coords_to_set.get('x_index'), y_index=coords_to_set.get('y_index'), from_text=False)

    def draw_all_ap_crosshairs(self):
        for child in self.layoutWidget.children():
            if 'graph' in child.objectName():
                self.draw_ap_crosshair(child)

    def draw_ap_crosshair(self, graph):
        graph_name = graph.objectName()
        self.vertical_line = pg.InfiniteLine(angle=90)
        x_label = self.get_var_index_label(self.find_associated_axis_label(graph, axis='x'))
        ap_x_val = self.GM._analysis_point.get_index(x_label)
        if 'spectra_fit' in graph_name:
            dx = self.GM._wavelength[1] - self.GM._wavelength[0] # Assumes constant spacing
            ap_x_val = self.GM._wavelength[ap_x_val]
        else:
            ap_x_val += 0.5
        self.vertical_line.setPos(ap_x_val)
        graph.addItem(self.vertical_line)
        if 'slice' in graph_name:
            self.horizontal_line = pg.InfiniteLine(angle=0)
            y_label = self.get_var_index_label(self.find_associated_axis_label(graph, axis='y'))
            ap_y_val = self.GM._analysis_point.get_index(y_label) + 0.5
            self.horizontal_line.setPos(ap_y_val)
            graph.addItem(self.horizontal_line)

    def find_associated_axis_label(self, graph_object, axis=0):
        """
        axis=0 or 'x' -> varx
        axis=1 or 'y' -> vary
        error otherwise
        """
        if axis in [0, 'x', 'X', 'varx']:
            axis = 'varx'
        elif axis in [1, 'y', 'Y', 'vary']:
            axis = 'vary'
        else:
            raise ValueError("axis keyword must be 0, 1, 'x', or 'y'")
        graph_name = graph_object.objectName()
        if 'spectra_fit' in graph_name:
            return 'λ'
        graph_name_core = '_'.join(graph_name.split(sep='_')[1:])
        combobox_name = '_'.join(['comboBox', graph_name_core, axis])
        for child in graph_object.parent().children():
            if child.objectName() == combobox_name:
                return child.currentText()
        raise NameError(f'{combobox_name} not found')
    
    def find_associated_graph(self, combobox_object):
        combobox_name = combobox_object.objectName()
        combobox_name_core = '_'.join(combobox_name.split(sep='_')[1:3])
        graph_name = '_'.join(['graph', combobox_name_core])
        for child in combobox_object.parent().children():
            if child.objectName() == graph_name:
                return child
        raise NameError(f'{graph_name} not found')
    
    def view_masked_points(self):
        masked_points_dialog = MaskedPointsDialog(self)
        if masked_points_dialog.exec():
            pass


class MaskedPointsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/MaskedPoints.ui'), self)
        self.setFixedSize(self.size())

        model = QStandardItemModel()
        self.list_maskedPoints.setModel(model)

        for masked_point in self.parent().mask_list:
            if masked_point not in self.parent().initial_mask:
                model.appendRow(QStandardItem(str(masked_point)))