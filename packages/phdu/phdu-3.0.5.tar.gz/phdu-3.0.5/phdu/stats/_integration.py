import numpy as np
from numba import njit

def simpson3oct_vec(f, a, b, pre, *args, relative=True):
    """
    Simpson 3 octaves method.
    Attrs:
        - f:          integrand
        - a:          lower end of integration
        - b:          upper end of integration
        - pre:        precision
        - relative:   precision w.r.t. the order of magnitude of the integration
                      (False: absolute precision)
    """
    num = 3
    In = -1
    In1 = 100.
    if relative:
        condition = lambda In, In1: abs((In-In1) / In1) > pre
    else:
        condition = lambda In, In1: abs(In - In1) > pre
    while condition(In, In1):
        xgrid = np.linspace(a, b, num+1)
        ygrid = f(xgrid, *args)
        if np.isnan(ygrid).all(): #restart
            In = 0. 
            In1 = 100.
        else:            
            In1 = In
            h_3oct = 3*(b-a) / (8*num) # num + 1 edges, num intervals 
            h_6oct = 2 * h_3oct
            h_9oct = 3 * h_3oct
            H = np.hstack((h_3oct, np.repeat(np.array([h_9oct, h_9oct, h_6oct])[None], 1 + num//3, axis=0).ravel()[:(num-1)], h_3oct))
            In = (H * ygrid).sum()
        num += 3
    return In, num-3

@njit
def simpson3oct(f, a, b, pre, *args):
    """
    Simpson 3 octaves method.
    Attrs:
        - f:   integrand
        - a:   lower end of integration
        - b:   upper end of integration
        - pre: precision
    """
    num = 3
    In = 0.
    In1 = 100.
    while abs(In - In1) > pre:
        In1 = In
        h = (b-a) / num
        In = 0.
        n = 1
        for k in np.linspace(a, b, num+1):
            if k == a:
                In = In + (3/8.)*h*f(k, *args)
            if k == b:
                In = In + (3/8.)*h*f(k, *args)
            elif n == 2:
                In = In + (9*h/8.)*f(k, *args)
            elif n == 3:
                In = In + (9*h/8.)*f(k, *args)
            elif n == 4:
                In = In + (6*h/8.)*f(k, *args)
            n += 1
            if n == 5:
                n = 2
        num += 3
    return In, num-3

@njit
def trapecios(f,a,b,pre, *args):
    num = 1
    In = 0.
    In1 = 100.
    while abs(In - In1) > pre:
        In1 = In
        h = (b-a) / num
        In = 0.
        for k in np.linspace(a, b, num+1):
            if k == a:
                In = In + (h/2.)*f(k, *args)
            elif k == b:
                In = In + (h/2)*f(k, *args)
            else:
                In = In + h*f(k, *args)
        num += 1
    return In, num-1