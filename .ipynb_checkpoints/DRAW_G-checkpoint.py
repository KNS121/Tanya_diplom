

import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, x=None, y=None, color='blue', title='', x_label='', y_label='', grid=True):
        self.x = x
        self.y = y
        self.color = color
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.grid = grid

    def draw(self):
        if self.x is None or self.y is None:
            raise ValueError("Data (x and y) must be set before drawing the plot.")

        plt.plot(self.x, self.y, color=self.color)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        if self.grid:
            plt.grid(True)
        plt.show()
