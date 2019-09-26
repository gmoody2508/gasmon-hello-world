import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def plot(plot_data):
    x, y, z = zip(*plot_data)
    #ax.scatter(x, y, z)

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    x, y = np.meshgrid(x, y)

    surf = ax.plot_surface(x, y, z, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)

    plt.show(block=False)
    plt.pause(5)
    plt.close()


