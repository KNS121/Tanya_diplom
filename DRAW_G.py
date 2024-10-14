import matplotlib.pyplot as plt

def draw(x,y, color_, title, x_label, y_label):
    plt.plot(x,y,color=color_)
    plt.plot(x,y,color=color_)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()