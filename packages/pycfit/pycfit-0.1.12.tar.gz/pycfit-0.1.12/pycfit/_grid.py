"""
Implementation of Grid class
Extends and modifies Ed's GridModel to contain the raster data to be fit
"""
import warnings
import numpy as np
from copy import deepcopy
from itertools import product
from collections import namedtuple
from astropy.modeling.fitting import TRFLSQFitter, parallel_fit_dask, FitInfoArrayContainer
from scipy import stats
from ._util import _none_to_nan, eliminate_axis, extract_parameter_uncertainties

class Grid:
    """
    Represents raster data to be fit and array of models 
    each of which can have different fit values but all with 
    the same structure	
    """
    _worker_ret_val = namedtuple('_worker_ret_val', ('fit', 'chi_sq', 'fit_info')) 

    def __init__(self, model, wavelength, intensity, uncertainty=None, mask=None, user_mask=None) :
        """
        model:        (astropy.Model) Description of the underlying model to use for fitting
                      Initial parameters at all points will be set to match it.
        wavelength:   (np.array) The independent variable.  Most likely wavelength.  (N,)
        intensity:    (np.array) The dependent variable.  Most likely intensity.  (N,X,Y)
        uncertainty:  (np.array) Uncertainty of the independent variable.  (N,X,Y)
        mask:         (boolean np.array) Indicates data to ignore during fitting. (N,X,Y) [Default is no mask]
                                         Use is driven by bad data or data filters
        user_mask:    (boolean np.array) Location points to ignore / not fit.  (X,Y)  [Default is no mask]
                                         Use is driven by User not wanting to fit the spectra at a given location
        fitter_type   (astropy.modeling.fitting._FitterMeta) Fitter type to be used.  Default is TRFLSQ
        """
        self.shape = Grid._check_dimensions(wavelength, intensity, model)
        self._wavelength = wavelength.copy()
        self._intensity = intensity.copy()
        self._uncertainty = None if uncertainty is None else uncertainty.copy()
        self._data_mask = Grid._load_mask(mask, self._intensity.shape) # To block bad data points within a spectra
        self._user_mask = Grid._load_mask(user_mask, self.shape)  # To block fitting of an entire spectra/ key (a.k.a. one (x,y) location)
        self._fitter_weights = Grid._load_weights(uncertainty, self._intensity.shape)
        self._fitter_type = TRFLSQFitter
        self._has_fit = False
        self._last_fit_parallel = False # Used to track whether last fit was with dask call (slightly different results available)
        self._fitted_model_grid = None # Only populated if parallel fit is performed
        self._analysis_point = AnalysisPoint()

        # To hold post-fit data
        self._model_vals = np.full(self._intensity.shape, np.nan)
        self._residual_vals = np.full(self._intensity.shape, np.nan)
        self._chi_sq = np.full(self.shape, np.nan) #Can only set after a fit
        self._dof    = np.full(self.shape, -1, dtype=np.int32)
        self._p_values = np.full(self.shape, np.nan)
        # self._cov_matrix = np.empty(self.shape, dtype=object)
        self._fit_info = np.empty(self.shape, dtype=object)
        # self._cov_matrix_pll = None  # Store results from parallel run separately to avoid key assignment conflicts
        self._fit_info_pll = None # Store results from parallel run separately to avoid key assignment conflicts


        # model values and std arrays by parameter name
        self._values = dict()
        self._stds = dict()
        self._model = model.copy()
        for param_name in self._model.param_names :
            parameter = getattr(self._model, param_name)
            self._values[param_name] = np.full(self.shape, parameter.value)
            self._stds[param_name] = np.full(self.shape, _none_to_nan(parameter.std))
        self.param_names = list(self._model.param_names)
        self._model.sync_constraints = True # Allow us to make changes to the model and its parameters TODO:verify
        self._free_param_count = sum(1 for param_name in self.param_names if not (self._model.fixed[param_name] or self._model.tied[param_name]))

    # # State used for pickling. Needed for working of the thread Pool (at least as implemented now)
    # TODO -- update this for recent changes
    def __getstate__(self) :
        return {'shape' : self.shape,
                'param_names' : self.param_names,
                '_model'      : self._model,
                '_values'     : self._values,
                '_stds'       : self._stds,
                '_free_param_count' : self._free_param_count,
                '_wavelength' :  self._wavelength,
                '_intensity' :  self._intensity,
                '_data_mask' :  self._data_mask,
                '_user_mask' :  self._user_mask,
                '_fitter_weights' :  self._fitter_weights,
                '_fitter_type' :  self._fitter_type,
                '_has_fit' :  self._has_fit,
                '_last_fit_parallel' : self._last_fit_parallel,
                'analysis_point' :  self._analysis_point,
                'chi_sq' : self._chi_sq,
                'dof' : self._dof,
                # 'cov_matrix' : self._cov_matrix,
                'fit_info' : self._fit_info,
        }

    # For un-pickling (again, needed for the thread Pool())
    def __setstate__(self, state) : self.__dict__.update(state)
    
    # Get a model for the key specified
    def __getitem__(self, key) :
        if key is None:
            key = (self._analysis_point.get_index('x_index'), self._analysis_point.get_index('y_index'))

        if self._user_mask[key]:
            return None
        
        model = self._model.copy()
        model.sync_constraints = True

        for param_name in self.param_names :
            parameter = getattr(model, param_name)
            parameter.value = self._values[param_name][key]
            parameter.std   = self._stds[param_name][key]
        
        return model
    
    # Set the values and stds for the point from the passed model (fit) 
    def __setitem__(self, key, fit_ret_val) :
        fit, chi_sq, fit_info = fit_ret_val

        self._fit_info[key] = fit_info
        self._chi_sq[key] = chi_sq
        self._p_values[key] = stats.chi2.sf(chi_sq, df=self._dof[key])
        for param_name in self.param_names :
            parameter = getattr(fit, param_name)
            
            self._values[param_name][key] = parameter.value
            self._stds[param_name][key] = _none_to_nan(parameter.std)



    
    # Get the _GridParameter object the represents the parameter asked for in name
    def __getattr__(self, name) :
        if name in self.param_names :
            return _GridParameter(getattr(self._model, name), self, name)
        
        raise AttributeError(f"'Grid' object has no attribute '{name}'")


    def _set_mask(self, key):
        self._user_mask[key] = True
        self._chi_sq[key] = np.nan
        self._dof[key] = -1
        # self._cov_matrix[key] = None
        self._fit_info[key] = None

    def _unset_mask(self, key):
        self._user_mask[key] = False

    def _toggle_mask(self, key):
        current = self._user_mask[key]
        self._user_mask[key] = not current


    def is_fitted(self):
        """
        Return state of whether the whole grid has been fitted or not
        """
        return self._has_fit
    

    def clear_fit(self):
        """
        Clear previous fit results
        """
        self._model_vals[:] = np.nan
        self._residual_vals[:] = np.nan
        self._chi_sq[:] = np.nan
        self._dof[:] = -1
        self._p_values[:] = np.nan
        # self._cov_matrix[:] = None
        self._fit_info[:] = None
        # self._cov_matrix_pll = None  # Store results from parallel run separately to avoid key assignment conflicts
        self._fit_info_pll = None # Store results from parallel run separately to avoid key assignment conflicts
        self._has_fit = False
        self._fitted_model_grid = None # Only populated if parallel fit is performed


    def fit(self, key=None, **kwds):
        """
        Adjust Grid fitting in place

        key:    (2 item tuple) If passed, fit only at this point.  
                Default is to fit all the points in the Grid
                
        all other keywords are passed to the fitter        
        """
        fitter = self._fitter_type(calc_uncertainties=True)
        parallel = True

        if key is None:
            print("Fitting across the grid. This may take a few minutes . . . ")
            self.clear_fit() 

            if parallel:
                self._last_fit_parallel = True
                if 'diagnostics_path' not in kwds.keys():
                    diagnostics_path = None
                else:
                    diagnostics_path = kwds['diagnostics_path']
                self._fit_parallel(fitter, diagnostics_path=diagnostics_path)
            else:
                self._last_fit_parallel = False
                self._fitted_model_grid = None
                kwds.pop('diagnostics_path', None) 
                for key in product(*(range(s) for s in self.shape)) : # Loop over all points
                    if not self._user_mask[key]:
                        self._fit_one(key, fitter, **kwds)
                self._residual_vals = self._intensity - self._model_vals
            if not self._has_fit: self._has_fit = True
            self._p_values = stats.chi2.sf(self._chi_sq, df=self._dof)
        else:
            if self._user_mask[key]:
                print(f"{key} is masked out. No fitting performed.")
            else:
                self._last_fit_parallel = False
                self._fitted_model_grid = None
                self._fit_one(key, fitter, **kwds)



    @staticmethod
    def _load_model(model):
        if type(model) == Grid:
            newmodel = model._model.copy()
        else:
            newmodel = model.copy()
        newmodel.sync_constraints = True # Allow us to make changes to the model and its parameters TODO:verify
        return newmodel
        
    @staticmethod
    def _check_dimensions(wavelength, intensity, model):
        assert wavelength.ndim == 1, "wavelength should be 1D"
        assert intensity.ndim == 3, "intensity should be 3D"
        assert wavelength.shape[0] == intensity.shape[0], "wavelength and intensity dimensions don't match"
        grid_shape = eliminate_axis(intensity.shape, axis=0)
        if type(model) == Grid:
            assert model.shape == grid_shape, "model grid dimension does not match" 
        return grid_shape

    @staticmethod
    def _load_mask(mask, shape):
        if mask is None:
            return np.full(shape, False)
        elif mask.shape != shape:
            warnings.warn('Mask shape does not match.  Removing mask.')
            return np.full(shape, False)
        else:
            return mask.astype(bool)

    @staticmethod
    def _load_weights(uncertainty, shape):
        if uncertainty is None:
            return np.ones(shape)
        elif uncertainty.shape != shape:
            warnings.warn('Uncertainty shape does not match.  All fitting weights set to 1')
            return np.ones(shape)
        else:
            return 1 / uncertainty

    # Do the work of fitting
    @staticmethod
    def _fit_worker(fitter, model, x, y, weights, **kwds) :
        fit = fitter(model, x, y, weights=weights, filter_non_finite=True, **kwds)
        chi_sq = np.sum(((fit(x) - y) * weights)**2)
        return Grid._worker_ret_val(fit, chi_sq, deepcopy(fitter.fit_info))

    def _fit_one(self, key, fitter, **kwds):
        # set keyword from_grid_fit to True if this is being called in a loop to fit the entire grid
        in_key = (slice(None),) + key
        include = np.invert(self._data_mask[in_key]) # Points to include (not masked)

        self._dof[key] = np.sum(include) - self._free_param_count # Degrees of freedom
        
        # If there are non-negative DoF and all values are not NaN
        if self._dof[key] >= 0 and not any(np.isnan(self._values[param_name][key]) for param_name in self.param_names) :
            # Execute the fit and set the values and chi squared
            ret_val = Grid._fit_worker(fitter, 
                                       self[key], 
                                       self._wavelength[include], 
                                       self._intensity[in_key][include], 
                                       self._fitter_weights[in_key][include], 
                                       **kwds) 
            
            self[key] = ret_val
            self._model_vals[in_key] = ret_val.fit(self._wavelength)
            self._residual_vals[key] = self._intensity[key] - self._model_vals[key]
        else :
            self._set_mask(key)  # Mask it if insufficient degrees of freedom so we can handle these missing Parameters later

    
    def _fit_parallel(self, fitter, diagnostics_path=None):
        lambda_tuple = (self._wavelength,)
        fit_mask = deepcopy(self._data_mask)
        data = deepcopy(self._intensity)
        weights = deepcopy(self._fitter_weights)
        nandata = np.isnan(data)
        data[nandata] = 0 # These points are masked, setting them to 0 so the function can be fit (still requires non-NaN values even for masked points)
        weights[nandata] = 0
        fit_mask[nandata] = True # Make sure NaN values are masked for fitting
        fit_mask[:, self._user_mask] = True # Also same compution time by not fitting unwanted spectra
        self._dof = np.sum(~fit_mask, axis=0) - self._free_param_count

        if self.is_fitted(): # Make the fit start with existing initial settings for parameters at each grid point if they exist
            model = deepcopy(self._model) 
            model.sync_constraints = True
            for param_name in self.param_names :
                parameter = getattr(model, param_name)
                parameter.value = self._values[param_name]  # These are numpy arrays
                parameter.std   = self._stds[param_name]
        if diagnostics_path is None:
            fit = parallel_fit_dask(model=self._model, fitter=fitter, mask=fit_mask, world=lambda_tuple, data=data, 
                                     weights=weights, fitting_axes=0, fit_info=True)
        else:
            fit = parallel_fit_dask(model=self._model, fitter=fitter, mask=fit_mask, world=lambda_tuple, data=data, 
                                    weights=weights, fitting_axes=0, fit_info=True, diagnostics='all', diagnostics_path=diagnostics_path)

        for param in fit.param_names:
            self.__getattr__(param).value = fit.__getattr__(param).value
        self._fit_info_pll = deepcopy(fitter.fit_info)
        self._fit_info = deepcopy(fitter.fit_info._fit_info_array)
        # self._cov_matrix_pll = fit.cov_matrix
        self._fitted_model_grid = fit
        self._compute_secondary_values()


    def _compute_secondary_values(self):
        """
        After a parallel fit:
        - Compute and store chi-squared, evaluated model values, 
          and residual at each grid point.

        - Populate the Grid._stds dictionary
        """
        d0 = len(self._wavelength)
        d1, d2 = self.shape
        wavelength = self._wavelength.reshape(d0, 1, 1)
        wavelength_3d = np.broadcast_to(wavelength, (d0, d1, d2))
        self._model_vals = self._fitted_model_grid(wavelength_3d)
        self._residual_vals = self._intensity - self._model_vals
        self._chi_sq = np.nansum(((self._residual_vals) * self._fitter_weights) ** 2, axis=0)
        
        self._stds = extract_parameter_uncertainties(self._fit_info_pll, self._fitted_model_grid.param_names)




    def _get_data_subset(self, data, fixed_lambda=False, fixed_x=False, fixed_y=False):
        assert len(data.shape) in (2, 3), 'Data has invalid shape'
        fixed = {'lambda': fixed_lambda, 'x': fixed_x, 'y': fixed_y}
        ap_vars = vars(self._analysis_point)
        index_dict = {}
        for var in fixed.keys():
            if  var == 'lambda' and len(data.shape) == 2: # Data slice - ignore lambda
                continue
            if fixed[var]:
                for ap_var in ap_vars.keys():
                    if var + '_' in ap_var:
                        index = self._analysis_point.get_index(ap_var)
                        assert index is not None, 'Index {} in AnalysisPoint Object cannot be set to None'.format(ap_var)
                        index_dict[var] = index
            else:
                index_dict[var] = slice(None)
        if len(data.shape) == 3:
            return data[index_dict['lambda'], index_dict['x'], index_dict['y']]
        elif len(data.shape) == 2:
            return data[index_dict['x'], index_dict['y']]


    def get_results(self):
        """
        Return a simple structure holding the model description and the 
        parameter arrays for each x,y grid point.
        Masked points will have np.nan parameter values
        """
        keys = ['base_model', 'mask', 'fit_info', 'std_err', 'p_values', 'cov_matrix']
        results_dict = dict.fromkeys(keys, None)
        if self.is_fitted():
            
            results_dict['base_model'] = self._model
            results_dict['mask'] = self._user_mask
            results_dict['p_values'] = self._p_values
            results_dict['std_err'] = self._stds
            results_dict['fit_info'] = FitInfoArrayContainer(self._fit_info)

            for param_name in self.param_names:
                results_dict[param_name] = self.__getattr__(param_name).value # This handles masking out _user_mask-ed points

        return deepcopy(results_dict)



class AnalysisPoint:
    def __init__(self):
        self.lambda_index = None
        self.x_index = None
        self.y_index = None

    def get_point(self):
        return (self.get_index('lambda_index'), self.get_index('x_index'), self.get_index('y_index'))

    def get_index(self, index_name):
        assert index_name in self.__dict__.keys(), '{} is not a valid index name'.format(index_name)
        return self.__dict__[index_name]

    def set_index(self, index_name, index):
        assert index_name in self.__dict__.keys(), '{} is not a valid index name'.format(index_name)
        assert type(index) is int, 'index must be an integer' # TODO: Instead of error, create dialog window with warning, keep index the same.
        self.__dict__[index_name] = index
    
    def set_point(self, point):
        index_list = ['lambda_index', 'x_index', 'y_index']
        for i, index_name in enumerate(index_list):
            self.set_index(index_name, point[i])

class _GridParameter :
    """ Represents one parameter in a Grid """
    def __init__(self, parameter, grid_model, param_name) :
        self._parameter = parameter # Corresponding parameter from model
        self._grid_model = grid_model # Corresponding Grid object
        self._param_name = param_name # Name
    
    # Get/Set the value array from the Grid 
    @property
    def value(self) :
        masked_vals = self._grid_model._values[self._param_name]
        masked_vals[self._grid_model._user_mask] = np.nan
        return masked_vals
    
    @value.setter
    def value(self, value) :
        self._grid_model._values[self._param_name] = value
    
    # Get std from the Grid
    @property
    def std(self) :
        masked_stds = self._grid_model._stds[self._param_name]
        masked_stds[self._grid_model._user_mask] = np.nan
        return masked_stds
    
    # Get/Set properties of the parameter
    # Pass though
    @property
    def fixed(self) : return self._parameter.fixed
    
    @fixed.setter
    def fixed(self, value) : self._parameter.fixed = value
    
    @property
    def tied(self) : return self._parameter.tied
    
    @tied.setter
    def tied(self, value) : self._parameter.tied = value
    
    @property
    def bounds(self) : return self._parameter.bounds
    
    @bounds.setter
    def bounds(self, value) : self._parameter.bounds = value
    
    @property
    def min(self) : return self._parameter.min
    
    @min.setter
    def min(self, value) : self._parameter.min = value
    
    @property
    def max(self) : return self._parameter.max
    
    @max.setter
    def max(self, value) : self._parameter.max = value