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

def evalCurveCR9(N, points):
    
    Pp0 = np.array([[points[0] , points[1], points[2]]]).T
    Pp1 = np.array([[points[3] , points[4], points[5]]]).T
    Pp2 = np.array([[points[6] , points[7], points[8]]]).T
    Pp3 = np.array([[points[9] , points[10], points[11]]]).T
    Pp4 = np.array([[points[12] , points[13], points[14]]]).T
    Pp5 = np.array([[points[15] , points[16] , points[17]]]).T
    Pp6 = np.array([[points[18] , points[19] , points[20]]]).T
    Pp7 = np.array([[points[21] , points[22] , points[23]]]).T
    Pp8 = np.array([[points[24] , points[25] , points[26]]]).T
    Pp9 = np.array([[points[27] , points[28] , points[29]]]).T
    Pp10 = np.array([[points[30] , points[31] , points[32]]]).T

    sSCR1 = CatMullRom(Pp0, Pp1, Pp2, Pp3)
    sSCR2 = CatMullRom(Pp1, Pp2, Pp3, Pp4)
    sSCR3 = CatMullRom(Pp2, Pp3, Pp4, Pp5)
    sSCR4 = CatMullRom(Pp3, Pp4, Pp5, Pp6)
    sSCR5 = CatMullRom(Pp4, Pp5, Pp6, Pp7)
    sSCR6 = CatMullRom(Pp5, Pp6, Pp7, Pp8)
    sSCR7 = CatMullRom(Pp6, Pp7, Pp8, Pp9)
    sSCR8 = CatMullRom(Pp7, Pp8, Pp9, Pp10)

    ts = np.linspace(0.0, 1.0, N//8) # Cada curva tendra N//8 puntos
    x = N//8
    curve = np.ndarray(shape=(len(ts)*8, 3), dtype=float) # van a entrar las 8 curvas de N//8 puntos

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(sSCR1, T).T
        curve[i+x, 0:3] = np.matmul(sSCR2, T).T
        curve[i+(2*x), 0:3] = np.matmul(sSCR3, T).T
        curve[i+(3*x), 0:3] = np.matmul(sSCR4, T).T
        curve[i+(4*x), 0:3] = np.matmul(sSCR5, T).T
        curve[i+(5*x), 0:3] = np.matmul(sSCR6, T).T
        curve[i+(6*x), 0:3] = np.matmul(sSCR7, T).T
        curve[i+(7*x), 0:3] = np.matmul(sSCR8, T).T

    return curve

def evalCurveBezier(N, points):
    P0 = np.array([[points[0], points[1], 0]]).T
    P1 = np.array([[points[2], points[3], 0]]).T
    P2 = np.array([[points[4], points[5], 0]]).T
    P3 = np.array([[points[6], points[7], 0]]).T

    B = bezierMatrix(P0, P1, P2, P3)

    ts = np.linspace(0.0, 1.0, N)
    curve = np.ndarray(shape=(len(ts), 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(B, T).T
    return curve

def evalCurveHermite(N, points):
    P0 = np.array([[points[0], points[1], 0]]).T
    P1 = np.array([[points[2], points[3], 0]]).T
    T0 = np.array([[points[4], points[5], 0]]).T
    T1 = np.array([[points[6], points[7], 0]]).T

    H = hermiteMatrix(P0, P1, T0, T1)

    ts = np.linspace(0.0, 1.0, N)
    curve = np.ndarray(shape=(len(ts), 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(H, T).T
    return curve

def evalCurveHermiteAndBezier(N, pointsH, pointsB):
    P0 = np.array([[pointsH[0], pointsH[1], 0]]).T
    P1 = np.array([[pointsH[2], pointsH[3], 0]]).T
    T0 = np.array([[pointsH[4], pointsH[5], 0]]).T
    T1 = np.array([[pointsH[6], pointsH[7], 0]]).T

    Pb0=np.array([[pointsB[0], pointsB[1], 0]]).T
    Pb1=np.array([[pointsB[2], pointsB[3], 0]]).T
    Pb2=np.array([[pointsB[4], pointsB[5], 0]]).T
    Pb3=np.array([[pointsB[6], pointsB[7], 0]]).T

    H = hermiteMatrix(P0, P1, T0, T1)
    B = bezierMatrix(Pb0, Pb1, Pb2, Pb3)

    ts = np.linspace(0.0, 1.0, N//2)
    curve = np.ndarray(shape=(len(ts)*2, 3), dtype=float)
    offset = N//2

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(H, T).T
        curve[i + offset, 0:3] = np.matmul(B, T).T
    return curve