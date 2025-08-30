from .newt_raph import solve_eqs
import re

def coolprop_formater(eqs, map_dict):
    """
    This function formats input equations that contains thermodynamic equations,
    to CoolProps standard format.
    """

    formated_eqs = []

    for eq in eqs:
        for pattern, formated_pattern in map_dict.items():
            if pattern in eq:
                eq = eq.replace(pattern, formated_pattern)
        formated_eqs.append(eq)

    return formated_eqs

def insert_solved_vars(eqs, solved_vars):
    """
    IF the value of a variable is optimized,
    this function replaces identifiers of variables with it's values.
    """
    masked_eqs = []

    for eq in eqs:
        for var_id, var_val in solved_vars.items():
            mask = r"""(?<![\w_'"]){}(?![\w_'"])""".format(var_id)
            eq = re.sub(mask, str(var_val), eq)
        masked_eqs.append(eq)

    return masked_eqs

def solve_system(system_eqs, system_vars, coolprop_map_dict, **kwargs):
    """
    This function solves a system of equations,
    which is part of all systems of equations.
    The system may contain several sub-systems that should be solved by order.
    """
    system_results = {}
    system_residuals = []

    for sub_eqs, sub_vars in zip(system_eqs, system_vars):
        sub_eqs = coolprop_formater(sub_eqs, coolprop_map_dict)
        sub_inserted_eqs = insert_solved_vars(sub_eqs, system_results)
        unsolved_vars = [var for var in sub_vars if var not in system_results.keys()]
        results, cost_residuals = solve_sub_system(sub_inserted_eqs, unsolved_vars, **kwargs)
        system_results.update(results)
        system_residuals.append(cost_residuals)

    return system_results, system_residuals

def solve_sub_system(eqs, vars_ids, **kwargs):
    """
    This solves a sub-system of equations,
    and returns the results.
    """
    
    values, cost_residuals = solve_eqs(eqs, vars_ids, **kwargs)
    results = {key:value for key, value in zip(vars_ids, values)}

    return results, cost_residuals
