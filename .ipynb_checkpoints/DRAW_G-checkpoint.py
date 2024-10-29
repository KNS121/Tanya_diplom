
import numpy as np
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, x=None, y=None, color='blue', title='', x_label='', y_label='', 
                 grid=True, x_step=0, y_step=0, figsize=(8, 6)):
        self.x = x
        self.y = y
        self.color = color
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.x_step = x_step
        self.y_step = y_step
        self.grid = grid
        self.figsize = figsize
        

    def draw(self):
        if self.x is None or self.y is None:
            raise ValueError("Data (x and y) must be set before drawing the plot.")
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(self.x, self.y, color=self.color, linewidth=4)
        ax.set_title(self.title,fontsize=self.figsize[0])
        ax.set_xlabel(self.x_label, fontsize=self.figsize[0])
        ax.set_ylabel(self.y_label, fontsize=self.figsize[0])
        if self.grid:
            ax.grid(True)
        if self.x_step!=0:
            ax.set_xticks(np.arange(min(self.x), max(self.x) + round(self.x_step), round(self.x_step)))
        ax.set_xticklabels(ax.get_xticks(),fontsize=self.figsize[0], rotation=45)
        if self.y_step!=0:
            ax.set_yticks(np.arange(min(self.y), max(self.y) + self.y_step, self.y_step))
        ax.set_yticklabels(ax.get_yticks(),fontsize=self.figsize[0])
        plt.show()
