"""
Interactive (GUI) dialogs and views
"""
import ast
import pickle
import numpy as np
import pyqtgraph as pg
from pathlib import Path
from copy import deepcopy
from qtpy.QtWidgets import QApplication, QWidget,  QPushButton, QTextBrowser, QHeaderView
from qtpy.uic import loadUi
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant
from qtpy.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QFileDialog, QStyledItemDelegate
from qtpy.QtGui import QFont
from ._function import FunctionFitter, Component
from ._util import TiedFunction, ConvertFloat, first_nonzero_decimal_place, auto_adjust_bounds
from ._settings import sig_dig


class FitDialog(QDialog):
    """ Dialog box to edit function and fit to data """
    def __init__(self, fitter, parent=None, limited_adjustment=False):
        assert isinstance(fitter, FunctionFitter), 'Bad FunctionFitter argument'

        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/Fit.ui'), self)

        self.make_responsive()
        self._current_screen = QApplication.screenAt(self.pos())   # Track current screen for DPI changes

        self.fitter = fitter
        self._fit_clicked = False
        self.limited_adjustment = limited_adjustment

        ## Models
        self.functionTreeModel = FunctionTreeModel(self)
        self.componentGraphItems = []
        self.sumGraph = SumGraph(self)
        self.resGraph = ResGraph(self)
        self.initializeComponentGraphItems()

        ## Tree Model/View
        # right_padded_delegate = PaddedDelegate(right_padding=15)
        self.treeView.setModel(self.functionTreeModel)
        # self.treeView.setItemDelegateForColumn(2, right_padded_delegate)  # Apply to column 2
        header = self.treeView.header()
        for c in range(3):
            header.setSectionResizeMode(c, QHeaderView.ResizeToContents)
  

        # Show grid lines and data points on graph - Sum Graph
        self.graph.showGrid(x=True, y=True)
        self.graph.plot(self.fitter.x, self.fitter.y, symbol='o', pen=None)
        if self.fitter.uncertainty is None:
            temp_uncert = np.zeros_like(self.fitter.x)
            self.error_bars = pg.ErrorBarItem(x=self.fitter.x, y=self.fitter.y, height=temp_uncert)
            self.res_error_bars = pg.ErrorBarItem(x=self.fitter.x, y=np.zeros_like(self.fitter.x), height=temp_uncert)
        else:
            self.error_bars = pg.ErrorBarItem(x=self.fitter.x, y=self.fitter.y, height=self.fitter.uncertainty)
            self.res_error_bars = pg.ErrorBarItem(x=self.fitter.x, y=np.zeros_like(self.fitter.x), height=self.fitter.uncertainty)
        self.graph.addItem(self.sumGraph)
        self.graph.addItem(self.error_bars)
        self.graph.addItem(self.sumGraph)


        # Show grid lines and data points on graph - Residuals Graph
        self.graph_residuals.showGrid(x=True, y=True)
        self.graph_residuals.plot(self.fitter.x, np.zeros(len(self.fitter.y)), symbol=None, pen='r')
        self.graph_residuals.addItem(self.resGraph)
        self.graph_residuals.addItem(self.res_error_bars)
        self.graph_residuals.setXLink(self.graph)
        self.graph_residuals.enableAutoRange()

        # self.checkBoxShowRes.setEnabled(False) # Checkbox currently does nothing. Disable for now

        if self.limited_adjustment:
            self.exportButton.setEnabled(False)
        else:
            self.graph.scene().sigMouseClicked.connect(self.functionGraphDoubleClicked)


        ## Controllers
        # Tree actions
        self.treeView.doubleClicked.connect(self.functionTreeDoubleClicked)
        self.treeView.keyPressEvent = self.functionTreeModel.keyPress
        self.treeView.selectionModel().selectionChanged.connect(self.selectionChange)
        # Connect and initialize buttons
        self.fitButton.clicked.connect(self.fit)
        self.exportButton.clicked.connect(self.export)
        self.updateDisplay()

        return


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

        half_width = int(self.width() * 0.5)
        graph_height = int(self.height() * 0.75)
        residual_height = int(self.height() - graph_height - (1.5 * physical_button_height) - y_margin)
        fit_btn_width = self.fitButton.width()
        exp_btn_width = self.exportButton.width()
        btn_box_width = self.buttonBox.width()
        txt_box_height = int(3*physical_button_height)
        txt_box_width = int(4*physical_button_height)

        # Size elements that need consistent "physical" size across monitors (Buttons, Textboxes)
        for button in self.findChildren(QPushButton):
            button.setFixedHeight(physical_button_height)
        self.buttonBox.setFixedHeight(physical_button_height)

        for txt in self.findChildren(QTextBrowser):
            txt.setFixedSize(txt_box_width, txt_box_height)

        # Set Locations and/or Geometry for left half of main window [Treeview, Text boxes]
        self.treeView.setGeometry(
            0,                           # x (margin left)
            0,                           # y (margin top)
            half_width,                  # width
            self.height()                # height
        )

        self.textAdd.move(half_width - txt_box_width - (2 * x_margin), self.height() - int(2*(txt_box_height + y_margin)) - y_margin)
        self.textDel.move(half_width - txt_box_width - (2 * x_margin), self.height() - (txt_box_height + y_margin) - y_margin)

        # Set Locations and/or Geometry for right half of main window [Graphs, Buttons]
        self.graph.setGeometry(half_width, 0, half_width, graph_height)
        self.graph_residuals.setGeometry(half_width, graph_height + y_margin, half_width, residual_height)
        self.buttonBox.move(self.width() - btn_box_width - x_margin, graph_height + residual_height + (2 * y_margin))
        self.fitButton.move(self.width() - btn_box_width - fit_btn_width - (2*x_margin), graph_height + residual_height + (2 * y_margin))
        self.exportButton.move(self.width() - btn_box_width - fit_btn_width - exp_btn_width - (3*x_margin), graph_height + residual_height + (2 * y_margin))



    def resizeEvent(self, event):
            """Override the built-in resize event handler"""
            # Call parent first to handle the actual resizing
            # super().resizeEvent(event)   # This isn't working properly but it seems that it can be safely left out
            
            # Then adjust our internal widgets
            self.adjust_internal_widgets()

    def moveEvent(self, event):
        """Handle moving between screens with different DPI"""
        current_screen = QApplication.screenAt(self.pos())
        
        if current_screen and current_screen != self._current_screen:
            # print(f"Moved to screen: {current_screen}")
            # print(f"Logical DPI: {current_screen.logicalDotsPerInch()}")
            # print(f"Physical DPI: {current_screen.physicalDotsPerInch()}")
            # print(f"size: {current_screen.size()}")
            # print(f"Device pixel ratio: {current_screen.devicePixelRatio()}")
            # print(f"Name: {current_screen.name()}\n\n")

            # Recalculate sizes for new screen's DPI
            self.make_responsive()
            self.adjust_internal_widgets()
            
            self._current_screen = current_screen
        
        


    def get_model(self):
        return deepcopy(self.fitter.function.model)
    
    def get_fit_info(self):
        return self.fitter.get_fit_info()
    
    def get_chi_sq(self):
        return self.fitter.get_chi_sq()
    
    def addComponent(self, pos):
        ID = self.functionTreeModel.rootItem.childCount()
        newComponentDialog = NewComponentDialog(self)
        if newComponentDialog.exec():
            if newComponentDialog.constraint_type == 'Voigt':
                QMessageBox.critical(self, None, 'Voigt components are not yet supported')
            else:
                self.fitter.add_component(newComponentDialog.component)
                self.addGraphComponent(newComponentDialog.component, pos=pos) #This will adjust the internal component parameter values and bounds
                self.functionTreeModel.addComponent(self.fitter.function.components[ID]) #Reference from the Function to make sure it's using the right pointer
                self.updateDisplay()
        return

    def fit(self):
        self.fitter.fit()
        self.functionTreeModel.reload()
        self.updateGraph()
        self.updateDisplay()

    def export(self):
        """
        Pickle and store the currently fitted astropy model to a file
        or store the function creator in a Python script
        """
        filename, filetype = QFileDialog.getSaveFileName(self, 'Save function', None, 'Python Code (*.py);;Pickle File (*.pkl)')
        if not filename : return # Canceled

        #Write the astropy function creator to a Python script
        if filetype == 'Python Code (*.py)' : 
            with open(filename, 'w') as code :
                print('from astropy.modeling.models import Const1D', file=code)
                print('from astropy.modeling.models import Linear1D', file=code)
                print('from astropy.modeling.models import Polynomial1D', file=code) # For Quadradic
                print('from astropy.modeling.models import Gaussian1D', file=code)
                print('from astropy.modeling.models import Moffat1D', file=code)
                
                print('\nfrom pycfit.util import sum_components, TiedFunction', file=code)
                print('\nmodel = sum_components(' + ', '.join(cmp.codeName for cmp in self.fitter.function.components.values()) + ')', file=code)
                
                for component in self.fitter.function.components.values() :
                    print('\n#', component.name, file=code)                
                    plist = component.getParamsLists()
                    for p in plist:
                        pbase = '_'.join(p[0].split('_')[:-1])
                        print(f'model.{p[0]}.value = {p[2]}', file=code)
                        print(f'model.{p[0]}.fixed = {component.model.fixed[pbase]}', file=code)
                        print(f'model.{p[0]}.bounds = {component.model.bounds[pbase]}', file=code)

                        if component.model.tied[pbase] is False:
                            print(f'model.{p[0]}.tied = False', file=code)    
                        else:                        
                            print(f'model.{p[0]}.tied = TiedFunction("{component.model.tied[pbase]}")', file=code)

        #Pickle and store the currently fitted astropy model to a file
        elif filetype == 'Pickle File (*.pkl)': 
            with open(filename, 'wb') as f:
                pickle.dump(self.fitter.function.model, f)
        
        return
                                        
               
    def updateDisplay(self):
        """Enable/disable buttons"""
        buttonsOn = False if self.fitter.function.model is None else True
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(buttonsOn)
        self.fitButton.setEnabled(buttonsOn)
        if not self.limited_adjustment:
            self.exportButton.setEnabled(buttonsOn)
        return

    def functionGraphDoubleClicked(self, event):
        if event.double():
            # Grab scene position and map it into the view's data coordinate system
            scene_pos = event.scenePos()
            view_box = self.graph.getViewBox()
            data_pos = view_box.mapSceneToView(scene_pos)
            x = data_pos.x()
            y = data_pos.y()
            print(f"Graph double clicked at data coordinates: {x}, {y}")
            self.addComponent(data_pos)


    def functionTreeDoubleClicked(self, index) :
        '''
        Edit a parameter when double-clicked
        '''
        tree_item = index.internalPointer()
        if tree_item.parentItem == self.functionTreeModel.rootItem:
            if AdjustComponentDialog(tree_item, self).exec():
                if self.fitter.function.model.n_submodels == 1:
                    self.fitter.function.model.name = tree_item.itemData[1]
                else:
                    thisID = int(tree_item.itemData[0].split('_')[-1])
                    self.fitter.function.model[thisID].name = tree_item.itemData[1]
            return  # Limited action if it's a Component type objects

        if ParameterDialog(tree_item, self).exec():
            self.fitter.function.compute_components()
            self.functionTreeModel.reload()
            self.updateDisplay()
        return

    def selectionChange(self, selected, deselected) :
        '''
        When the selected component changes...
        '''
        tags = []
        for index in selected.indexes():
            tags.append(int(index.internalPointer().itemData[0].split('_')[1]))
        selectedTags = set(tags)

        if len(selectedTags) > 0:
            self.fitter.function.selected_comp = selectedTags.pop()
        else:
            self.fitter.function.selected_comp = -1

        self.updateGraph()
        return

    def initializeComponentGraphItems(self):
        if self.fitter.function.model is not None:
            for comp in self.fitter.function.components.values():
                self.addGraphComponent(comp, None, set_defaults=False) # To skip adjusting the model parameters
        return

    def addGraphComponent(self, comp, pos, set_defaults=True):
        if 'Constant' in comp.name:
            graph = ConstGraph(comp, pos, self, set_defaults=set_defaults)
        elif 'Linear' in comp.name:
            graph = LinearGraph(comp, pos, self, set_defaults=set_defaults)
        elif 'Quadratic' in comp.name:
            graph = QuadraticGraph(comp, pos, self, set_defaults=set_defaults)
        elif 'Gaussian' in comp.name:
            graph = GaussianGraph(comp, pos, self, set_defaults=set_defaults)
        elif 'Moffat' in comp.name:
            graph = MoffatGraph(comp, pos, self, set_defaults=set_defaults)
        else:
            graph = None

        if graph is not None:
            self.componentGraphItems.append(graph)
            self.graph.addItem(graph)
            self.sumGraph.updateGraph()
            self.resGraph.updateGraph()
        
        return

    def updateGraph(self):
        """ To handle parameter updates after a fit """
        for graphItem in self.componentGraphItems:
            graphItem.updateGraph()
        return

    def reject(self):
        '''If the user cancels the fit'''
        if self._fit_clicked :
            if QMessageBox.question(self, None, 'Are you sure you want to cancel without saving?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes :
                super().reject()
        else :
            super().reject()


class NewComponentDialog(QDialog):
    '''
    Dialog box to create a new component
    '''
    def __init__(self, parent=None) :
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/NewComponent.ui'), self)
        self.setFixedSize(self.size())
        
        self.constraint_type = self.typeComboBox.currentText()
        self.description = ''
        self.component = None
        self.ID = parent.functionTreeModel.rootItem.childCount()
    
    def accept(self) :
        self.constraint_type = self.typeComboBox.currentText()
        self.description = self.descLineEdit.text()
        self.component = Component(self.constraint_type, description=self.description, ID=self.ID)     
        super().accept()


class AdjustComponentDialog(QDialog):
    '''
    Dialog box to adjust Component model description
    '''
    def __init__(self, comp, parent=None):
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/AdjustComponent.ui'), self)
        self.setFixedSize(self.size())
        self.componentItem = comp
        self.modelTypeName.setText('_'.join(comp.itemData[0].split('_')[:-1]))
        self.descLineEdit.setText(comp.itemData[1])

    def accept(self) :
        self.componentItem.itemData[1] = self.descLineEdit.text()
        super().accept()

class ParameterDialog(QDialog):
    '''
    Dialog to edit a parameter
    '''
    def __init__(self, parameter, parent=None) :
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/Parameter.ui'), self)
        self.setFixedSize(self.size())
        self.combomodel = parent.fitter.function.model
        if self.combomodel.n_submodels == 1:
            self.param_name = '_'.join(parameter.itemData[0].split('_')[:-1])
        else:
            self.param_name = parameter.itemData[0]
        self.parameter = parent.fitter.function.model.__getattribute__(self.param_name)

        self.freeRadioButton.clicked.connect(self.freeRadioButtonClicked)
        self.fixedRadioButton.clicked.connect(self.fixedRadioButtonClicked)
        self.tiedRadioButton.clicked.connect(self.tiedRadioButtonClicked)
        self.lowerCheckBox.clicked.connect(self.lowerCheckBoxClicked)
        self.upperCheckBox.clicked.connect(self.upperCheckBoxClicked)
        
        self.display_val = f'{self.parameter.value:.{sig_dig}f}'
        self.valueLineEdit.setText(self.display_val)
        
        self.fixedRadioButton.setChecked(self.parameter.fixed)
        self.freeRadioButton.setChecked(not self.parameter.fixed)
        if self.parameter.tied:
            self.tiedRadioButton.setChecked(True)
            self.exprLineEdit.setText(str(self.parameter.tied))
        else:
            self.tiedRadioButton.setChecked(False)
            self.exprLineEdit.setText('')

        self.lowerCheckBox.setChecked(self.parameter.bounds[0] != None)
        if self.parameter.bounds[0] is None:
            self.lowerLineEdit.setText(self.parameter.bounds[0])
        else:
            self.lowerLineEdit.setText(f'{self.parameter.bounds[0]:.{sig_dig}f}')
        
        self.upperCheckBox.setChecked(self.parameter.bounds[1] != None)
        if self.parameter.bounds[1] is None:
            self.upperLineEdit.setText(self.parameter.bounds[1])
        else:
            self.upperLineEdit.setText(f'{self.parameter.bounds[1]:.{sig_dig}f}')

        self.updateEnabled()
    
    
    def freeRadioButtonClicked(self, checked) :
        self.updateEnabled()
    
    def fixedRadioButtonClicked(self, checked) :
        self.updateEnabled()
    
    def tiedRadioButtonClicked(self, checked) :
        self.updateEnabled()
    
    def lowerCheckBoxClicked(self, checked) :
        self.updateEnabled()
    
    def upperCheckBoxClicked(self, checked) :
        self.updateEnabled()
    
    # Change the widgets that are enabled based on constraint type
    def updateEnabled(self) :
        if self.freeRadioButton.isChecked() :
            self.lowerCheckBox.setEnabled(True)
            
            self.lowerLineEdit.setEnabled(self.lowerCheckBox.isChecked())
            
            self.upperCheckBox.setEnabled(True)
            self.upperLineEdit.setEnabled(self.upperCheckBox.isChecked())
            
            self.exprLabel.setEnabled(False)
            self.exprLineEdit.setEnabled(False)
        elif self.fixedRadioButton.isChecked() :
            self.lowerCheckBox.setEnabled(False)
            self.lowerLineEdit.setEnabled(False)
            
            self.upperCheckBox.setEnabled(False)
            self.upperLineEdit.setEnabled(False)
            
            self.exprLabel.setEnabled(False)
            self.exprLineEdit.setEnabled(False)
        elif self.tiedRadioButton.isChecked() :
            self.lowerCheckBox.setEnabled(False)
            self.lowerLineEdit.setEnabled(False)
            
            self.upperCheckBox.setEnabled(False)
            self.upperLineEdit.setEnabled(False)
            
            self.exprLabel.setEnabled(True)
            self.exprLineEdit.setEnabled(True)
    
    # When the user clicks OK
    def accept(self) :		
        value = ConvertFloat(self.valueLineEdit.text())
        if value is None  :
            QMessageBox.critical(self, None, 'Value is not a valid floating point')
            return
        
        # Update information in the model
        self.combomodel.fixed[self.param_name] = self.fixedRadioButton.isChecked()
        if not self.tiedRadioButton.isChecked():
            self.combomodel.tied[self.param_name] = False

        if self.freeRadioButton.isChecked() :
            if self.lowerCheckBox.isChecked() :
                lower_bound = ConvertFloat(self.lowerLineEdit.text())
                if lower_bound is None :
                    QMessageBox.critical(self, None, 'Lower Bound is not a valid floating point')
                    return
                elif value < lower_bound:
                    reply = QMessageBox.question(self, 'Out of Bounds', 
                                                 ("VALUE is lower than the set LOWER BOUND. "
                                                 "You can adjust the bounds or use the lower bound."
                                                 "\n\nDo you want to set VALUE = LOWER BOUND?"),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        value = lower_bound
                    else:
                        return                    
            else:
                lower_bound = None
            
            if self.upperCheckBox.isChecked() :
                upper_bound = ConvertFloat(self.upperLineEdit.text())
                if upper_bound is None :
                    QMessageBox.information(self, None, 'Upper Bound is not a valid floating point')
                    return
                elif value > upper_bound:
                    reply = QMessageBox.question(self, 'Out of Bounds', 
                                                 ("VALUE is greater than the set UPPER BOUND. "
                                                 "You can adjust the bounds or use the upper bound."
                                                 "\n\nDo you want to set VALUE = UPPER BOUND?"),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        value = upper_bound
                    else:
                        return     
            else:
                upper_bound = None            

            self.combomodel.bounds[self.param_name] = (lower_bound, upper_bound)

        elif self.tiedRadioButton.isChecked() :
            if not self.exprLineEdit.text() :
                QMessageBox.critical(self, 'Need Expression', 'An expression must be entered')
                return
            
            try :
                ast.parse('(' + self.exprLineEdit.text() + ')') # Check that the expression is valid. This does not validate that the variables exist.
            except SyntaxError :
                QMessageBox.critical(self, None, 'Expression must be valid')
                return
            
            self.combomodel.tied[self.param_name] = TiedFunction(self.exprLineEdit.text()) 
        
        # Check if value is the same as the initial rounded value
        if value != self.display_val: # Value has been changed
            self.parameter.value = value
        
        super().accept()


class FunctionTreeModel(QAbstractItemModel):
    def __init__(self, fitDialog, parent=None):
        super().__init__(parent)
        self.rootItem = self.createTree(fitDialog.fitter.function)
        self.function = fitDialog.fitter.function
        self.fitDialog = fitDialog

    def createTree(self, function):
        rootItem = TreeItem(None)
        data = function.asDict()
        for key, values in data.items():
            parentItem = TreeItem([key, values['desc'], "", ""], rootItem)
            for sublist in values['params']:
                childItem = TreeItem(sublist, parentItem)
        return rootItem

    def addComponent(self, comp):
        self.layoutAboutToBeChanged.emit()
        parentItem = TreeItem([comp.name, comp.description, "", ""], self.rootItem)
        params = comp.getParamsLists()
        for plist in params:
            childItem = TreeItem(plist, parent=parentItem)
        self.layoutChanged.emit()
        return

    def removeComponent(self, row):
        self.layoutAboutToBeChanged.emit()
        self.rootItem.removeChild(row)
        self.layoutChanged.emit()
        return

    def reload(self):
        """For updating parameter values and selected components """
        self.layoutAboutToBeChanged.emit()
        if self.function.selected_comp >= 0:
            currIdx = self.index(self.function.selected_comp, 0, QModelIndex())
            self.fitDialog.treeView.setCurrentIndex(currIdx)
        data = self.function.asDict()
        treeComp = self.rootItem.childItems
        for i, (name, info) in enumerate(data.items()):
            treeComp[i].itemData[0] = name
            treeParam = treeComp[i].childItems
            for j, plist in enumerate(info['params']):
                treeParam[j].updateData(plist)
        self.layoutChanged.emit()
        return

    def columnCount(self, parent):
        return 4

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            return ['Name', 'Description', 'Value', 'Constraint'][section]

    def rowCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().childCount()
        return self.rootItem.childCount()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())

        if role == Qt.TextAlignmentRole:
            if index.column() == 2:
                return Qt.AlignRight | Qt.AlignVCenter
            
        if role == Qt.FontRole:
            if index.column() in [2, 3]:  # Numerical columns
                mono_font = QFont("Courier New")
                return mono_font
            
        return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def keyPress(self, event) :
        '''
        Handle deleting a component
        '''
        if event.key() == Qt.Key_Delete and not self.fitDialog.limited_adjustment: # Handle deleting a component
            componentIndex = self.fitDialog.treeView.currentIndex()
            if componentIndex is None : return # Nothing selected
            
            # Work with ID so we can get all parts of a Component
            tree_item = componentIndex.internalPointer()
            ID = int(tree_item.itemData[0].split('_')[-1])

            self.function.delete(ID) # Remove from Function

            # Remove from Tree
            self.removeComponent(ID)
            self.fitDialog.treeView.reset()
            self.reload()             

            # Remove from Graph
            componentGraphItem = self.fitDialog.componentGraphItems[ID]
            self.fitDialog.componentGraphItems.remove(componentGraphItem)
            self.fitDialog.graph.removeItem(componentGraphItem)
            for i, graph in enumerate(self.fitDialog.componentGraphItems):
                graph.ID = i
            self.fitDialog.sumGraph.updateGraph()
            self.fitDialog.resGraph.updateGraph()

            self.fitDialog.updateDisplay()    #Disable buttons if the function is now empty


class TreeItem:
    def __init__(self, data, parent=None):
        self.itemData = data
        self.parentItem = parent
        self.childItems = []

        if parent is not None:
            parent.appendChild(self)

    def updateData(self, data):
        self.itemData = data

    def appendChild(self, item):
        self.childItems.append(item)

    def removeChild(self, row):
        self.childItems.remove(self.child(row))

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def data(self, column):
        return self.itemData[column]

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0



# class PaddedDelegate(QStyledItemDelegate):
#     def __init__(self, right_padding=10, parent=None):
#         super().__init__(parent)
#         self.right_padding = right_padding
        
#     def paint(self, painter, option, index):
#         # Add right padding to the content rectangle
#         option.rect.setRight(option.rect.right() - self.right_padding)
        
#         # Call the base class implementation with modified option
#         super().paint(painter, option, index)
        
#     def sizeHint(self, option, index):
#         size = super().sizeHint(option, index)
#         # Increase width to account for padding
#         size.setWidth(size.width() + self.right_padding)
#         return size


class SumGraph(pg.GraphItem):
    ''' Show the sum of all components '''
    def __init__(self, fitDialog):
        self.function = fitDialog.fitter.function
        self.x = fitDialog.fitter.x
        super().__init__()
    
    def setData(self):
        if self.function.model is not None:
            pos = np.column_stack((self.x, self.function.model(self.x)))
        else:
            pos = np.column_stack((self.x, np.full(self.x.shape, np.nan)))

        self.display_data = {'pos' : pos, # curve points
                            'adj' : np.array([[i, i+1] for i in range(len(self.x)-1)]), # connect them all
                            'pen' : pg.mkPen(color='w', alpha=1.0, width=3.5), # Thick white line
                            'size' : [0 for x in self.x],
                            'symbol' : [None for x in self.x],
                            'pxMode' : True}
    
        self.updateGraph()
    
    def updateGraph(self):
        if self.function.model is not None:
            self.display_data['pos'] = np.column_stack((self.x, self.function.model(self.x)))
            
            super().setData(**self.display_data)


class ResGraph(pg.GraphItem):
    ''' Show the residual of the fit '''
    def __init__(self, fitDialog):
        self.function = fitDialog.fitter.function
        self.x = fitDialog.fitter.x
        self.y = fitDialog.fitter.y
        if self.function.model is not None:
            self.residuals = self.y - self.function.model(self.x)
        else:
            self.residuals = self.y.copy()
        super().__init__()
    
    def setData(self):
        if self.function.model is not None:
            pos = np.column_stack((self.x, self.residuals))
        else:
            pos = np.column_stack((self.x, np.full(self.x.shape, np.nan)))

        self.display_data = {'pos' : pos, # curve points
                            'adj' : np.array([[i, i+1] for i in range(len(self.x)-1)]), # connect them all
                            'pen' : pg.mkPen(color='w', alpha=1.0, width=3.5), # Thick white line
                            'size' : [0 for x in self.x],
                            'symbol' : [None for x in self.x],
                            'pxMode' : True}
    
        self.updateGraph()
    
    def updateGraph(self):
        if self.function.model is not None:
            self.residuals = self.y - self.function.model(self.x)
            self.display_data['pos'] = np.column_stack((self.x, self.residuals))
            
            super().setData(**self.display_data)


class ConstGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a constant component"""
    def __init__(self, constComponent, clickpos, fitDialog, set_defaults=True):
        self.ID = constComponent.ID
        self.fitDialog = fitDialog

        # Set default model values and bounds based on to-be-fit data and click position
        if set_defaults:
            y = fitDialog.fitter.y
            yrange = abs(max(y) - min(y))
            ymid = y[0] + (yrange/2)
            lb = ymid - 4*yrange
            ub = ymid + 4*yrange
            if yrange > 1:
                ndig = None
            else:
                ndig = first_nonzero_decimal_place(ub-lb) + 1  # Do this to have valid bounds with very small y values
            bounds = [round(lb, ndigits=ndig), round(ub, ndigits=ndig)]
            fitDialog.fitter.function.components[self.ID].model.amplitude.value = clickpos.y()
            fitDialog.fitter.function.components[self.ID].model.amplitude.bounds = bounds
            self.fitDialog.fitter.compute_model()        
        
        # Extremis points for the display
        self.xL = fitDialog.fitter.x[0]
        self.xR = fitDialog.fitter.x[-1]
        
        self.dragPoint = None # Used when dragging points with mouse
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data = {'pos' : np.array([[self.xL, component.model(self.xL)], # position of grab points at ends of line segment
                                               [self.xR, component.model(self.xR)]], dtype=float),
                             'adj' : np.array([[0, 1]]), # Conect the two points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # Thin line (white or red depending on selection status)
                             'size' : [15, 15],
                             'symbol' : ['+', '+'],
                             'pxMode' : True,
                             'data' : ['left', 'right']} # Names of the points
        
        self.updateGraph()
    
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data['pos'][0] = [self.xL, component.model(self.xL)]
        self.display_data['pos'][1] = [self.xR, component.model(self.xR)]
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    # Used to move end-points
    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            self.dragPoint = pts[0]
            ind = self.dragPoint.data()
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][1] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        # Update component
        component = self.fitDialog.fitter.function.components[self.ID]
        if   ind == 'left'  : component.model.amplitude.value = (ev.pos() + self.dragOffset).y()
        elif ind == 'right' : component.model.amplitude.value = (ev.pos() + self.dragOffset).y()
        auto_adjust_bounds(component.model.amplitude)
        self.fitDialog.fitter.compute_model()     

        self.fitDialog.updateGraph()  #To update all elements for selection
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class LinearGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a linear component"""
    def __init__(self, linearComponent, clickpos, fitDialog, set_defaults=True) :
        self.ID = linearComponent.ID
        self.fitDialog = fitDialog
     
        if set_defaults:
            x = fitDialog.fitter.x
            y = fitDialog.fitter.y
            slope0 = (y[-1] - y[0]) / (x[-1] - x[0])
            incpt0 = y[0] - (slope0 * x[0])
            sbound = 4 * (abs(max(y) - min(y)) / abs(x[-1] - x[0]))
            if sbound > 1:
                ndig = None
            else:
                ndig = first_nonzero_decimal_place(sbound) + 1
            sbounds = [-1*round(sbound, ndigits=ndig), round(sbound, ndigits=ndig)]

            fitDialog.fitter.function.components[self.ID].model.slope.value = slope0
            fitDialog.fitter.function.components[self.ID].model.slope.bounds = sbounds
            fitDialog.fitter.function.components[self.ID].model.intercept.value = incpt0 + clickpos.y()
            
            self.fitDialog.fitter.compute_model()
        
        # Extremis points for the display
        self.xL = fitDialog.fitter.x[0]
        self.xR = fitDialog.fitter.x[-1]
        self.dragPoint = None # Used when dragging points with mouse
        self.dragOffset = None
        super().__init__()

    def setData(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data = {'pos' : np.array([[self.xL, component.model(self.xL)], # position of grab points at ends of line segment
                                               [self.xR, component.model(self.xR)]], dtype=float),
                             'adj' : np.array([[0, 1]]), # Conect the two points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # Thin line (white or red depending on selection status)
                             'size' : [15, 15],
                             'symbol' : ['+', '+'],
                             'pxMode' : True,
                             'data' : ['left', 'right']} # Names of the points

        self.updateGraph()
    
    def updateGraph(self) :
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data['pos'][0] = [self.xL, component.model(self.xL)]
        self.display_data['pos'][1] = [self.xR, component.model(self.xR)]
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)

        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    # Used to move end-points
    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            self.dragPoint = pts[0]
            ind = self.dragPoint.data()
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][1] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        x0, y0 = self.display_data['pos'][0]
        x1, y1 = self.display_data['pos'][1]
        
        # Update component
        if   ind == 'left'  : y0 = (ev.pos() + self.dragOffset).y()
        elif ind == 'right' : y1 = (ev.pos() + self.dragOffset).y()
        
        component = self.fitDialog.fitter.function.components[self.ID]
        component.model.slope.value, component.model.intercept.value = np.polyfit([x0, x1], [y0, y1], deg=1)
        auto_adjust_bounds(component.model.slope)
        auto_adjust_bounds(component.model.intercept)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()  #To update all elements for selection
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class QuadraticGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a quadratic component"""
    def __init__(self, quadraticComponent, clickpos, fitDialog, set_defaults=True) :
        self.ID = quadraticComponent.ID
        self.x = fitDialog.fitter.x
        self.fitDialog = fitDialog
        
        # extremis and middle points
        self.xL = self.x[0]
        self.xR = self.x[-1]
        self.x_mid = (self.xL + self.xR) / 2
        
        # Set default model values based on to-be-fit data and the click
        if set_defaults:
            self.x_mid = clickpos.x()
            xfit = [self.xL, self.x_mid, self.xR]
            yfit = [fitDialog.fitter.y[0], clickpos.y(), fitDialog.fitter.y[-1]]
            c2, c1, c0 = np.polyfit(xfit, yfit, deg=2)
            component = self.fitDialog.fitter.function.components[self.ID]
            component.model.c2.value = c2
            component.model.c1.value = c1
            component.model.c0.value = c0

            ndig = None if (c2 > 1) else first_nonzero_decimal_place(c2)
            component.model.c2.bounds = [-1 * round(7*abs(c2), ndigits=ndig), round(7*abs(c2), ndigits=ndig)]

            ndig = None if (c1 > 1) else first_nonzero_decimal_place(c1)
            component.model.c1.bounds = [-1 * round(7*abs(c1), ndigits=ndig), round(7*abs(c1), ndigits=ndig)]
            
            ndig = None if (c0 > 1) else first_nonzero_decimal_place(c0)
            component.model.c0.bounds = [-1 * round(7*abs(c0), ndigits=ndig), round(7*abs(c0), ndigits=ndig)]
            
            self.fitDialog.fitter.compute_model()

        self.dragPoint = None # Used when dragging points with mouse
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data = {'pos' : np.array([[self.xL, component.model(self.xL)], # position of grab points
                                               [self.x_mid, component.model(self.x_mid)],
                                               [self.xR, component.model(self.xR)]] +
                                               [[x, component.model(x)] for x in self.x], dtype=float), # Draw the curve
                             'adj' : np.array([[i, i+1] for i in range(3, len(self.x)+2)]), # connect the curve points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # thin white or red line
                             'size' : [15, 15, 15] + [0 for x in self.x], # only show the grab points
                             'symbol' : ['+', '+', '+'] + [None for x in self.x],
                             'pxMode' : True,
                             'data' : ['left', 'mid', 'right'] + [None for x in self.x]}
        
        self.updateGraph()
    
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data['pos'][0] = [self.xL, component.model(self.xL)]
        self.display_data['pos'][1] = [self.x_mid, component.model(self.x_mid)]
        self.display_data['pos'][2] = [self.xR, component.model(self.xR)]
        self.display_data['pos'][3:] = np.column_stack((self.x, component.model(self.x)))
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    def mouseDragEvent(self, ev):
        """ Used to move drag points"""
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            self.dragPoint = pts[0]
            ind = self.dragPoint.data()
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'mid'   : self.dragOffset = self.display_data['pos'][1] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][2] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        x0, y0 = self.display_data['pos'][0]
        x1, y1 = self.display_data['pos'][1]
        x2, y2 = self.display_data['pos'][2]
        
        # Update component
        if   ind == 'left'  : y0 = (ev.pos() + self.dragOffset).y()
        elif ind == 'mid'   : y1 = (ev.pos() + self.dragOffset).y()
        elif ind == 'right' : y2 = (ev.pos() + self.dragOffset).y()
        component = self.fitDialog.fitter.function.components[self.ID]
        component.model.c2.value, component.model.c1.value, component.model.c0.value = np.polyfit([x0, x1, x2], [y0, y1, y2], deg=2)
        auto_adjust_bounds(component.model.c2)
        auto_adjust_bounds(component.model.c1)
        auto_adjust_bounds(component.model.c0)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class GaussianGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a gaussian component"""

    def __init__(self, gaussianComponent, clickpos, fitDialog, set_defaults=True) :
        self.ID = gaussianComponent.ID
        self.x = fitDialog.fitter.x
        self.fitDialog = fitDialog

        # Set default values based on click point and residuals
        #   The residual values values correspond to the closest dataset X (lambda) value where the user clicked and the Y value of the residual at that point
        #   They will also be the initial guess as to the Amplitude and Mean
        if set_defaults:
            # Find closest x datapoint to the click and some min/max std_dev values based on x-step and window size
            std_max = abs(self.x[0] - self.x[-1]) / 2
            if fitDialog.fitter.x_isDecreasing: 
                ix = np.searchsorted(np.flip(self.x), clickpos.x())
                ix = len(self.x) - ix
                std_min = 0.1 * np.diff(np.flip(self.x)).min()
            else:
                ix = np.searchsorted(self.x, clickpos.x())
                std_min = 0.1 * np.diff(self.x).min()

            if abs(self.x[ix] - clickpos.x()) < abs(self.x[ix-1] - clickpos.x()):
                meanIX = ix
            else:
                meanIX = ix - 1

            # Find points where residual is halved and use as default standard deviation
            this_x = self.x[meanIX]
            this_resid = fitDialog.resGraph.residuals[meanIX]
            for ix in range(meanIX+1, len(self.x)):
                if abs(fitDialog.resGraph.residuals[ix]) <= abs(this_resid)/2:
                    break
            diffR = abs(this_x - self.x[ix])

            for ix in range(meanIX-1, -1, -1):
                if abs(fitDialog.resGraph.residuals[ix]) <= abs(this_resid)/2:
                    break
            diffL = abs(this_x - self.x[ix])
            this_stddev = min((diffL, diffR))

            # Find default parameter bounds
            if std_min < (0.1 * this_stddev):
                std_min = 0.1 * this_stddev
            if std_max > (10 * this_stddev):
                std_max = 10 * this_stddev

            if this_resid > 0:
                amp_ub = this_resid * 1e3
                if this_resid > 1:
                    amp_lb = 0.0001
                else:
                    n = first_nonzero_decimal_place(this_resid)
                    amp_lb = 1 * 10**(-1 * (n+3))
            else:
                amp_lb = this_resid * 1e3
                if this_resid < -1:
                    amp_ub = -0.0001
                else:
                    n = first_nonzero_decimal_place(this_resid)
                    amp_ub = -1 * 10**(-1 * (n+3))


            # Set defaults based on this point
            component = fitDialog.fitter.function.components[self.ID]

            component.model.mean.value = this_x
            component.model.mean.bounds = [this_x - this_stddev, this_x + this_stddev]

            component.model.amplitude.value = this_resid
            component.model.amplitude.bounds = [amp_lb, amp_ub]

            component.model.stddev.value = this_stddev
            component.model.stddev.bounds = [std_min, std_max]

            self.fitDialog.fitter.compute_model()          

        # for grab points
        xL = self.x[0]
        xR = self.x[-1]
        self.stddev_min = abs(xR - xL) / (len(self.x)-1) # Don't let the width go to zero
        
        self.dragPoint = None
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        # 'pos' is the position of grab points and the curve
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        
        mean = component.model.mean.value
        stddev = component.model.stddev.value
        self.display_data = {'pos' : np.array([[mean - stddev, component.model(mean - stddev)],
                                               [mean, component.model(mean)],
                                               [mean + stddev, component.model(mean + stddev)]] +
                                               [[x, component.model(x)] for x in self.x], dtype=float),
                             'adj' : np.array([[i, i+1] for i in range(3, len(self.x)+2)]), # connect the curve points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # thin white or red line
                             'size' : [15, 15, 15] + [0 for x in self.x], # only show the grad points
                             'symbol' : ['+', '+', '+'] + [None for x in self.x],
                             'pxMode' : True,
                             'data' : ['left', 'peak', 'right'] + [None for x in self.x]}

        self.updateGraph()
    
    # Used to move drag points
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'

        mean = component.model.mean.value
        stddev = component.model.stddev.value        
        self.display_data['pos'][0] = (mean - stddev, component.model(mean - stddev))
        self.display_data['pos'][1] = (mean, component.model(mean))
        self.display_data['pos'][2] = (mean + stddev, component.model(mean + stddev))
        self.display_data['pos'][3:] = np.column_stack((self.x, component.model(self.x)))                        
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected 
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            ind = None
            for pt in pts :
                self.dragPoint = pt
                ind = pt.data()
                if ind is not None : break
            else :
                ev.ignore()
                return
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'peak'  : self.dragOffset = self.display_data['pos'][1] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][2] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        # Update component
        component = self.fitDialog.fitter.function.components[self.ID]
        if   ind == 'left' :
            component.model.stddev.value = max(self.stddev_min, component.model.mean.value - (ev.pos() + self.dragOffset).x())
            auto_adjust_bounds(component.model.stddev)
        elif ind == 'peak' :
            component.model.mean.value, component.model.amplitude.value = ev.pos() + self.dragOffset
            auto_adjust_bounds(component.model.mean)
            auto_adjust_bounds(component.model.amplitude)
        elif ind == 'right' :
            component.model.stddev.value = max(self.stddev_min, (ev.pos() + self.dragOffset).x() - component.model.mean.value)
            auto_adjust_bounds(component.model.stddev)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class MoffatGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a Moffat component"""

    def __init__(self, moffatComponent, clickpos, fitDialog, set_defaults=True) :
        self.ID = moffatComponent.ID
        self.x = fitDialog.fitter.x
        self.fitDialog = fitDialog
        
        # Set default model values based on to-be-fit data
        # Or set class variables based on loaded model
        component = fitDialog.fitter.function.components[self.ID]
        
        if set_defaults:
            # Find closest x datapoint to the click and some min/max gamma values
            gam_max = abs(self.x[0] - self.x[-1]) / 2
            if fitDialog.fitter.x_isDecreasing: 
                ix = np.searchsorted(np.flip(np.array(self.x)), clickpos.x())
                ix = len(self.x) - ix
                gam_min = 0.1 * np.diff(np.flip(self.x)).min()
            else:
                ix = np.searchsorted(self.x, clickpos.x())
                gam_min = 0.1 * np.diff(self.x).min()

            if abs(self.x[ix] - clickpos.x()) < abs(self.x[ix-1] - clickpos.x()):
                amplitude_index = ix
            else:
                amplitude_index = ix - 1

            # Find points where residual is halved and use for default gamma calculation
            this_x = self.x[amplitude_index]
            this_resid = fitDialog.resGraph.residuals[amplitude_index]
            for ix_pos in range(amplitude_index+1, len(self.x)):
                if abs(fitDialog.resGraph.residuals[ix_pos]) <= abs(this_resid)/2:
                    break
            diff_pos = abs(this_x - self.x[ix_pos])

            for ix_neg in range(amplitude_index-1, -1, -1):
                if abs(fitDialog.resGraph.residuals[ix_neg]) <= abs(this_resid)/2:
                    break
            diff_neg = abs(this_x - self.x[ix_neg])
            this_gamma = min(diff_pos, diff_neg)

            # Find default parameter bounds
            if gam_min < (0.1 * this_gamma):
                gam_min = 0.1 * this_gamma
            if gam_max > (10 * this_gamma):
                gam_max = 10 * this_gamma

            if this_resid > 0:
                amp_ub = this_resid * 1e3
                if this_resid > 1:
                    amp_lb = 0.0001
                else:
                    n = first_nonzero_decimal_place(this_resid)
                    amp_lb = 1 * 10**(-1 * (n+3))
            else:
                amp_lb = this_resid * 1e3
                if this_resid < -1:
                    amp_ub = -0.0001
                else:
                    n = first_nonzero_decimal_place(this_resid)
                    amp_ub = -1 * 10**(-1 * (n+3))

            component.model.amplitude.value = this_resid
            component.model.amplitude.bounds = [amp_lb, amp_ub]

            component.model.x_0.value = this_x
            component.model.x_0.bounds = [this_x - this_gamma, this_x + this_gamma]

            component.model.alpha.value = 1 # When alpha=1, gamma=fwhm/2. Easier to calculate for initialization
            component.model.alpha.bounds = [1, 10]

            component.model.gamma.value = this_gamma
            component.model.gamma.bounds = [gam_min, gam_max]

            self.fwhm_min = 2 * abs(this_x - self.x[amplitude_index - 1])
            self.fitDialog.fitter.compute_model()

        else:
            this_val = component.model.x_0.value
            x_index_R = np.argwhere(self.x > this_val).squeeze()[0]
            Rdiff = abs(this_val - self.x[x_index_R])
            if x_index_R > 0:
                Ldiff = abs(this_val - self.x[x_index_R-1])
                self.fwhm_min = Rdiff + Ldiff
            else:
                self.fwhm_min = 2 * Rdiff


        # for grab points
        self.dragPoint = None
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        # 'pos' is the position of grab points and the curve
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        
        x_0 = component.model.x_0.value
        hwhm = component.model.fwhm / 2 # half width half max
        hwqm = self.calc_full_width_quarter_max() / 2 # half width quarter max
        self.display_data = {'pos' : np.array([[x_0 - hwqm, component.model(x_0 - hwqm)],
                                               [x_0 - hwhm, component.model(x_0 - hwhm)],
                                               [x_0, component.model(x_0)],
                                               [x_0 + hwhm, component.model(x_0 + hwhm)],
                                               [x_0 + hwqm, component.model(x_0 + hwqm)]] +
                                               [[x, component.model(x)] for x in self.x], dtype=float),
                             'adj' : np.array([[i, i+1] for i in range(5, len(self.x)+4)]), # connect the curve points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # thin white or red line
                             'size' : [15, 15, 15, 15, 15] + [0 for x in self.x], # only show the grad points
                             'symbol' : ['+', '+', '+', '+', '+'] + [None for x in self.x],
                             'pxMode' : True,
                             'data' : ['left quarter max', 'left half max', 'peak', 'right half max', 'right quarter max'] + [None for x in self.x]}
        self.updateGraph()
    
    def calc_full_width_quarter_max(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        return 2 * component.model.gamma.value * np.sqrt((2 ** (2 / component.model.alpha.value) - 1))

    def calc_alpha_gamma(self, component, fwqm, fwhm):
        component.model.alpha.value = 1 / np.log2(fwqm ** 2 / fwhm ** 2 - 1)
        component.model.gamma.value = fwhm / (2 * np.sqrt(2 ** (1 / component.model.alpha.value) - 1))

    def check_full_width_bounds(self, fwhm, fwqm, fwhm_fixed=False, fwqm_fixed=False, epsilon=1e-10):
        """
        checks bounds according to sqrt(2) < fwqm / fwhm <= sqrt(3) and fwhm >= fwhm_min
        Exactly one of fwhm_fixed and fwqm_fixed must be set to True. The other parameter will be calculated such that the ratio falls within the valid range
        Note: the lower bound is a '<' NOT '<='. Epsilon is a small number that is used when relevant to ensure the ratio of interest is never equivalent to sqrt(2)
        """
        assert fwhm_fixed + fwqm_fixed == 1, 'Exactly one of fwhm_fixed and fwqm_fixed must be set to True'
        if fwqm / fwhm <= np.sqrt(2):
            if fwhm_fixed:
                fwqm = fwhm * np.sqrt(2) + epsilon
            elif fwqm_fixed:
                fwhm = (fwqm - epsilon) / np.sqrt(2)
        if fwqm / fwhm > np.sqrt(3):
            if fwhm_fixed:
                fwqm = fwhm * np.sqrt(3)
            elif fwqm_fixed:
                fwhm = fwqm / np.sqrt(3)
        if fwhm < self.fwhm_min:
            return self.check_full_width_bounds(self.fwhm_min, fwqm, fwhm_fixed=True)
        return fwhm, fwqm

    # Used to move drag points
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'

        x_0 = component.model.x_0.value
        hwhm = component.model.fwhm / 2 # half width half max
        hwqm = self.calc_full_width_quarter_max() / 2 # half width quarter max
        self.display_data['pos'][0] = (x_0 - hwqm, component.model(x_0 - hwqm))
        self.display_data['pos'][1] = (x_0 - hwhm, component.model(x_0 - hwhm))
        self.display_data['pos'][2] = (x_0, component.model(x_0))
        self.display_data['pos'][3] = (x_0 + hwhm, component.model(x_0 + hwhm))
        self.display_data['pos'][4] = (x_0 + hwqm, component.model(x_0 + hwqm))
        self.display_data['pos'][5:] = np.column_stack((self.x, component.model(self.x)))
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected 
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            ind = None
            for pt in pts :
                self.dragPoint = pt
                ind = pt.data()
                if ind is not None : break
            else :
                ev.ignore()
                return
            
            if   ind == 'left quarter max'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'left half max'     : self.dragOffset = self.display_data['pos'][1] - pos
            elif ind == 'peak'              : self.dragOffset = self.display_data['pos'][2] - pos
            elif ind == 'right half max'    : self.dragOffset = self.display_data['pos'][3] - pos
            elif ind == 'right quarter max' : self.dragOffset = self.display_data['pos'][4] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        # Update component
        component = self.fitDialog.fitter.function.components[self.ID]
        if   ind == 'left quarter max':
            fwhm, fwqm = self.check_full_width_bounds(component.model.fwhm, 2 * (component.model.x_0.value - (ev.pos() + self.dragOffset).x()), fwqm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        elif ind == 'left half max' :
            fwhm, fwqm = self.check_full_width_bounds(2 * (component.model.x_0.value - (ev.pos() + self.dragOffset).x()), self.calc_full_width_quarter_max(), fwhm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        elif ind == 'peak' :
            component.model.x_0.value, component.model.amplitude.value = ev.pos() + self.dragOffset
        elif ind == 'right half max' :
            fwhm, fwqm = self.check_full_width_bounds(2 * ((ev.pos() + self.dragOffset).x() - component.model.x_0.value), self.calc_full_width_quarter_max(), fwhm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        elif ind == 'right quarter max':
            fwhm, fwqm = self.check_full_width_bounds(component.model.fwhm, 2 * ((ev.pos() + self.dragOffset).x() - component.model.x_0.value), fwqm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)

        if ind == 'peak':
            auto_adjust_bounds(component.model.x_0)
            auto_adjust_bounds(component.model.amplitude)
        else:
            auto_adjust_bounds(component.model.alpha)
            auto_adjust_bounds(component.model.gamma)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()