"""
Function object class that is the sum of one or more Components
and FunctionFitter object class that integrates a Function object
with the data to be fit.
"""

import warnings
import numpy as np
from copy import deepcopy
from collections.abc import Iterable
from astropy.modeling import Model
from astropy.modeling.fitting import TRFLSQFitter, parallel_fit_dask
from astropy.modeling.models import Const1D, Linear1D, Polynomial1D, Gaussian1D, Moffat1D
from ._util import sum_components, isMonotonic
from ._settings import sig_dig, flt_wdth

#TODO : Add sensible __str__() and/or __repr__

class Function:
    """ Sum of one or more Components """
    def __init__(self, model=None):
        """
        model   Description of the model to initialize with.  Can be one 
                of the following:
                - None (creates empty Function)
                - astropy Model type (compound or single)
                - iterable of "Component" or single astropy Model types
        """
        self.components = dict()
        self.selected_comp = -1
        self.model = None

        if model is not None:
            if isinstance(model, Model):
                try:
                    if model.n_submodels == 1:
                        self.components[0] = Component(model=model, description=model.name, ID=0)
                    else:
                        for i, m in enumerate(model):
                            self.components[i] = Component(m, m.name, i)
                    self.model = model.copy()
                except:
                    warnings.warn('Bad model argument [1]. Creating empty Function object.')

            elif (isinstance(model, Iterable) and isinstance(model[0], (Model, Component))):
                i = 0
                try:
                    for c in model:
                        if isinstance(c, Model):
                            self.components[i] = Component(c, c.name, i)
                        else:
                            self.components[i] = deepcopy(c)
                            self.components[i].ID = i
                        i += 1
                    self.model = Component.sum(self.components.values())
                except: warnings.warn('Bad model argument [2]. Creating empty Function object.')
            else:
                warnings.warn('Bad model argument [3]. Creating empty Function object.')
            self.compute_model()

    def compute_components(self):
        """ Adjust Components after model had been changed """
        try:
            if self.model.n_submodels == 1:
                self.components[0] = Component(model=self.model, description=self.model.name, ID=0)
            else:
                for i, m in enumerate(self.model):
                    self.components[i] = Component(m, m.name, i)            
        except:
            self.components = dict()


    def compute_model(self):
        """ (Re)Calculate the astropy Model from self.components """
        try:
            self.model = Component.sum(self.components.values())
        except:
            print("Still Can't Compute Model")
            self.model = None

    def update_model(self, model):
        """ Update the self.model """
        self.model = model
        self.compute_components()

    def update_components(self, comps):
        """ Update self.components """
        self.components = comps
        self.compute_model()

    def add(self, new_comp, return_comp=False):
        """ 
        Add a new component to the Function.
        Takes either an astropy Model or a Component object
        """
        if isinstance(new_comp, str):
            assert new_comp in Component.valid_strs, f'Component must be of type {Component.valid_strs}'
        else:
            assert isinstance(new_comp, (Model, Component)), f"Component must be of type {type(Model)} or {type(Component)}"
        
        ID = 0 if len(self.components) == 0 else 1 + max(self.components)
        if isinstance(new_comp, str):
            comp = Component(model=new_comp, ID=ID)
        elif isinstance(new_comp, Model):
            comp = Component(model=new_comp, description=new_comp.name, ID=ID)
        else:
            comp = deepcopy(new_comp)
            comp.ID = ID
        self.components[ID] = comp
        self.compute_model()
        if return_comp:
            return comp
        else:
            return
    
    def delete(self, ID):
        """Remove a Component and keep Function Component IDs sequential from 0 """
        try:
            self.selected_comp = -1
            _ = self.components.pop(ID)
            old_comps = self.components.copy()
            self.components.clear()
            for i, value in enumerate(old_comps.values()):
                self.components[i] = value
                value.updateID(i)
            self.compute_model()
        except KeyError:
            print(f'Bad ID. No change to Function.')

    def asDict(self):
        """Simple text descrption. Can be used in tree model"""
        items = dict()
        for c in self.components.values():
            items[c.name] = {'desc':c.description, 'params':c.getParamsLists()}
        return items
    

class Component:
    """
    Elements that contribute to the Function
    Takes one of the valid astropy model types, or a string 
    representation of it {'Constant', 'Linear', 'Quadratic', 'Gaussian', 'Moffat'}
    """
    valid_types = {Const1D, Linear1D, Polynomial1D, Gaussian1D, Moffat1D}
    valid_strs = {'Constant', 'Linear', 'Quadratic', 'Gaussian', 'Moffat'}

    def __init__(self, model, description='', ID=-1):
        self.ID = int(ID)
        self.description = description
        self.selected = False
        self.model = None
        self.name = ''
        self.codeName = ''
        self.tied = None  #Will mirror the model.tied dictionary by parameter keys, but use TiedFunction objects

        if isinstance(model, str) and (model in Component.valid_strs):
            self.name = model + '_' + str(ID)
            if model == 'Constant':
                self.model = Const1D()
                self.codeName = 'Const1D()'
            elif model == 'Linear':
                self.model = Linear1D()
                self.codeName = 'Linear1D()'
            elif model == 'Quadratic':
                self.model = Polynomial1D(degree=2)
                self.codeName = 'Polynomial1D(degree=2)'
            elif model == 'Gaussian':
                self.model = Gaussian1D()
                self.codeName = 'Gaussian1D()'
            elif model == 'Moffat':
                self.model = Moffat1D(bounds={'alpha': (1, 10), 'gamma': (1e-30, None)})
                self.codeName = 'Moffat1D()'
        elif type(model) in Component.valid_types:
            if (type(model) == Polynomial1D) and (model.degree != 2):
                warnings.warn('Unsupported Model type')
            else:
                self.model = model.copy()
                self.tied = self.model.tied
                if type(model) == Const1D:
                    self.name = 'Constant_' + str(ID)
                    self.codeName = 'Const1D()'
                elif type(model) == Linear1D:
                    self.name = 'Linear_' + str(ID)
                    self.codeName = 'Linear1D()'
                elif type(model) == Polynomial1D:
                    self.name = 'Quadratic_' + str(ID)
                    self.codeName = 'Polynomial1D(degree=2)'
                elif type(model) == Gaussian1D:
                    self.name = 'Gaussian_' + str(ID)
                    self.codeName = 'Gaussian1D()'
                else:
                    self.name = 'Moffat_' + str(ID)
                    self.codeName = 'Moffat1D()'
        if self.model is None: warnings.warn('Unsupported Model type')
        else: self.model.name = self.description

    def updateID(self, newID):
        name_base = self.name.split('_')[0]
        self.name = name_base + '_' + str(newID)
        self.ID = newID
        return
    
    def getParamsLists(self):
        '''Suitable for use in a widget tree
           Tied parameters must be created and stored via the TiedFunction class
        '''
        params = []
        for p in self.model.param_names:
            val_str = f'{self.model.__getattribute__(p).value:.{sig_dig}f}'
            if self.model.fixed[p]:
                constraint_str = 'Fixed'
            elif self.model.tied[p]:
                constraint_str = str(self.tied[p])
            else:
                if self.model.bounds[p][0] is None:
                    # lb = '-∞' #This is cute but doesn't show up in monospace
                    lb = '-inf'
                else:
                    lb = f'{self.model.bounds[p][0]:{flt_wdth}.{sig_dig}f}'
                
                if self.model.bounds[p][1] is None:
                    # ub = '+∞'
                    ub = 'inf'
                else:
                    ub = f'{self.model.bounds[p][1]:{flt_wdth}.{sig_dig}f}'
                constraint_str = f'({lb}, {ub})'

            pdata = [p+'_'+str(self.ID), '', val_str, constraint_str]
            params.append(pdata)

        return params
    
    @staticmethod
    def sum(Comps):
        """
        Combine "Component" elements into an astropy CompoundModel
        type, creating a new Jacobian that combines the Jacobians
        of the individual components.

        Comps: iterable of Component type
        """
        components = [x.model for x in Comps]
        return sum_components(*components).copy()
    


class FunctionFitter:
    """ Object combining Function with data to fit """
    def __init__(self, x, y, uncertainty=None, function=None):
        """
        function :  default is None --> starts with empty Function
                    Also accepts:
                    - Function object
                    - Any x such that Function(model=x) is valid
        """
        assert x.shape == y.shape, "Independent and dependent variables must have same shape"
        assert np.all(np.isfinite(x)), "All X values must be finite"
        assert np.all(np.isfinite(y)), "All Y values must be finite"
        assert isMonotonic(x), "X must be monotonic"
        self.x_isDecreasing =  x[-1] < x[0]
        self.x = x.copy()
        self.y = y.copy()
        self.uncertainty = uncertainty if uncertainty is None else uncertainty.copy()
        self.fitter = TRFLSQFitter(calc_uncertainties=True) # This could be changed but probably shouldn't be (Ed)
        self.last_fit_info = None
        self.last_chi_sq = None

        if isinstance(function, Function):
            self.function = deepcopy(function)
        else:
            try:
                self.function = Function(function)
            except:
                self.function = Function()

        if uncertainty is None:
            self._fitter_weights = np.ones(x.shape)
        elif uncertainty.shape != x.shape:
            warnings.warn('Uncertainty shape does not match.  Fitter weights set to 1')
            self._fitter_weights = np.ones(x.shape)
        elif any(uncert_value == 0 for uncert_value in uncertainty):
            warnings.warn('Uncertainty values of 0 are present.  Fitter weights set to 1 for those cases')
            self._fitter_weights = np.array([1 if uncert_value == 0 else 1 / uncert_value for uncert_value in uncertainty])
        else:
            self._fitter_weights = 1 / uncertainty
        
    def add_component(self, comp, return_comp=False):
        """ Wrapper to self.function.add() """
        retval = self.function.add(comp, return_comp=return_comp)
        if return_comp:
            return retval
        else:
            return

    def delete_component(self, ID):
        """ Wrapper to self.function.delete() """
        return self.function.delete(ID)
    
    def update_model(self, model):
        return self.function.update_model(model)

    def fit(self):
        """ Run the fitter """
        try :
            fit = self.fitter(self.function.model, self.x, self.y, weights=self._fitter_weights, filter_non_finite=True)
        except Exception as e :
            warnings.warn(f'No Fitting: {e}')
        else:
            self.last_fit_info = self.fitter.fit_info
            self.last_chi_sq = np.sum(((fit(self.x) - self.y) * self._fitter_weights)**2)
            self.function.update_model(fit)

    def compute_model(self):
        """ (Re)Calculate the astropy Model from the now defined components """
        return self.function.compute_model()

    def get_model(self):
        """ Return current model """
        return deepcopy(self.function.model)

    def get_fit_info(self):
        """ Return most recent fit_info """
        return deepcopy(self.last_fit_info)
    
    def get_chi_sq(self):
        """ Return most recent chi_sq """
        return deepcopy(self.last_chi_sq)