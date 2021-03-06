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
import copy

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

# Convenience function to ease initialization
def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

# Convenience function to ease initialization
def createTextureGPUShapeX(shape, pipeline,sWrapMode, tWrapMode, minFilterMode, maxFilterMode, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, sWrapMode, tWrapMode, minFilterMode, maxFilterMode)
    glGenerateMipmap(GL_TEXTURE_2D)
    return gpuShape

# creates the scene where the dance takes place
# returns sceneGraphNode
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

# creates a shape of a quad with a texture
# returns a Shape
def createTextureQuad(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions        texture
        -0.5, -0.5, 0.0,  0, ny, 1,1,1,
         0.5, -0.5, 0.0, nx, ny, 1,1,1,
         0.5,  0.5, 0.0, nx, 0, 1,1,1,
        -0.5,  0.5, 0.0,  0, 0, 1,1,1]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return bs.Shape(vertices, indices)

# creates the body that will be dancing
# return a sceneGraphNode
def createBodyScene2(pipeline, babyNode):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.7, 0.7, 0.7))
    articulationShape = createGPUShape(pipeline, createColorNormalSphere(64, 0.4, 0.4, 0.4))

    neckNode = sg.SceneGraphNode("neck")
    neckNode.transform = tr.matmul([tr.uniformScale(0.15)])
    neckNode.childs = [articulationShape]

    # Brazo Izquierdo

    leftShoulder = sg.SceneGraphNode("leftShoulder")
    leftShoulder.transform = tr.matmul([tr.uniformScale(0.15)])
    leftShoulder.childs = [articulationShape]

    leftArmPart = sg.SceneGraphNode("leftArmPart")
    leftArmPart.transform = tr.matmul([tr.translate(0.0,0,-0.2) ,tr.scale(0.1,0.1,0.4)])
    leftArmPart.childs = [gpuGrayCube]
    
    leftElbowPart = sg.SceneGraphNode("leftElbowPart")
    leftElbowPart.transform = tr.matmul([tr.translate(0.0,0,0) ,tr.uniformScale(0.15)])
    leftElbowPart.childs = [articulationShape]

    leftLowerPart = sg.SceneGraphNode("leftLowerPart")
    leftLowerPart.transform = tr.matmul([tr.translate(0.0,0,-0.15) ,tr.scale(0.1,0.1,0.2)])
    leftLowerPart.childs = [gpuGrayCube]

    leftForearmRot = sg.SceneGraphNode("leftForearmRot")
    leftForearmRot.childs = [leftElbowPart, leftLowerPart]

    leftForeArm = sg.SceneGraphNode("leftForearm")
    leftForeArm.transform = tr.translate(0, 0, -0.4)
    leftForeArm.childs = [leftForearmRot]

    leftArmRot = sg.SceneGraphNode("leftArmRot")
    leftArmRot.childs = [leftShoulder, leftArmPart, leftForeArm]

    leftArm = sg.SceneGraphNode("leftArm")
    leftArm.transform = tr.translate(-0.35, 0, 0)
    leftArm.childs = [leftArmRot]

    # Brazo Derecho

    rightShoulder = sg.SceneGraphNode("rightShoulder")
    rightShoulder.transform = tr.matmul([tr.uniformScale(0.15)])
    rightShoulder.childs = [articulationShape]

    rightArmPart = sg.SceneGraphNode("rightArmPart")
    rightArmPart.transform = tr.matmul([tr.translate(0.0,0,-0.2) ,tr.scale(0.1,0.1,0.4)])
    rightArmPart.childs = [gpuGrayCube]
    
    rightElbowPart = sg.SceneGraphNode("rightElbowPart")
    rightElbowPart.transform = tr.matmul([tr.translate(0.0,0,0) ,tr.uniformScale(0.15)])
    rightElbowPart.childs = [articulationShape]

    rightLowerPart = sg.SceneGraphNode("rightLowerPart")
    rightLowerPart.transform = tr.matmul([tr.translate(0.0,0,-0.15) ,tr.scale(0.1,0.1,0.2)])
    rightLowerPart.childs = [gpuGrayCube]

    rightForearmRot = sg.SceneGraphNode("rightForearmRot")
    rightForearmRot.childs = [rightElbowPart, rightLowerPart]

    rightForeArm = sg.SceneGraphNode("rightForearm")
    rightForeArm.transform = tr.translate(0, 0, -0.4)
    rightForeArm.childs = [rightForearmRot]

    rightArmRot = sg.SceneGraphNode("rightArmRot")
    rightArmRot.childs = [rightShoulder, rightArmPart, rightForeArm]

    rightArm = sg.SceneGraphNode("rightArm")
    rightArm.transform = tr.translate(0.35, 0, 0)
    rightArm.childs = [rightArmRot]

    # Pierna Izquierda

    leftSomething = sg.SceneGraphNode("leftSomething")
    leftSomething.transform = tr.matmul([tr.uniformScale(0.15)])
    leftSomething.childs = [articulationShape]

    leftLegPart = sg.SceneGraphNode("leftLegPart")
    leftLegPart.transform = tr.matmul([tr.translate(0,0,-0.3) ,tr.scale(0.1,0.1,0.6)])
    leftLegPart.childs = [gpuGrayCube]

    leftLegRot = sg.SceneGraphNode("leftLegRot")
    leftLegRot.childs = [leftSomething, leftLegPart]

    leftLeg = sg.SceneGraphNode("leftLeg")
    leftLeg.transform = tr.translate(-0.2, 0,-0.7)
    leftLeg.childs = [leftLegRot]

    # Pierna Derecha

    rightSomething = sg.SceneGraphNode("rightSomething")
    rightSomething.transform = tr.matmul([tr.uniformScale(0.15)])
    rightSomething.childs = [articulationShape]

    rightLegPart = sg.SceneGraphNode("rightLegPart")
    rightLegPart.transform = tr.matmul([tr.translate(0,0,-0.3) ,tr.scale(0.1,0.1,0.6)])
    rightLegPart.childs = [gpuGrayCube]

    rightLegRot = sg.SceneGraphNode("rightLegRot")
    rightLegRot.childs = [rightSomething, rightLegPart]

    rightLeg = sg.SceneGraphNode("rightLeg")
    rightLeg.transform = tr.translate(0.2, 0,-0.7)
    rightLeg.childs = [rightLegRot]

    # Cuerpo completo

    extremidades = sg.SceneGraphNode("extremidades")
    extremidades.childs = [leftArm, rightArm, leftLeg, rightLeg]

    headNode = sg.SceneGraphNode("headNode")
    headNode.transform = tr.translate(0, 0, 0.0)
    headNode.childs = [neckNode, babyNode]

    headRotationNode = sg.SceneGraphNode("headRotation")
    headRotationNode.childs=[headNode]

    wholeBody = sg.SceneGraphNode("wholeBody")
    wholeBody.childs = [extremidades, headRotationNode]

    return wholeBody

# creates the shape of a STAR, dont mind the name
# returns a Shape
def hanger():
    vertices = [
        0, 0.5, 0, 1, 1, 1,       # 0
        -0.5, -0.5, 0, 1, 1, 1,   # 1
        0.5, -0.5, 0, 1, 1, 1,    # 2
        -0.7, 0, 0, 1, 1, 1,      # 3
        0.7, 0, 0, 1, 1, 1        # 4
    ]
    indices = [1,0, 2, 3, 2, 0, 4, 3, 4, 1]
    return bs.Shape(vertices, indices)

# creates a node with a cube and its transformations
# returns a sceneGraphNode
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

# creates a node with a cube and its transformations
# returns a sceneGraphNode
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

# creates the shape of the central part of the body
# returns a Shape with textures
def createTorax():
    vertices = [
        0.2, -0.3, 0.4, 0.33, 0.0, 1, -1, 1,  # 0
        0.2, 0.3, 0.4, 0.66, 0.0, 1, 1, 1,    # 1
        -0.2, 0.3, 0.4, 1, 0.0, -1, 1, 1,     # 2
        -0.2, -0.3, 0.4, 0, 0, -1, -1, 1,     # 3
        0.25, 0.0, 0.4, 0.5, 0, 1, 1, 1,      # 4

        0.15, -0.2, 0.0, 0.2, 0.8, 1, -1, 0,  # 5
        0.15, 0.2, 0.0, 0.8, 0.8, 1, 1, 0,    # 6
        -0.15, 0.2, 0.0, 1, 0.8, -1, 1, 0,    # 7
        -0.15, -0.2, 0.0, 0, 0.8, -1, -1, 0,  # 8

        0.1, -0.15, -0.4, 0.33, 1, 1, -1, -1, # 9
        0.1, 0.15, -0.4, 0.66, 1, 1, 1, -1,   # 10
        -0.1, 0.15, -0.4, 1, 1, -1, 1, -1,    # 11
        -0.1, -0.15, -0.4, 0, 1, -1, -1, -1   # 12
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

# creates a shape of a sphere
# returns a Shape 
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

# creates the mesh of a Sphere
# returns a Mesh
def createSphereMesh(N,r,g,b):
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.5

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
                vh0 = sphereMesh.add_vertex([v0[0], v0[1], v0[2]])
                vh1 = sphereMesh.add_vertex([v1[0], v1[1], v1[2]])
                vh2 = sphereMesh.add_vertex([v2[0], v2[1], v2[2]])
                sphereMesh.add_face(vh0, vh1, vh2)
            # Creamos los quads inferiores
            elif i == (N-2):
                vh0 = sphereMesh.add_vertex([v0[0], v0[1], v0[2]])
                vh1 = sphereMesh.add_vertex([v1[0], v1[1], v1[2]])
                vh2 = sphereMesh.add_vertex([v2[0], v2[1], v2[2]])
                sphereMesh.add_face(vh0, vh1, vh2)
            
            # Creamos los quads intermedios
            else: 
                vh0 = sphereMesh.add_vertex([v0[0], v0[1], v0[2]])
                vh1 = sphereMesh.add_vertex([v1[0], v1[1], v1[2]])
                vh2 = sphereMesh.add_vertex([v2[0], v2[1], v2[2]])
                vh3 = sphereMesh.add_vertex([v3[0], v3[1], v3[2]])
                sphereMesh.add_face(vh0, vh1, vh2)
                sphereMesh.add_face(vh2, vh3, vh0)
    return sphereMesh

# get function to the vertexes and indexes of a mesh
# returns a list
def get_vertexs_and_indexes(mesh, color):
    # Obtenemos las caras de la malla
    faces = mesh.faces()

    mesh.request_face_normals()
    mesh.request_vertex_normals()
    mesh.update_normals()

    r = color[0]
    g = color[1]
    b = color[2]
    # Creamos una lista para los vertices e indices
    vertexs = []
    indexes = []

    def extractCoordinates(numpyVector3):
        assert len(numpyVector3) == 3
        x = vertex[0]
        y = vertex[1]
        z = vertex[2]
        return [x,y,z]

    for faceIt in mesh.faces():
        faceId = faceIt.idx()

        # Checking each vertex of the face
        for faceVertexIt in mesh.fv(faceIt):
            faceVertexId = faceVertexIt.idx()

            # Obtaining the position and normal of each vertex
            vertex = mesh.point(faceVertexIt)
            normal = mesh.normal(faceVertexIt)

            x, y, z = extractCoordinates(vertex)
            nx, ny, nz = extractCoordinates(normal)

            vertexs += [x, y, z, r, g, b, nx, ny, nz]
            indexes += [len(vertexs)//9 - 1]

    # Obtenemos los vertices y los recorremos
    """
    for vertex in mesh.points():
        vertexs += vertex.tolist()
        # Agregamos un color al azar
        vertexs += [r, g, b]
    """

    """
    for face in faces:
        # Obtenemos los vertices de la cara
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            # Obtenemos el numero de indice y lo agregamos a la lista
            indexes += [vertex.idx()]
    """

    return vertexs, indexes

# creates a shape of sphere with textures
# returns a Shape
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

# creates the shape of a torus
# returns a Shape
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

# creates the shape of a torus with textures
# returns a Shape
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

            vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], 0, 1, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], 0, 1, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4
    
    return bs.Shape(vertices, indices)

# creates the shape of a cube with normals and textures
# returns a Shape
def createTextureNormalsCube(nx, ny):

    # Defining locations,texture coordinates and normals for each vertex of the shape  
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    0, ny,        0,0,1,
         0.5, -0.5,  0.5,    nx, ny,        0,0,1,
         0.5,  0.5,  0.5,    nx, 0,        0,0,1,
        -0.5,  0.5,  0.5,    0, 0,        0,0,1,   
    # Z-          
        -0.5, -0.5, -0.5,    0, ny,        0,0,-1,
         0.5, -0.5, -0.5,    nx, ny,        0,0,-1,
         0.5,  0.5, -0.5,    nx, 0,        0,0,-1,
        -0.5,  0.5, -0.5,    0, 0,        0,0,-1,
       
    # X+          
         0.5, -0.5, -0.5,    0, ny,        1,0,0,
         0.5,  0.5, -0.5,    nx, ny,        1,0,0,
         0.5,  0.5,  0.5,    nx, 0,        1,0,0,
         0.5, -0.5,  0.5,    0, 0,        1,0,0,   
    # X-          
        -0.5, -0.5, -0.5,    0, ny,        -1,0,0,
        -0.5,  0.5, -0.5,    nx, ny,        -1,0,0,
        -0.5,  0.5,  0.5,    nx, 0,        -1,0,0,
        -0.5, -0.5,  0.5,    0, 0,        -1,0,0,   
    # Y+          
        -0.5,  0.5, -0.5,    0, ny,        0,1,0,
         0.5,  0.5, -0.5,    nx, ny,        0,1,0,
         0.5,  0.5,  0.5,    nx, 0,        0,1,0,
        -0.5,  0.5,  0.5,    0, 0,        0,1,0,   
    # Y-          
        -0.5, -0.5, -0.5,    0, ny,        0,-1,0,
         0.5, -0.5, -0.5,    nx, ny,        0,-1,0,
         0.5, -0.5,  0.5,    nx, 0,        0,-1,0,
        -0.5, -0.5,  0.5,    0, 0,        0,-1,0
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices)

# creates a node for the sphere mesh
# returns a sceneGraphNode
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

# creates a node of a sphere
# returns a Node  
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

# creates a node of a sphere with textures
# returns a sceneGraphNode
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

# creates a node of a torus
# returns a sceneGraphNode
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

# creates a node of torus with textures
# returns a sceneGraphNode
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