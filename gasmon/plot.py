import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy import optimize
import math

def Gaussian3D(A, x_0, y_0, sig_x, sig_y):
    fit=[]
    x_values = list(range(0,1001, 100))
    y_values = list(range(0,1001, 100))
    for x in x_values:
        for y in y_values:
            x_term = ((float(x) - x_0)**2.0) / (2.0*(sig_x**2.0))
            y_term = ((float(y) - y_0) ** 2.0) / (2.0 * (sig_y ** 2.0))
            z = A * math.exp(-(x_term + y_term))
            fit.append([x,y,z])
    return fit

def plot(plot_data, fit):


    x, y, z = zip(*plot_data)

    fitx, fity, fitz = zip(*fit)

    fig = plt.figure()

    ax = Axes3D(fig)
    surf = ax.plot_trisurf(x, y, z, cmap=cm.jet, linewidth=0.1)
    surf_fit = ax.plot_trisurf(fitx, fity, fitz, cmap=cm.brg, linewidth=0.1)
    fig.colorbar(surf_fit, shrink=0.5, aspect=5)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('Average concentration')
    plt.ylim((0, 1000))
    plt.ylim((0, 1000))

    plt.show(block=False)
    plt.pause(10)
    plt.close()


