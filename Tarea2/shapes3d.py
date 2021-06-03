"""Funciones para crear distintas figuras y escenas en 3D """

from model import articulation
import numpy as np
import math
from OpenGL.GL import *
from numpy.core.numeric import indices
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg
import openmesh as om
import random

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

def createScene(pipeline):

    gpuRedCube = createGPUShape(pipeline, bs.createColorNormalsCube(1, 0, 0))
    gpuGreenCube = createGPUShape(pipeline, bs.createColorNormalsCube(0, 1, 0))
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.7, 0.7, 0.7))
    gpuWhiteCube = createGPUShape(pipeline, bs.createColorNormalsCube(1, 1, 1))

    redCubeNode = sg.SceneGraphNode("redCube")
    redCubeNode.childs = [gpuRedCube]

    greenCubeNode = sg.SceneGraphNode("greenCube")
    greenCubeNode.childs = [gpuGreenCube]

    grayCubeNode = sg.SceneGraphNode("grayCube")
    grayCubeNode.childs = [gpuGrayCube]

    whiteCubeNode = sg.SceneGraphNode("whiteCube")
    whiteCubeNode.childs = [gpuWhiteCube]

    rightWallNode = sg.SceneGraphNode("rightWall")
    rightWallNode.transform = tr.translate(1, 0, 0)
    rightWallNode.childs = [redCubeNode]

    leftWallNode = sg.SceneGraphNode("leftWall")
    leftWallNode.transform = tr.translate(-1, 0, 0)
    leftWallNode.childs = [greenCubeNode]

    backWallNode = sg.SceneGraphNode("backWall")
    backWallNode.transform = tr.translate(0,-1, 0)
    backWallNode.childs = [grayCubeNode]

    lightNode = sg.SceneGraphNode("lightSource")
    lightNode.transform = tr.matmul([tr.translate(0, 0, -0.4), tr.scale(0.12, 0.12, 0.12)])
    lightNode.childs = [grayCubeNode]

    ceilNode = sg.SceneGraphNode("ceil")
    ceilNode.transform = tr.translate(0, 0, 1)
    ceilNode.childs = [grayCubeNode, lightNode]

    floorNode = sg.SceneGraphNode("floor")
    floorNode.transform = tr.translate(0, 0, -1)
    floorNode.childs = [grayCubeNode]

    sceneNode = sg.SceneGraphNode("scene")
    sceneNode.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(5, 5, 5)])
    sceneNode.childs = [rightWallNode, leftWallNode, backWallNode, ceilNode, floorNode]

    trSceneNode = sg.SceneGraphNode("tr_scene")
    trSceneNode.childs = [sceneNode]

    return trSceneNode

def createBodyScene(pipeline, babyNode):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.7, 0.7, 0.7))
    articulationShape = createGPUShape(pipeline, createColorNormalSphere(64, 0.4, 0.4, 0.4))
    
    neckNode = sg.SceneGraphNode("neck")
    neckNode.transform = tr.matmul([tr.uniformScale(0.15)])
    neckNode.childs = [articulationShape]

    leftShoulder = sg.SceneGraphNode("leftShoulder")
    leftShoulder.transform = tr.matmul([tr.translate(-0.3,0,0.0) ,tr.uniformScale(0.15)])
    leftShoulder.childs = [articulationShape]

    leftArmPart = sg.SceneGraphNode("leftArmPart")
    leftArmPart.transform = tr.matmul([tr.translate(-0.4,0,-0.15) ,tr.scale(0.1,0.1,0.4)])
    leftArmPart.childs = [gpuGrayCube]

    leftElbowPart = sg.SceneGraphNode("leftElbowPart")
    leftElbowPart.transform = tr.matmul([tr.translate(-0.4,0,-0.4) ,tr.uniformScale(0.15)])
    leftElbowPart.childs = [articulationShape]

    leftLowerPart = sg.SceneGraphNode("leftLowerPart")
    leftLowerPart.transform = tr.matmul([tr.translate(-0.4,0,-0.55) ,tr.scale(0.1,0.1,0.2)])
    leftLowerPart.childs = [gpuGrayCube]

    leftForearm = sg.SceneGraphNode("leftForearm") # Agragar la mano
    leftForearm.childs = [leftElbowPart, leftLowerPart]

    leftArm = sg.SceneGraphNode("leftArm")
    leftArm.childs = [leftShoulder, leftArmPart, leftForearm]

    rightShoulder = sg.SceneGraphNode("rightShoulder")
    rightShoulder.transform = tr.matmul([tr.translate(0.3,0,0.0) ,tr.uniformScale(0.15)])
    rightShoulder.childs = [articulationShape]

    rightArmPart = sg.SceneGraphNode("rightArmPart")
    rightArmPart.transform = tr.matmul([tr.translate(0.4,0,-0.15) ,tr.scale(0.1,0.1,0.4)])
    rightArmPart.childs = [gpuGrayCube]

    rightElbowPart = sg.SceneGraphNode("rigthElbowPart")
    rightElbowPart.transform = tr.matmul([tr.translate(0.4,0,-0.4) ,tr.uniformScale(0.15)])
    rightElbowPart.childs = [articulationShape]

    rightLowerPart = sg.SceneGraphNode("rightLowerPart")
    rightLowerPart.transform = tr.matmul([tr.translate(0.4,0,-0.55) ,tr.scale(0.1,0.1,0.2)])
    rightLowerPart.childs = [gpuGrayCube]

    rightForearm = sg.SceneGraphNode("rightForearm") # Agragar la mano
    rightForearm.childs = [rightElbowPart, rightLowerPart]

    rightArm = sg.SceneGraphNode("rightArm")
    rightArm.childs = [rightShoulder, rightArmPart, rightForearm]

    leftSomething = sg.SceneGraphNode("leftSomething")
    leftSomething.transform = tr.matmul([tr.translate(-0.2,0.0,-0.7) ,tr.uniformScale(0.15)])
    leftSomething.childs = [articulationShape]

    leftLegPart = sg.SceneGraphNode("leftLegPart")
    leftLegPart.transform = tr.matmul([tr.translate(-0.3,0,-1.0) ,tr.scale(0.1,0.1,0.6)])
    leftLegPart.childs = [gpuGrayCube]

    leftLeg = sg.SceneGraphNode("leftLeg")
    leftLeg.childs = [leftSomething, leftLegPart]

    rightSomething = sg.SceneGraphNode("leftSomething")
    rightSomething.transform = tr.matmul([tr.translate(0.2,0,-0.7) ,tr.uniformScale(0.15)])
    rightSomething.childs = [articulationShape]

    rightLegPart = sg.SceneGraphNode("leftLegPart")
    rightLegPart.transform = tr.matmul([tr.translate(0.3,0,-1.0) ,tr.scale(0.1,0.1,0.6)])
    rightLegPart.childs = [gpuGrayCube]

    rightLeg = sg.SceneGraphNode("rightLeg")
    rightLeg.childs = [rightSomething, rightLegPart]

    extremidades = sg.SceneGraphNode("extremidades")
    extremidades.childs = [leftArm, rightArm, leftLeg, rightLeg]

    headRotationNode = sg.SceneGraphNode("headRotation")
    headRotationNode.childs=[neckNode, babyNode]

    wholeBody = sg.SceneGraphNode("wholeBody")
    wholeBody.childs = [extremidades, headRotationNode]

    return wholeBody

def createCube1(pipeline):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.5, 0.5, 0.5))

    grayCubeNode = sg.SceneGraphNode("grayCube")
    grayCubeNode.childs = [gpuGrayCube]

    objectNode = sg.SceneGraphNode("object1")
    objectNode.transform = tr.matmul([
        tr.translate(0.25,-0.15,-0.25),
        tr.rotationZ(np.pi*0.15),
        tr.scale(0.2,0.2,0.5)
    ])
    objectNode.childs = [grayCubeNode]

    scaledObject = sg.SceneGraphNode("object1")
    scaledObject.transform = tr.scale(5, 5, 5)
    scaledObject.childs = [objectNode]

    return scaledObject

def createCube2(pipeline):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.5, 0.5, 0.5))

    grayCubeNode = sg.SceneGraphNode("grayCube")
    grayCubeNode.childs = [gpuGrayCube]

    objectNode = sg.SceneGraphNode("object1")
    objectNode.transform = tr.matmul([
        tr.translate(-0.25,-0.15,-0.35),
        tr.rotationZ(np.pi*-0.2),
        tr.scale(0.3,0.3,0.3)
    ])
    objectNode.childs = [grayCubeNode]

    scaledObject = sg.SceneGraphNode("object1")
    scaledObject.transform = tr.scale(5, 5, 5)
    scaledObject.childs = [objectNode]

    return scaledObject

def createTorax():
    vertices = [
        0.2, -0.3, 0.4, 0.33, 0.0, 1, -1, 1, # 0
        0.2, 0.3, 0.4, 0.66, 0.0, 1, 1, 1, # 1
        -0.2, 0.3, 0.4, 1, 0.0, -1, 1, 1, # 2
        -0.2, -0.3, 0.4, 0, 0, -1, -1, 1, # 3
        0.25, 0.0, 0.4, 0.5, 0, 1, 1, 1, # 4

        0.15, -0.2, 0.0, 0.2, 0.8, 1, -1, 0, # 5
        0.15, 0.2, 0.0, 0.8, 0.8, 1, 1, 0, # 6
        -0.15, 0.2, 0.0, 1, 0.8, -1, 1, 0, # 7
        -0.15, -0.2, 0.0, 0, 0.8, -1, -1, 0, # 8

        0.1, -0.15, -0.4, 0.33, 1, 1, -1, -1, # 9
        0.1, 0.15, -0.4, 0.66, 1, 1, 1, -1, # 10
        -0.1, 0.15, -0.4, 1, 1, -1, 1, -1, # 11
        -0.1, -0.15, -0.4, 0, 1, -1, -1, -1 # 12
    ]
    indices = [
        0,1,2,
        2,3,0,
        0,1,4,
        0,5,4,
        4,6,1,
        4,5,6,
        1,6,7,
        7,2,1,
        2,7,8,
        8,3,2,
        3,8,5,
        5,0,3,
        5,9,10,
        10,6,5,
        6,10,11,
        11,7,6,
        7,11,12,
        12,8,7,
        8,12,9,
        9,5,8,
        9,10,11,
        11,12,9
    ]
    return bs.Shape(vertices, indices)

def createColorNormalSphere(N, red, g, b):

    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.5
    c = 0

    for i in range(N - 1):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [r*np.sin(theta)*np.cos(phi), r*np.sin(theta)*np.sin(phi), r*np.cos(theta)]
            v1 = [r*np.sin(theta1)*np.cos(phi), r*np.sin(theta1)*np.sin(phi), r*np.cos(theta1)]
            v2 = [r*np.sin(theta1)*np.cos(phi1), r*np.sin(theta1)*np.sin(phi1), r*np.cos(theta1)]
            v3 = [r*np.sin(theta)*np.cos(phi1), r*np.sin(theta)*np.sin(phi1), r*np.cos(theta)]
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]


            # Creamos los quad superiores
            if i == 0:
                vertices += [v0[0], v0[1], v0[2], red, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], red, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], red, g, b, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], red, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], red, g, b, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], red, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], red, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], red, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], red, g, b, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], red, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)

def createSphereMesh(N,r,g,b):
    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.5
    c = 0

    sphereMesh = om.TriMesh()

    for i in range(N - 1):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [r*np.sin(theta)*np.cos(phi), r*np.sin(theta)*np.sin(phi), r*np.cos(theta)]
            v1 = [r*np.sin(theta1)*np.cos(phi), r*np.sin(theta1)*np.sin(phi), r*np.cos(theta1)]
            v2 = [r*np.sin(theta1)*np.cos(phi1), r*np.sin(theta1)*np.sin(phi1), r*np.cos(theta1)]
            v3 = [r*np.sin(theta)*np.cos(phi1), r*np.sin(theta)*np.sin(phi1), r*np.cos(theta)]
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]


            # Creamos los quad superiores
            if i == 0:
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
                vh0 = sphereMesh.add_vertex([v0[0], v0[1], v0[2]])
                vh1 = sphereMesh.add_vertex([v1[0], v1[1], v1[2]])
                vh2 = sphereMesh.add_vertex([v2[0], v2[1], v2[2]])
                sphereMesh.add_face(vh0, vh1, vh2)
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
                vh0 = sphereMesh.add_vertex([v0[0], v0[1], v0[2]])
                vh1 = sphereMesh.add_vertex([v1[0], v1[1], v1[2]])
                vh2 = sphereMesh.add_vertex([v2[0], v2[1], v2[2]])
                sphereMesh.add_face(vh0, vh1, vh2)
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
                vh0 = sphereMesh.add_vertex([v0[0], v0[1], v0[2]])
                vh1 = sphereMesh.add_vertex([v1[0], v1[1], v1[2]])
                vh2 = sphereMesh.add_vertex([v2[0], v2[1], v2[2]])
                vh3 = sphereMesh.add_vertex([v3[0], v3[1], v3[2]])
                sphereMesh.add_face(vh0, vh1, vh2)
                sphereMesh.add_face(vh2, vh3, vh0)
    return sphereMesh

def get_vertexs_and_indexes(mesh):
    # Obtenemos las caras de la malla
    faces = mesh.faces()

    # Creamos una lista para los vertices e indices
    vertexs = []

    # Obtenemos los vertices y los recorremos
    for vertex in mesh.points():
        vertexs += vertex.tolist()
        # Agregamos un color al azar
        vertexs += [0, 0, 0]

    indexes = []

    for face in faces:
        # Obtenemos los vertices de la cara
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            # Obtenemos el numero de indice y lo agregamos a la lista
            indexes += [vertex.idx()]

    return vertexs, indexes

def createTextureNormalSphere(N):
    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.5
    c = 0

    for i in range(N - 1):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [r*np.sin(theta)*np.cos(phi), r*np.sin(theta)*np.sin(phi), r*np.cos(theta)]
            v1 = [r*np.sin(theta1)*np.cos(phi), r*np.sin(theta1)*np.sin(phi), r*np.cos(theta1)]
            v2 = [r*np.sin(theta1)*np.cos(phi1), r*np.sin(theta1)*np.sin(phi1), r*np.cos(theta1)]
            v3 = [r*np.sin(theta)*np.cos(phi1), r*np.sin(theta)*np.sin(phi1), r*np.cos(theta)]
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]


            # Creamos los quad superiores
            if i == 0:
                vertices += [v0[0], v0[1], v0[2], 0, 1, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 1, 1, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 0.5, 0, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0.5, 1, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], 1, 0, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0, 1, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], 0, 1, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)

def createColorTorus(N):
    vertices = []
    indices = []
    dPhi = 2 * np.pi/N
    dTheta = 2 * np.pi/N
    c= 0
    for i in range(N):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi

            v0 = [(0.5 + 0.1*np.cos(theta))*np.cos(phi), (0.5 + 0.1*np.cos(theta))*np.sin(phi), 0.1 * np.sin(theta)]
            v1 = [(0.5 + 0.1*np.cos(theta1))*np.cos(phi), (0.5 + 0.1*np.cos(theta1))*np.sin(phi), 0.1 * np.sin(theta1)]
            v2 = [(0.5 + 0.1*np.cos(theta1))*np.cos(phi1), (0.5 + 0.1*np.cos(theta1))*np.sin(phi1), 0.1 * np.sin(theta1)]
            v3 = [(0.5 + 0.1*np.cos(theta))*np.cos(phi1), (0.5 + 0.1*np.cos(theta))*np.sin(phi1), 0.1 * np.sin(theta)]

            n0 = [(0.5 + np.cos(theta))*np.cos(phi), (0.5 + np.cos(theta))*np.sin(phi),  np.sin(theta)]
            n1 = [(0.5 + np.cos(theta1))*np.cos(phi), (0.5 + np.cos(theta1))*np.sin(phi), np.sin(theta1)]
            n2 = [(0.5 + np.cos(theta1))*np.cos(phi1), (0.5 + np.cos(theta1))*np.sin(phi1),  np.sin(theta1)]
            n3 = [(0.5 + np.cos(theta))*np.cos(phi1), (0.5 + np.cos(theta))*np.sin(phi1),   np.sin(theta)]

            vertices += [v0[0], v0[1], v0[2], 0.3, 0.3, 0.3, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], 0.3, 0.3, 0.3, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], 0.3, 0.3, 0.3, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], 0.3, 0.3, 0.3, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4
    
    return bs.Shape(vertices, indices)

def createTextureTorus(N):
    vertices = []
    indices = []
    dPhi = 2 * np.pi/N
    dTheta = 2 * np.pi/N
    c= 0
    for i in range(N):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi

            v0 = [(0.5 + 0.1*np.cos(theta))*np.cos(phi), (0.5 + 0.1*np.cos(theta))*np.sin(phi), 0.1 * np.sin(theta)]
            v1 = [(0.5 + 0.1*np.cos(theta1))*np.cos(phi), (0.5 + 0.1*np.cos(theta1))*np.sin(phi), 0.1 * np.sin(theta1)]
            v2 = [(0.5 + 0.1*np.cos(theta1))*np.cos(phi1), (0.5 + 0.1*np.cos(theta1))*np.sin(phi1), 0.1 * np.sin(theta1)]
            v3 = [(0.5 + 0.1*np.cos(theta))*np.cos(phi1), (0.5 + 0.1*np.cos(theta))*np.sin(phi1), 0.1 * np.sin(theta)]

            n0 = [(0.5 + np.cos(theta))*np.cos(phi), (0.5 + np.cos(theta))*np.sin(phi),  np.sin(theta)]
            n1 = [(0.5 + np.cos(theta1))*np.cos(phi), (0.5 + np.cos(theta1))*np.sin(phi), np.sin(theta1)]
            n2 = [(0.5 + np.cos(theta1))*np.cos(phi1), (0.5 + np.cos(theta1))*np.sin(phi1),  np.sin(theta1)]
            n3 = [(0.5 + np.cos(theta))*np.cos(phi1), (0.5 + np.cos(theta))*np.sin(phi1),   np.sin(theta)]

            vertices += [v0[0], v0[1], v0[2], 0, 1, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], 0, 1, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], 0, 1, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4
    
    return bs.Shape(vertices, indices)


def createSphMshNode(pipeline):
    sphereMesh = createSphereMesh(64,0,0,0)
    sphereMesh_vertices, sphereMesh_indices = get_vertexs_and_indexes(sphereMesh)

    gpuSphere = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSphere)
    gpuSphere.fillBuffers(sphereMesh_vertices, sphereMesh_indices, GL_STATIC_DRAW)

    sphMshNode = sg.SceneGraphNode("spere")
    sphMshNode.transform = tr.matmul([
        tr.uniformScale(0.3)
    ])
    sphMshNode.childs = [gpuSphere]

    sphRotation = sg.SceneGraphNode("sphRotation")
    sphRotation.childs = [sphMshNode]

    return sphRotation
    
def createSphereNode(r, g, b, pipeline):
    sphere = createGPUShape(pipeline, createColorNormalSphere(20, r,g,b))

    sphereNode = sg.SceneGraphNode("sphere")
    sphereNode.transform =tr.matmul([
        tr.translate(0.25,0.15,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    sphereNode.childs = [sphere]

    scaledSphere = sg.SceneGraphNode("sc_sphere")
    scaledSphere.transform = tr.scale(5, 5, 5)
    scaledSphere.childs = [sphereNode]

    return scaledSphere

def createTexSphereNode(pipeline):
    sphere = createTextureGPUShape(createTextureNormalSphere(20), pipeline, "sprites/stone.png")

    sphereNode = sg.SceneGraphNode("sphere")
    sphereNode.transform =tr.matmul([
        tr.translate(-0.25,0.25,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    sphereNode.childs = [sphere]

    scaledSphere = sg.SceneGraphNode("sc_sphere")
    scaledSphere.transform = tr.scale(5, 5, 5)
    scaledSphere.childs = [sphereNode]

    return scaledSphere

def createTorusNode(pipeline, num = 0.0):
    torus = createGPUShape(pipeline,createColorTorus(20))

    torusNode = sg.SceneGraphNode("torus")
    torusNode.transform =tr.matmul([
        tr.translate(-0.05 + num,0.15+ num,-0.18+ num),
        tr.scale(0.3,0.3,0.3)
    ])
    torusNode.childs = [torus]

    scaledTorus = sg.SceneGraphNode("sc_sphere")
    scaledTorus.transform = tr.scale(5, 5, 5)
    scaledTorus.childs = [torusNode]

    return scaledTorus

def createTexTorusNode(pipeline, num = 0.0):
    torus = createTextureGPUShape(createTextureTorus(20), pipeline, "sprites/stone.png")

    torusNode = sg.SceneGraphNode("torus")
    torusNode.transform =tr.matmul([
        tr.translate(-0.05 + num,0.15+ num,-0.18+ num),
        tr.scale(0.3,0.3,0.3)
    ])
    torusNode.childs = [torus]

    scaledTorus = sg.SceneGraphNode("sc_sphere")
    scaledTorus.transform = tr.scale(5, 5, 5)
    scaledTorus.childs = [torusNode]

    return scaledTorus