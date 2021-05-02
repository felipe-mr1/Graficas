"""Funciones para crear distintas figuras y escenas """

import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.ex_curves as cv
import grafica.scene_graph as sg

def createGPUShape(shape, pipeline):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path, mode = GL_CLAMP_TO_EDGE):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, mode, mode, GL_NEAREST, GL_NEAREST)
    return gpuShape

def createColorTriangle(r, g, b):
    # Funcion para crear un triangulo con un color personalizado

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  r, g, b,
         0.5, -0.5, 0.0,  r, g, b,
         0.0,  0.5, 0.0,  r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return bs.Shape(vertices, indices)

def createColorCircle(N, r, g, b):
    # Funcion para crear un circulo con un color personalizado
    # Poligono de N lados 

    # First vertex at the center, white color
    vertices = [0, 0, 0, r, g, b]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  r, g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return bs.Shape(vertices, indices)

def evalMixCurve(N):
    # Funcion para generar N puntos entre 0 y 1 de una curva personalizada
    # Hermite + Bezier para modelar la superficie de un auto

    # Puntos de Control
    P0 = np.array([[0.07, 0.14, 0]]).T
    P1 = np.array([[0.27, -0.04, 0]]).T
    P2 = np.array([[0.42, 0.06, 0]]).T
    P3 = np.array([[0.5, -0.06, 0]]).T
    P4 = np.array([[-0.5, -0.06, 0]]).T
    T0 = np.array([[-0.13, 0.35, 0]]).T
    alpha = 1
    T1 = 3 * alpha * (P1 - P0)
    # Matrices de Hermite y Beziers
    H_M = cv.hermiteMatrix(P4, P0, T0, T1)
    B_M = cv.bezierMatrix(P0, P1, P2, P3)

    # Arreglo de numeros entre 0 y 1
    ts = np.linspace(0.0, 1.0, N//2)
    offset = N//2 
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(len(ts) * 2, 3), dtype=float)
    
    # Se llenan los puntos de la curva
    for i in range(len(ts)):
        T = cv.generateT(ts[i])
        curve[i, 0:3] = np.matmul(H_M, T).T
        curve[i + offset, 0:3] = np.matmul(B_M, T).T
        
    return curve

def createColorChasis(r, g, b):
    # Crea un shape del chasis de un auto a partir de una curva personalizada
    vertices = []
    indices = []
    curve = evalMixCurve(64) # Se obtienen los puntos de la curva
    delta = 1 / len(curve) # distancia del step /paso
    x_0 = -0.5 # Posicion x inicial de la recta inferior
    y_0 = -0.2 # Posicion y inicial de la recta inferior
    counter = 0 # Contador de vertices, para indicar los indices

    # Se generan los vertices
    for i in range(len(curve)-1):
        c_0 = curve[i] # punto i de la curva
        r_0 = [x_0 + i*delta, y_0] # punto i de la recta
        c_1 = curve[i + 1] # punto i + 1 de la curva
        r_1 = [x_0 + (i+1)*delta, y_0] # punto i + 1 de la recta
        vertices += [c_0[0], c_0[1], 0, r + 0.3, g + 0.3, b + 0.3]
        vertices += [r_0[0], r_0[1], 0, r, g, b]
        vertices += [c_1[0], c_1[1], 0, r + 0.3, g + 0.3, b + 0.3]
        vertices += [r_1[0], r_1[1], 0, r, g, b]
        indices += [counter + 0, counter +1, counter + 2]
        indices += [counter + 2, counter + 3, counter + 1]
        counter += 4

    return bs.Shape(vertices, indices)


def createCar(pipeline):
    # Se crea la escena del auto de la pregunta 1

    # Se crean las shapes en GPU
    gpuChasis = createGPUShape(createColorChasis(0.7, 0, 0), pipeline) # Shape del chasis 
    gpuGrayCircle =  createGPUShape(createColorCircle(20, 0.4, 0.4, 0.4), pipeline) # Shape del circulo gris
    gpuBlackCircle =  createGPUShape(createColorCircle(20, 0, 0, 0), pipeline) # Shape del circulo negro
    gpuBlueQuad = createGPUShape(bs.createColorQuad(0.2, 0.2, 1), pipeline) # Shape de quad azul

    # Nodo del chasis rojo
    redChasisNode = sg.SceneGraphNode("redChasis")
    redChasisNode.childs = [gpuChasis]

    # Nodo del circulo gris
    grayCircleNode = sg.SceneGraphNode("grayCircleNode")
    grayCircleNode.childs = [gpuGrayCircle]
    
    # Nodo del circulo negro
    blackCircleNode = sg.SceneGraphNode("blackCircle")
    blackCircleNode.childs = [gpuBlackCircle]

    # Nodo del quad celeste
    blueQuadNode = sg.SceneGraphNode("blueQuad")
    blueQuadNode.childs = [gpuBlueQuad]

    # Nodo del circulo gris escalado
    scaledGrayCircleNode = sg.SceneGraphNode("slGrayCircle")
    scaledGrayCircleNode.transform = tr.scale(0.6, 0.6, 0.6)
    scaledGrayCircleNode.childs = [grayCircleNode]

    # Nodo de una rueda, escalado
    wheelNode = sg.SceneGraphNode("wheel")
    wheelNode.transform = tr.scale(0.22, 0.22, 0.22)
    wheelNode.childs = [blackCircleNode, scaledGrayCircleNode]

    # Nodo de la ventana, quad celeste escalado
    windowNode = sg.SceneGraphNode("window")
    windowNode.transform = tr.scale(0.22, 0.15, 1)
    windowNode.childs = [blueQuadNode]
     
    # Rueda izquierda posicionada
    leftWheel = sg.SceneGraphNode("lWheel")
    leftWheel.transform = tr.translate(-0.3, -0.2, 0)
    leftWheel.childs = [wheelNode]

    # Rueda derecha posicionada
    rightWheel = sg.SceneGraphNode("rWheel")
    rightWheel.transform = tr.translate(0.26, -0.2, 0)
    rightWheel.childs = [wheelNode]

    # Ventana posicionada
    translateWindow = sg.SceneGraphNode("tlWindow")
    translateWindow.transform = tr.translate(-0.08, 0.06, 0.0)
    translateWindow.childs = [windowNode]

    # Nodo padre auto
    carNode = sg.SceneGraphNode("car")
    carNode.childs = [redChasisNode, translateWindow, leftWheel, rightWheel]

    return carNode

def createSun(pipeline):
    gpuYellowCircle = createGPUShape(createColorCircle(20, 1, 1, 0), pipeline) # Shape del circulo amarillo
    # Nodo del sol, circulo amarillo escalado y posicionado
    sunNode = sg.SceneGraphNode("sun")
    sunNode.transform = tr.matmul([tr.translate(0.7, 0.6, -0.5), tr.scale(0.3, 0.3, 1)])
    sunNode.childs = [gpuYellowCircle]

    return sunNode

def createTextureScene(tex_pipeline):
    gpuTree = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "Tarea1v2/sprites/tree2.png")
    gpuSidewalk = createTextureGPUShape(bs.createTextureQuad(1.0,3.0), tex_pipeline, "Tarea1v2/sprites/sidewalk.jpg", GL_REPEAT)
    gpuTreeRepeat = createTextureGPUShape(bs.createTextureQuad(1, 4), tex_pipeline, "Tarea1v2/sprites/tree2.png", GL_REPEAT)

    # Nodo vereda 1
    sidewalk1Node = sg.SceneGraphNode("sidewalk")
    sidewalk1Node.transform = tr.matmul([tr.translate(0, -0.64, 0),tr.scale(0.1, 0.7, 1)])
    sidewalk1Node.childs = [gpuSidewalk]

    # Nodo vereda 2
    sidewalk2Node = sg.SceneGraphNode("vereda2")
    sidewalk2Node.transform = tr.matmul([tr.translate(0, 0.07, 0),tr.scale(0.1, 0.7, 1)])
    sidewalk2Node.childs = [gpuSidewalk]

    # Nodo vereda 3
    sidewalk3Node = sg.SceneGraphNode("vereda3")
    sidewalk3Node.transform = tr.matmul([tr.translate(0, 0.72, 0),tr.scale(0.1, 0.58, 1)])
    sidewalk3Node.childs = [gpuSidewalk]

    # Nodo vereda izq
    sideWalkLeftNode = sg.SceneGraphNode("veredaIzq")
    sideWalkLeftNode.transform = tr.translate(-0.55, 0.0, 0.0)
    sideWalkLeftNode.childs = [sidewalk1Node, sidewalk2Node, sidewalk3Node]

    # vereda der
    sideWalkRightNode = sg.SceneGraphNode("veredaDer")
    sideWalkRightNode.transform = tr.translate(0.55, 0, 0)
    sideWalkRightNode.childs = [sidewalk1Node, sidewalk2Node, sidewalk3Node]

    # Nodo vereda
    sidewalkNode = sg.SceneGraphNode("vereda")
    sidewalkNode.childs = [sideWalkLeftNode, sideWalkRightNode]

    treeRepeatNode = sg.SceneGraphNode("sidewalk")
    treeRepeatNode.transform = tr.matmul([tr.translate(0, 0, 0),tr.scale(0.3, 0.3, 1)])
    treeRepeatNode.childs = [gpuTreeRepeat]

    # Nodo del primer arbol
    tree1Node = sg.SceneGraphNode("tree1")
    tree1Node.transform = tr.matmul([tr.translate(0.0, -0.8, 0), tr.scale(0.3, 0.3, 1)])
    tree1Node.childs = [gpuTree]
    # Nodo del segundo arbol
    tree2Node = sg.SceneGraphNode("tree2")
    tree2Node.transform = tr.matmul([tr.translate(0.0, -0.3, 0), tr.scale(0.3, 0.3, 1)])
    tree2Node.childs = [gpuTree]
    # Nodo del tercer arbol
    tree3Node = sg.SceneGraphNode("tree3")
    tree3Node.transform = tr.matmul([tr.translate(0.0, 0.3, 0), tr.scale(0.3, 0.3, 1)])
    tree3Node.childs = [gpuTree]
    # Nodo del cuarto arbol
    tree4Node = sg.SceneGraphNode("tree4")
    tree4Node.transform = tr.matmul([tr.translate(0.0, 0.8, 0), tr.scale(0.3, 0.3, 1)])
    tree4Node.childs = [gpuTree]
    # Nodo de los arboles de la izquirda
    leftTreeNode = sg.SceneGraphNode("leftTrees")
    leftTreeNode.transform = tr.translate(-0.75,0.0,1.0)
    leftTreeNode.childs = [tree1Node, tree2Node, tree3Node, tree4Node]
    # Nodo de los arboles de la derecha
    rightTreeNode = sg.SceneGraphNode("rightTrees")
    rightTreeNode.transform = tr.translate(0.75,0.0,1.0)
    rightTreeNode.childs = [tree1Node, tree2Node, tree3Node, tree4Node]
    # Nodo del bosque
    forestNode = sg.SceneGraphNode("trees")
    forestNode.childs = [leftTreeNode, rightTreeNode]
    # Escena
    sceneNode = sg.SceneGraphNode("forest")
    sceneNode.childs = [forestNode, sidewalkNode]

    return sceneNode

def createScene(pipeline):
    # Funcion que crea la escena de la pregunta 2

    # Se crean las shapes en GPU
    gpuGrayQuad = createGPUShape(bs.createColorQuad(0.5, 0.5, 0.5), pipeline) # Shape del quad gris
    gpuBrownTriangle = createGPUShape(createColorTriangle(0.592, 0.329, 0.090), pipeline) # Shape del triangulo cafe
    gpuWhiteQuad = createGPUShape(bs.createColorQuad(1,1,1), pipeline) # Shape del quad blanco
    gpuGreenQuad =  createGPUShape(bs.createColorQuad(68/255, 168/255, 50/255), pipeline) # Shape del quad verde
    #gpuTreeQuad = createTextureGPUShape(bs.createTextureQuad(1, 1), pipeline, "Tarea1v2/sprites/tree.bmp")

    # Nodo del pasto, quad verde escalado
    grassNode = sg.SceneGraphNode("pasto")
    grassNode.transform = tr.scale(2, 2, 1)
    grassNode.childs = [gpuGreenQuad]

    # Nodo de la carretera, quad gris escalado y posicionado
    highwayNode = sg.SceneGraphNode("highway")
    highwayNode.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(1, 4, 1)])
    highwayNode.childs = [gpuGrayQuad]

    # Nodo de lineas de la calle 1
    line1Node = sg.SceneGraphNode("line1")
    line1Node.transform = tr.matmul([tr.translate(0, 0.5, 0),tr.scale(0.1, 0.5, 1)])
    line1Node.childs = [gpuWhiteQuad]

    # Nodo de lineas de la calle 2
    line2Node = sg.SceneGraphNode("line2")
    line2Node.transform = tr.matmul([tr.translate(0, -0.5, 0),tr.scale(0.1, 0.5, 1)])
    line2Node.childs = [gpuWhiteQuad]

    # Nodo vereda izq 1
    vereda1Node = sg.SceneGraphNode("vereda1")
    vereda1Node.transform = tr.matmul([tr.translate(0, -0.64, 0),tr.scale(0.1, 0.7, 1)])
    vereda1Node.childs = [gpuWhiteQuad]

    # Nodo vereda izq 2
    vereda2Node = sg.SceneGraphNode("vereda2")
    vereda2Node.transform = tr.matmul([tr.translate(0, 0.07, 0),tr.scale(0.1, 0.7, 1)])
    vereda2Node.childs = [gpuWhiteQuad]

    # Nodo vereda izq 3
    vereda3Node = sg.SceneGraphNode("vereda3")
    vereda3Node.transform = tr.matmul([tr.translate(0, 0.72, 0),tr.scale(0.1, 0.58, 1)])
    vereda3Node.childs = [gpuWhiteQuad]

    # Nodo vereda izq
    veredaIzqNode = sg.SceneGraphNode("veredaIzq")
    veredaIzqNode.transform = tr.translate(-0.55, 0.0, 0.0)
    veredaIzqNode.childs = [vereda1Node, vereda2Node, vereda3Node]

    # vereda der
    veredaDerNode = sg.SceneGraphNode("veredaDer")
    veredaDerNode.transform = tr.translate(0.55, 0, 0)
    veredaDerNode.childs = [vereda1Node, vereda2Node, vereda3Node]

    # Nodo vereda
    veredaNode = sg.SceneGraphNode("vereda")
    veredaNode.childs = [veredaDerNode, veredaIzqNode]

    # Nodo de la calle completa
    streetNode = sg.SceneGraphNode("street")
    streetNode.childs = [highwayNode, line1Node, line2Node, veredaNode]
    
    # nodo de la linea de pista, quad blanco escalado y posicionado
    lineNode = sg.SceneGraphNode("line")
    lineNode.transform = tr.matmul([tr.translate(0, -0.65, 0), tr.scale(4, 0.02, 1)])
    lineNode.childs = [gpuWhiteQuad]

    # Nodo del background con todos los nodos anteriores
    backGroundNode = sg.SceneGraphNode("background")
    backGroundNode.childs = [grassNode, highwayNode, streetNode] # sunNode pasa abajo

    # Nodo padre de la escena
    sceneNode = sg.SceneGraphNode("world")
    sceneNode.childs = [backGroundNode]

    return sceneNode



