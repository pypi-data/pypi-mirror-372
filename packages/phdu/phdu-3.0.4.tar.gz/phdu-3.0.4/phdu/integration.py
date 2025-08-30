"""
Compute the definite integral of a function using the trapezoid rule or Simpson's 3/8 rule.
"""
import numpy as np
from numba import njit
from numba.core.registry import CPUDispatcher

def trapezoid_rule(func, a, b, n, *args):
    """
    Applies the trapezoid rule with n intervals.

    Parameters:
    func (function): The function to integrate.
    a (float): The lower limit of integration.
    b (float): The upper limit of integration.
    n (int): The number of intervals.
    args: Additional arguments for the function.

    Returns:
    float: The approximated value of the integral.
    """
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = func(x, *args)
    integral = (h / 2) * (y[0] + 2 * np.sum(y[1:n]) + y[n])
    return integral

def simpson_3oct_rule(func, a, b, n, *args):
    """
    Applies Simpson's 3/8 rule with n intervals.

    Parameters:
    func (function): The function to integrate.
    a (float): The lower limit of integration.
    b (float): The upper limit of integration.
    n (int): The number of intervals (must be a multiple of 3).
    args: Additional arguments for the function.

    Returns:
    float: The approximated value of the integral.
    """
    if n % 3 != 0:
        raise ValueError("Number of intervals must be a multiple of 3 for Simpson's 3/8 rule.")

    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = func(x, *args)

    integral = 0
    for i in range(0, n, 3):
        integral += (3 * h / 8) * (y[i] + 3 * y[i + 1] + 3 * y[i + 2] + y[i + 3])

    return integral

def eval_definite_integral(method, func, a, b, target_error, n0, *args):
    n = n0
    # Initial evaluation
    integral_prev = method(func, a, b, n, *args)
    n *= 2
    integral_current = method(func, a, b, n, *args)
    # Loop until the relative error is less than the target error
    while abs((integral_current - integral_prev) / integral_current) > target_error:
        n *= 2
        integral_prev = integral_current
        integral_current = method(func, a, b, n, *args)

    return integral_current, n


trapezoid_rule_nb = njit(trapezoid_rule)
simpson_3oct_rule_nb = njit(simpson_3oct_rule)
eval_definite_integral_nb = njit(eval_definite_integral)

def definite_integral(func, a, b, *args, target_error=1e-4, n0=24, return_n=False, method='simpson_3oct'):
    """
    Returns the definite integral of a function. Uses Numba acceleration if possible.

    Parameters:
    method (str): The method to use. Options are 'trapezoid' and 'simpson_3oct'.
    func (function): The function to integrate.
    a (float): The lower limit of integration.
    b (float): The upper limit of integration.
    target_error (float): The target relative error.
    n0 (int): The initial number of intervals.
    return_n (bool): Whether to return the number of intervals.
    *args: Additional arguments for the function.

    Returns:
    float: The approximated value of the integral.
    int: The number of intervals used.
    """
    assert n0 > 0, "Initial number of intervals must be greater than 0."
    if method == 'simpson_3oct':
        assert n0 % 3 == 0, "Initial number of intervals must be a multiple of 3 for Simpson's 3/8 rule."
    elif method != 'trapezoid':
        raise ValueError("Method must be 'trapezoid' or 'simpson_3oct'.")

    if isinstance(func, CPUDispatcher): # use numba
        nb_str = '_nb'
    else:
        nb_str = ''

    computer = globals()[f'{method}_rule{nb_str}']
    evaluator = globals()[f'eval_definite_integral{nb_str}']

    integral, n = evaluator(computer, func, a, b, target_error, n0, *args)
    if return_n:
        return integral, n
    else:
        return integral
