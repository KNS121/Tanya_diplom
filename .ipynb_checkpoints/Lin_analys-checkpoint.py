import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class LinearInterval():
     
    def __init__(self, x, y, interval_for_check):
        
        self.x = x
        self.y = y
        self.interval_for_check = interval_for_check
        
        self.max_r2_index = None
        self.max_r2 = None
        self.best_slope = None
        self.best_intercept = None
        
        self.r2_scores = []
        
        if len(x) != len(y):
            raise ValueError("Массивы X и Y должны быть одинаковой длины.")

        if len(x) == 0 or len(y) == 0:
            raise ValueError("Массивы X и Y не должны быть пустыми.")

        if interval_for_check <= 1:
            raise ValueError("Размер окна должен быть больше 1.")
            
            
    def get_r2_score_array(self):
        
        for i in range(len(self.x) - self.interval_for_check + 1):
            
            interval_x = self.x[i:i+self.interval_for_check].reshape(-1, 1)
            interval_y = self.y[i:i+self.interval_for_check]
            
            model = LinearRegression()
            model.fit(interval_x, interval_y)
            
            y_pred = model.predict(interval_x)
        
            r2 = r2_score(interval_y, y_pred)
            self.r2_scores.append((i, r2, model.coef_[0], model.intercept_))
    
        self.max_r2_index, self.max_r2, self.best_slope, self.best_intercept = max(self.r2_scores, key=lambda x: x[1])
        
        
    def get_best_segment(self):
        
        if self.max_r2_index is None or self.max_r2 is None:
            raise ValueError("Метод analyze должен быть выполнен перед вызовом get_best_segment.")

        start_index = self.max_r2_index
        end_index = start_index + self.interval_for_check
        return self.x[start_index], self.y[start_index], self.x[end_index - 1], self.y[end_index - 1], self.best_slope,                                                                                                                       self.best_intercept