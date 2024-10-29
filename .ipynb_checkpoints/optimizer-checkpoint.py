import numpy as np
from scipy.optimize import curve_fit

class PowerLawFitter:
    def __init__(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data
        self.params = None
        self.covariance = None

    def model_func(self, x, a, n):
        return a * x**n

    def fit(self):
        self.params, self.covariance = curve_fit(self.model_func, self.x_data, self.y_data)
        return self.params

    def get_optimal_params(self):
        if self.params is None:
            raise ValueError("Model has not been fitted yet. Call fit() method first.")
        return self.params