"""
Main API Functions
"""
import pickle
from astropy.modeling import Model
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QFont

from copy import deepcopy
from ._function import FunctionFitter
from ._dialog import FitDialog
from ._grid import Grid
from ._dialog_grid import GridDialog



## For Single Spectra ##
def cfit(wavelength, intensity, uncertainty=None, function=None):
    fitter = FunctionFitter(wavelength, intensity, uncertainty, function=function)
    return fitter



def cfit_gui(wavelength, intensity, uncertainty=None, function=None):
    """
    Single spectra fit GUI
    Will return the astropy model that is stored at the time of GUI exit.
    Meaning -- if you have done a "fit", and then adjusted your graphs, the
    adjusted model is returned.

    wavelength:  (1D array)
    intensity:   (1D array)
    uncertainty: (optional 1D array) Measurement uncertainty
    function:  (opional.  astropy model or path to .pkl) 
                Expects an astropy model object, plain or pickled 
                If passed, loads this as the initial model state.
                Otherwise, loads with no model at start
    """
    # create FunctionFitter object
    if function:
        try:
            if isinstance(function, Model):
                astroModel = function
            else:
                with open(function, 'rb') as pkl:
                    astroModel = pickle.load(pkl)
            fitter = FunctionFitter(wavelength, intensity, uncertainty, function=astroModel)
            model_init = astroModel.copy()
        except:
            print(f'Bad function argument: {function}')
            return
    else:
        fitter = FunctionFitter(wavelength, intensity, uncertainty)
        model_init = None

    # Create interactive fit dialog object
    if not QApplication.instance():    
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication.instance() or QApplication(['cfit_gui'])
    set_application_font(app, 10)  # Set 10pt as the base font size. Call this early in before creating/showing any widgets
                                       
    fd = FitDialog(fitter=fitter)
    if fd.exec_():
        return fd.get_model()
    else:
        print('Canceled!')
        return model_init


## For Grid of Spectras ##
def cfit_grid(function, wavelength, intensity, uncertainty=None, mask=None, user_mask=None): 
    GM = Grid(function, wavelength, intensity, uncertainty=uncertainty, mask=mask, user_mask=user_mask)
    return GM


def cfit_grid_gui(model, wavelength=None, intensity=None, uncertainty=None, mask=None, user_mask=None):
    if isinstance(model, Grid):
        GM_orig = deepcopy(model)
        GM = model
        if not GM.is_fitted():
            GM.fit()
    else:
        GM_orig = None
        GM = Grid(model, wavelength, intensity, uncertainty=uncertainty, mask=mask, user_mask=user_mask)
        GM.fit()

    # Create interactive fit dialog object
    if not QApplication.instance():    
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create QApplication only if it doesn't exist
    app = QApplication.instance() or QApplication(['cfit_grid_gui'])
    set_application_font(app, 10)  # Set 10pt as the base font size. Call this early in before creating/showing any widgets
    gd = GridDialog(GM)
    if gd.exec_():
        return gd.GM
    else:
        print('Canceled!')
        return GM_orig
        

def set_application_font(app, size=10):
    """Set a base font size for the entire application"""
    # Alternatively: font = QFont("Your preferred font family", size)
    font = app.font()
    font.setPointSize(size)
    app.setFont(font)
