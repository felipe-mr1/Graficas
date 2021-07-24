from curves import evalCurveCR
import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D

# file to plot and visualize some curves

def plotCurve(ax, curve, label, color=(0,0,1)):
    
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]
    
    ax.plot(xs, ys, zs, label=label, color=color)

if __name__ == "__main__":
    curvepoints9 = [
        0, 0,                 # 0
        0.2, np.pi * 0.25,    # 1
        0.4, np.pi * (0.0),   # 2
        0.5, np.pi * (0.25),  # 3
        0.6, np.pi * (0.10),  # 4
        0.8, np.pi * (0.0),   # 5
        1,0                   # 6
    ]

    curve = evalCurveCR(800, curvepoints9)
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
    plotCurve(ax, curve, "Catmull-Rom curve", (1,0,0))
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()