"""
Utility Functions
"""

import math
import warnings
import numpy as np
from functools import reduce
from operator import add
from astropy.modeling.fitting import DEFAULT_EPS


def first_nonzero_decimal_place(x):
    if x == 0:
        return None  # Or raise an exception if you prefer
    s = f"{abs(x):.20f}"  # 20 decimal places should be enough for most practical floats
    decimal_part = s.split('.')[1]
    for i, ch in enumerate(decimal_part):
        if ch != '0':
            return i + 1  # 1-based indexing for "place-values"


def isMonotonic(arr0):
    """
    Is this array monotonic (excludind NaNs)?
    """
    arr = np.array(arr0)
    diffs = np.diff(arr[np.isfinite(arr)])
    return np.all(diffs >= 0) or np.all(diffs <= 0)


def ConvertFloat(s) :
    """
    Convert a string to a finite floating point
    Return None if invalid
    """
    try :
        f = float(s)
    except ValueError :
        return None
    
    if not math.isfinite(f) :
        return None	
    return f


def _none_to_nan(val) :
    """ Convert None to NaN	"""
    return np.nan if val is None else val


def eliminate_axis(shape, axis) :
    """ The shape of a dataset after removing one axis """
    return tuple(dim for i, dim in enumerate(shape) if axis!=i)


def expand_array(arr, shape, axis) :
    """ Turn a 1-D array into a multi-D array by repeating elements """
    if arr.ndim != 1 : raise ValueError('arr must be one dimensional')
    if arr.shape[0] != shape[axis] : raise ValueError('dimension size mismatch')
    
    arr = arr[tuple((slice(None) if axis == _axis else np.newaxis) for _axis, s in enumerate(shape))]
    
    for _axis, s in enumerate(shape) :
        if axis != _axis :
            arr = np.repeat(arr, s, axis=_axis)
    
    return arr



def extract_parameter_uncertainties(fit_info_container, param_names):
    cov_matrices = fit_info_container.get_property_as_array('param_cov')
    nx, ny, np1, np2 = cov_matrices.shape
    assert np1 == np2 and np1 == len(param_names), "Bad arguments"

    cov_mat_list = cov_matrices.reshape(-1, np1, np2)
    uncertainties = {}
    for idx, param_name in enumerate(param_names):
        # Extract standard errors (square root of diagonal elements of covariance matrix)
        std_values = np.array([np.sqrt(max(0, cov[idx, idx])) for cov in cov_mat_list])
        uncertainties[param_name] = std_values.reshape(nx, ny)
    return uncertainties
     

class TiedFunction :
    """ Object used to represent an expression for a Tied astropy parameter """
    def __init__(self, expr) :
        self.expr = expr
    
    def __call__(self, model) :
        return eval(self.expr, {'np':np, 'math':math}, {param_name:getattr(model, param_name) for param_name in model.param_names})
    
    def __str__(self) :
        return self.expr
    
    def __repr__(self) :
        return 'TiedFunction(%r)' % self.expr
    

## -- Sum Components -- ##
class _FakeModel :
    def __init__(self, param_names, params, offset_param_name=None) :
        self.param_names = param_names
        self.values = dict(zip(param_names, params))
        
        if offset_param_name is not None :
            self.values[offset_param_name] += DEFAULT_EPS
    
    def __getattr__(self, name) :		
        return self.values[name]

# Class to represent the Jacobian of a sum of componenets
class _Jacobian :
    def __init__(self, model, *components, transfer_jac=True) :
        self.model = model
        self.components = components
        self.transfer_jac = transfer_jac
        # print("_Jacobian: A", flush=True)

        # Set the slices of the parameters that will be passed that correspond to each component
        self.param_slices = []
        i = 0
        for component in components :
            self.param_slices.append(slice(i, i+len(component.param_names)))
            i += len(component.param_names)
        # print("_Jacobian: B", flush=True)

    # Calculate the Jacobian
    def __call__(self, xdata, *params) :
        # print("_Jacobian: C", flush=True)

        jac = []
        for component, param_slice in zip(self.components, self.param_slices) :
            if component.col_fit_deriv :
                jac.extend(component.fit_deriv(xdata, *params[param_slice]))
            else :
                jac.extend(component.fit_deriv(xdata, *params[param_slice]).T)
        
        # Calculate derivatives of jac components with regard to tied parameters
        if self.transfer_jac and any(callable(tied) for tied in self.model.tied.values()) :
            center = _FakeModel(self.model.param_names, params)
            offsets = [_FakeModel(self.model.param_names, params, offset_param_name) for offset_param_name in self.model.param_names]
            
            for i, (param_name, tied) in enumerate(self.model.tied.items()) :
                if not callable(tied) : continue
                
                center_val = tied(center)
                offset_vals = np.array([tied(offset) for offset in offsets])
                derivs = (offset_vals - center_val) / DEFAULT_EPS
                
                for j, deriv in enumerate(derivs) :
                    if not np.isclose(0.0, deriv) :
                        jac[j] += deriv * jac[i]
        
        return jac


def sum_components(*components, transfer_jac=True) :
    """
    Combine models via addition
    Create a new fit_deriv (Jacobian) that combines the fit_deriv results of the individual componenets
    """
    
    if not components :
        raise TypeError('Must give at least one component')
    
    if len(components) == 1 :
        return components[0]
    
    # Add up the component models
    compound_model = reduce(add, components)
    
    # Create Jacobian if it does not exist
    if compound_model.fit_deriv is None:
        # If each componenet has a Jacobian function
        if all(component.fit_deriv is not None for component in components) :
            # print("sum_components: A", flush=True)
            # try:
            compound_model.fit_deriv = _Jacobian(compound_model, *components, transfer_jac=transfer_jac)
            # print("sum_components: BBBB", flush=True)
            
            # compound_model.col_fit_deriv = True
        else :
            warnings.warn('Building model without Jacobian. This will adversely affect fitting run time.')
    
    # print("sum_components: C", flush=True)
       
    return compound_model


def auto_adjust_bounds(p):
    """
    To use after adjusting a parameter value.
    If fitting is bounded, will check if the new value is within bounds.
    If not, will adjust the bounds so that fit won't fail due to bad 
    initial condition.

    p:  astropy.modeling.parameters.Parameter type
    """
    if (not p.fixed) and (p.bounds != (None, None)):
        too_low = True if (p.bounds[0] is not None) and (p.value <= p.bounds[0]) else False
        too_high = True if (p.bounds[1] is not None) and (p.value >= p.bounds[1]) else False
        if too_low or too_high:
            lower_bound = p.bounds[0]
            upper_bound = p.bounds[1]
            if too_low:
                if upper_bound is None:
                    delta = lower_bound - p.value
                    lower_bound -= (delta * 3)
                else:
                    delta = upper_bound - lower_bound
                    lower_bound -= delta/2

            if too_high:
                if lower_bound is None:
                    delta = p.value - upper_bound
                    upper_bound += (delta * 3)
                else:
                    delta = upper_bound - lower_bound
                    upper_bound += delta/2

            p.bounds = (lower_bound, upper_bound)
    return