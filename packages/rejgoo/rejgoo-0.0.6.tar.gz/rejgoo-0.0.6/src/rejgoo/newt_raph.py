from .riazi import *
from CoolProp import CoolProp
import numpy as np
import re

def eq_to_cost(eqs):
    """
    This function gets a list of equations and then converts them to a list of cost_functions.

    Parameters:
    eqs (list): A list that contains equations as strings.

    Returns:
    list: A list that contains cost_functions as strings.
    """
    
    cost_fs = []
    for idx, eq in enumerate(eqs):
        equal_loc = eq.find('=')
        cost = eq[:equal_loc] + '-(' + eq[equal_loc+1:] + ')'
        cost_fs.append(cost)

    return cost_fs


def residual(vars_val, cost_fs, vars_masks):
    """
    This function calculates values(residuals) of cost_functions.

    Parameters:
    vars_val (NumPy array):
    cost_fs (List):
    vars_masks (List):
    

    Reterns:
    NumPy array: An array that contains residuals of cost functions.
    """
    res = []
    for cost in cost_fs:
        for var_m, var_val in zip(vars_masks, vars_val):
            cost = re.sub(var_m, '({})'.format(str(var_val)), cost)
        res.append(eval(cost))
    
    return np.array(res)


def deriv(vars_val, cost_fs, vars_masks):
    """
    This function calculates derivatives of cost_fs

    Parameters:
    vars_val (NumPy array):
    cost_fs(List):
    vars_masks (List): A list of RegEx patterns, that select variables in equations strings.
    
    Returns:
    NumPy array: An array that contains derivatives of cost functions.
    """
    res = np.zeros((len(cost_fs), len(vars_val)))

    for var_idx, var_val in enumerate(vars_val):
        vars_val_plus = vars_val.copy()
        vars_val_plus[var_idx] = vars_val_plus[var_idx] + 0.00001
        before = residual(vars_val, cost_fs, vars_masks)
        after = residual(vars_val_plus, cost_fs, vars_masks)
        der = (after - before) / 0.00001
        res[:, var_idx] = der

    return res


def newtraph(vars_val, cost_fs, vars_masks, **kwargs):
    """
    This function finds the root of cost_fs

    Parameters:
    vars_val (NumPy array):
    cost_fs (List):
    vars_masks (List):

    Returns:
    NumPy array : Solved values of variables.
    NumPy array : Residuals of cost functions.
    """

    max_iter = kwargs.get('max_iter', 100)
    learning_rate = kwargs.get('learning_rate', 1)
    
    for _ in range(max_iter):
        der = deriv(vars_val, cost_fs, vars_masks)
        res = residual(vars_val, cost_fs, vars_masks)
        delt = (np.linalg.inv(der) @ res)
        vars_val -= delt * learning_rate

    return vars_val, res

def solve_eqs(eqs, vars_id, **kwargs):
    """
    This function solves the input equation by using other functions in newt_raph module.

    Parameters:
    eqs (List):
    vars_id (List):
    init_vals (Boolean):

    Returns:
    NumPy array : Solved values of variables.
    NumPy array : Residuals of cost functions.
    """

    init_vals = kwargs.get('init_vals', False)
    if init_vals:
        init_vals = {key:float(value) for key, value in init_vals.items()}
    else:
        init_vals = {}

    if 'random_seed' in kwargs.keys():
        np.random.seed(kwargs['random_seed'])
    
    vars_val = [init_vals.get(i, np.random.rand())
            for i in vars_id]
    vars_val = np.array(vars_val)

    vars_masks = [r'(?<!\w)({})(?!\w)'.format(var_id) for var_id in vars_id]
    cost_fs = eq_to_cost(eqs)
    results, residuals = newtraph(vars_val, cost_fs, vars_masks, **kwargs)

    return results, residuals
