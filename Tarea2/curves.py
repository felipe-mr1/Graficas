import numpy as np

def CatMullRom(P0, P1, P2, P3):
    G = np.concatenate((P0, P1, P2, P3), axis=1)
    M_CR = np.array([[0, -1/2, 2/2, -1/2],
                     [2/2, 0, -5/2, 3/2],
                     [0, 1/2, 4/2, -3/2],
                     [0, 0, -1/2, 1/2]])
    return np.matmul(G, M_CR)

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def evalCurveCR(N, points):
    
    Pp0 = np.array([[points[0] , points[1], 0]]).T
    Pp1 = np.array([[points[2] , points[3], 0]]).T
    Pp2 = np.array([[points[4] , points[5], 0]]).T
    Pp3 = np.array([[points[6] , points[7], 0]]).T
    Pp4 = np.array([[points[8] , points[9], 0]]).T
    Pp5 = np.array([[points[10] , points[11] , 0]]).T
    Pp6 = np.array([[points[12] , points[13] , 0]]).T

    sSCR1 = CatMullRom(Pp0, Pp1, Pp2, Pp3)
    sSCR2 = CatMullRom(Pp1, Pp2, Pp3, Pp4)
    sSCR3 = CatMullRom(Pp2, Pp3, Pp4, Pp5)
    sSCR4 = CatMullRom(Pp3, Pp4, Pp5, Pp6)

    ts = np.linspace(0.0, 1.0, N//4) # Cada curva tendra N//4 puntos
    x = N//4
    curve = np.ndarray(shape=(len(ts)*4, 3), dtype=float) # van a entrar las 4 curvas de N//4 puntos

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(sSCR1, T).T
        curve[i+x, 0:3] = np.matmul(sSCR2, T).T
        curve[i+(2*x), 0:3] = np.matmul(sSCR3, T).T
        curve[i+(3*x), 0:3] = np.matmul(sSCR4, T).T

    return curve

def hermiteMatrix(P1, P2, T1, T2):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    
    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])    
    
    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    return np.matmul(G, Mb)