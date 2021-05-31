# coding=utf-8
"""Textures and transformations in 3D"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"

############################################################################

def createColorPyramid(r, g ,b):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #    positions         colors
        -0.5, 0.5,  0,  r, g, b,
         0.5, -0.5, 0,  r, g, b,
         0.5, 0.5,  0,  r, g, b,
        -0.5, -0.5, 0,  r, g, b,
         0, 0,  0.5,  r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         0, 1, 3,
         0, 2, 4,
         2, 4, 1,
         3, 4, 1,
         0, 4, 3]

    return bs.Shape(vertices, indices)

def create_tree(pipeline):
    # Piramide verde
    green_pyramid = createColorPyramid(0, 1, 0)
    gpuGreenPyramid = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuGreenPyramid)
    gpuGreenPyramid.fillBuffers(green_pyramid.vertices, green_pyramid.indices, GL_STATIC_DRAW)

    # Cubo cafe
    brown_quad = bs.createColorCube(139/255, 69/255, 19/255)
    gpuBrownQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownQuad)
    gpuBrownQuad.fillBuffers(brown_quad.vertices, brown_quad.indices, GL_STATIC_DRAW)

    # Tronco
    tronco = sg.SceneGraphNode("tronco")
    tronco.transform = tr.scale(0.05, 0.05, 0.2)
    tronco.childs += [gpuBrownQuad]

    # Hojas
    hojas = sg.SceneGraphNode("hojas")
    hojas.transform = tr.matmul([tr.translate(0, 0, 0.1), tr.uniformScale(0.25)])
    hojas.childs += [gpuGreenPyramid]

    # Arbol
    tree = sg.SceneGraphNode("arbol")
    tree.transform = tr.identity()
    tree.childs += [tronco, hojas]

    return tree


def create_house(pipeline):
    # Piramide cafe
    brown_pyramid = createColorPyramid(166/255, 112/255, 49/255)
    gpuBrownPyramid = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownPyramid)
    gpuBrownPyramid.fillBuffers(brown_pyramid.vertices, brown_pyramid.indices, GL_STATIC_DRAW)

    # Cubo rojo
    red_cube = bs.createColorCube(1, 0, 0)
    gpuRedCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuRedCube)
    gpuRedCube.fillBuffers(red_cube.vertices, red_cube.indices, GL_STATIC_DRAW)

    # Cubo cafe
    brown_cube = bs.createColorCube(166/255, 112/255, 49/255)
    gpuBrownCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownCube)
    gpuBrownCube.fillBuffers(brown_cube.vertices, brown_cube.indices, GL_STATIC_DRAW)

    # Techo
    techo = sg.SceneGraphNode("techo")
    techo.transform = tr.matmul([tr.translate(0, 0, 0.1), tr.scale(0.2, 0.4, 0.2)])
    techo.childs += [gpuBrownPyramid]

    # Base
    base = sg.SceneGraphNode("base")
    base.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(0.2, 0.4, 0.2)])
    base.childs += [gpuRedCube]

    # Puerta
    puerta = sg.SceneGraphNode("puerta")
    puerta.transform = tr.matmul([tr.translate(0, -0.2, 0), tr.scale(0.05, 0.001, 0.1)])
    puerta.childs += [gpuBrownCube]

    # Casa
    casa = sg.SceneGraphNode("house")
    casa.transform = tr.identity()
    casa.childs += [techo, base, puerta]

    return casa

def create_skybox(pipeline):
    shapeSky = bs.createTextureCube('paisaje.jfif')
    gpuSky = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSky)
    gpuSky.fillBuffers(shapeSky.vertices, shapeSky.indices, GL_STATIC_DRAW)
    gpuSky.texture = es.textureSimpleSetup(
        getAssetPath("paisaje2.jfif"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    skybox = sg.SceneGraphNode("skybox")
    skybox.transform = tr.matmul([tr.translate(0, 0, 0.3), tr.uniformScale(2)])
    skybox.childs += [gpuSky]

    return skybox

def create_floor(pipeline):
    shapeFloor = bs.createTextureQuad(8, 8)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.texture = es.textureSimpleSetup(
        getAssetPath("grass.jfif"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, 0),tr.scale(2, 2, 1)])
    floor.childs += [gpuFloor]

    return floor

def create_decorations(pipeline):
    tree1 = create_tree(pipeline)
    tree1.transform = tr.translate(0.5, 0, 0)

    tree2 = create_tree(pipeline)
    tree2.transform = tr.translate(-0.5, 0, 0)

    tree3 = create_tree(pipeline)
    tree3.transform = tr.translate(0, -0.5, 0)

    tree4 = create_tree(pipeline)
    tree4.transform = tr.translate(-0.2, 0.5, 0)

    tree5 = create_tree(pipeline)
    tree5.transform = tr.translate(0.2, 0.5, 0)

    house = create_house(pipeline)
    house.transform = tr.translate(0, 0.5, 0)

    decorations = sg.SceneGraphNode("decorations")
    decorations.transform = tr.identity()
    decorations.childs += [tree1, tree2, tree3, tree4, tree5, house]    

    return decorations

def CatMullRom(P0, P1, P2, P3):
    G = np.concatenate((P0, P1, P2, P3), axis=1)
    M_CR = np.array([[0, -1/2, 2/2, -1/2],
                     [2/2, 0, -5/2, 3/2],
                     [0, 1/2, 4/2, -3/2],
                     [0, 0, -1/2, 1/2]])
    return np.matmul(G, M_CR)

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def evalCurve(N, offset):
    
    Pp0 = np.array([[0 + offset, -1.5, 0]]).T
    Pp1 = np.array([[0 + offset, -0.5, 0]]).T
    Pp2 = np.array([[-0.5 + offset, -0.25, 0]]).T
    Pp3 = np.array([[0 + offset, 0, 0]]).T
    Pp4 = np.array([[0.5 + offset, 0.25 , 0]]).T
    Pp5 = np.array([[0 + offset, 0.5 , 0]]).T
    Pp6 = np.array([[-0.5 + offset, 0.25 , 0]]).T

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

def createRiver():
    vertices = []
    indices = []
    curve = evalCurve(64, 0.0)
    oCurve = evalCurve(64, 0.4)

    counter = 0
    for i in range(len(curve)- 1):
        c_0 = curve[i]
        o_0= oCurve[i]
        c_1 = curve[i+1]
        o_1= oCurve[i+1]
        
        vertices+=[c_0[0], c_0[1], 0, 0, 0, 1]
        vertices+=[o_0[0], o_0[1], 0, 0, 0, 1]
        vertices+=[c_1[0], c_1[1], 0, 0, 0, 1]
        vertices+=[o_1[0], o_1[1], 0, 0, 0, 1]

        indices += [counter + 0, counter + 1, counter + 2]
        indices += [counter + 2, counter + 3, counter + 1]

        counter+=4

    return bs.Shape(vertices, indices)

def createBoat():
    vertices = [
        0.2, -0.2,0.02, 122/255, 72/255, 11/255,
        0.2, 0.2, 0.02, 122/255, 72/255, 11/255,
        -0.2, 0.2, 0.02, 122/255, 72/255, 11/255,
        -0.2, -0.2, 0.02, 122/255, 72/255, 11/255,

        0.3, -0.3,0.5, 132/255, 82/255, 21/255,
        0.3, 0.3, 0.5, 132/255, 82/255, 21/255,
        -0.3, 0.3, 0.5, 132/255, 82/255, 21/255,
        -0.3, -0.3, 0.5, 132/255, 82/255, 21/255,
    ]
    indices = [
        0, 1, 2,
        2, 3, 0,
        0,1,5,
        5,4,0,
        1,2,6,
        6,5,1,
        2,3,7,
        7,6,2,
        3,7,4,
        4,0,3
    ]
    return bs.Shape(vertices, indices)


############################################################################

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
###########################################################
        self.theta = np.pi
        self.eye = [0, 0, 0.1]
        self.at = [0, 1, 0.1]
        self.up = [0, 0, 1]
###########################################################


# global controller as communication with the callback function
controller = Controller()

class boat:
    def __init__(self, aCurve):
        self.curve = aCurve
        self.model = None
        self.controller = None
        self.index = 0
        self.pos = self.curve[0]
        self.transform = 0
    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model
        self.transform = self.model.transform

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def moveBoat(self):
        if self.index < len(self.curve) - 3:
            self.index += 1
            self.pos = self.curve[self.index]
    
    def update(self):
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], self.pos[2]+0.01),self.transform])

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS and action != glfw.REPEAT:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_H:
        daBoat.moveBoat()

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    
###########################################################

    elif key == glfw.KEY_W:
        controller.eye += (controller.at - controller.eye) * 0.05
        controller.at += (controller.at - controller.eye) * 0.05
    elif key == glfw.KEY_D:
        controller.theta -= np.pi*0.05
    elif key == glfw.KEY_A:
        controller.theta += np.pi*0.05

###########################################################
    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Dice", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colors
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

###########################################################################################
    # Creating shapes on GPU memory

    decorations = create_decorations(colorShaderProgram)
    skybox = create_skybox(textureShaderProgram)
    floor = create_floor(textureShaderProgram)

    riverShape = createRiver()
    gpuRiver = es.GPUShape().initBuffers()
    colorShaderProgram.setupVAO(gpuRiver)
    gpuRiver.fillBuffers(riverShape.vertices, riverShape.indices, GL_STATIC_DRAW)
    river = sg.SceneGraphNode("river")
    river.childs = [gpuRiver]

    boatShape = createBoat()
    gpuBoat = es.GPUShape().initBuffers()
    colorShaderProgram.setupVAO(gpuBoat)
    gpuBoat.fillBuffers(boatShape.vertices, boatShape.indices, GL_STATIC_DRAW)
    boatNode = sg.SceneGraphNode("boat")
    boatNode.transform = tr.matmul([tr.scale(0.2, 0.3, 0.1)])
    boatNode.childs = [gpuBoat]
    boatCurve = evalCurve(64,0.2)
    # Necesito que la curva del bote sea igual al rio escalado
    # tengo que escalar la componente 'y' por el mismo valor
    for i in range(len(boatCurve) - 1):
        boatCurve[i][1] *= 2.0
    daBoat = boat(boatCurve)
    daBoat.set_controller(controller)
    daBoat.set_model(boatNode)

###########################################################################################

    # View and projection
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        theta = -10 * glfw.get_time()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        daBoat.update()

###########################################################################

        at_x = controller.eye[0] + np.cos(controller.theta)
        at_y = controller.eye[1] + np.sin(controller.theta)
        controller.at = np.array([at_x, at_y, controller.at[2]])

        view = tr.lookAt(controller.eye, controller.at, controller.up)

###########################################################################

        # Drawing (no texture)
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        #glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        river.transform = tr.matmul([tr.scale(1.0,2.0,1.0),tr.translate(0,0,0.01)])

        sg.drawSceneGraphNode(decorations, colorShaderProgram, "model")
        sg.drawSceneGraphNode(river, colorShaderProgram, "model")
        sg.drawSceneGraphNode(boatNode, colorShaderProgram, "model")

        # Drawing dice (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        #glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")
        sg.drawSceneGraphNode(floor, textureShaderProgram, "model")       

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
