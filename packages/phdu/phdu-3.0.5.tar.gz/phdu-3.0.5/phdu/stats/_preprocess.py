"""
To be implemented
"""
import numpy as np
from scipy.stats import gaussian_kde

def density_kernel(data, cov_factor=0.1, n_points=300):    
    density = gaussian_kde(data)
    xs = np.linspace(data.min(), data.max(), n_points)
    density.covariance_factor = lambda : cov_factor
    density._compute_covariance()
    return xs, density(xs)