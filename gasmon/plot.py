import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def plot(plot_data):
    x, y, z = zip(*plot_data)
    #ax.scatter(x, y, z)

    fig = plt.figure()

    ax = Axes3D(fig)
    surf = ax.plot_trisurf(x, y, z, cmap=cm.jet, linewidth=0.1)
    fig.colorbar(surf, shrink=0.5, aspect=5)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.ylim((0, 1000))
    plt.ylim((0, 1000))

    plt.show(block=False)
    plt.pause(5)
    #plt.close()




