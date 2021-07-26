"""Funciones para crear distintas figuras y escenas en 3D """

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

def createBlackCircle(N):

    # First vertex at the center, white color
    vertices = [0, 0, 0, 0.0, 0.0, 0.0]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # Black color
                  0,       0, 0]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

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
    return vertexs, indexes

# creates a shape of sphere with textures
# returns a Shape
def createTextureNormalSphere(N, u_i, u_f, v_i, v_f):
    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.5
    c = 0

    for i in range(N//2):
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
            
            # Creamos los quads intermedios
            vertices += [v0[0], v0[1], v0[2], u_i + phi/(2*np.pi)* (u_f - u_i), v_i + theta/np.pi * (v_f - v_i), n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], u_i + phi/(2*np.pi)* (u_f - u_i), v_i + theta1/np.pi* (v_f - v_i), n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], u_i + phi1/(2*np.pi)* (u_f - u_i), v_i + theta1/np.pi* (v_f - v_i), n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], u_i + phi1/(2*np.pi)* (u_f - u_i), v_i + theta/np.pi* (v_f - v_i), n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4
    return bs.Shape(vertices, indices)

def createPoolBalls(pipeline):
    gpuBall1 = createTextureGPUShape(createTextureNormalSphere(50, 0, 1/3, 0, 1/6), pipeline, "sprites/pool.png")
    gpuBall2 = createTextureGPUShape(createTextureNormalSphere(50, 1/3, 2/3, 0, 1/6), pipeline, "sprites/pool.png")
    gpuBall3 = createTextureGPUShape(createTextureNormalSphere(50, 2/3, 1, 0, 1/6), pipeline, "sprites/pool.png")
    gpuBall4 = createTextureGPUShape(createTextureNormalSphere(50, 0, 1/3, 1/6, 2/6), pipeline, "sprites/pool.png")
    gpuBall5 = createTextureGPUShape(createTextureNormalSphere(50, 1/3, 2/3, 1/6, 2/6), pipeline, "sprites/pool.png")
    gpuBall6 = createTextureGPUShape(createTextureNormalSphere(50, 2/3, 1, 1/6, 2/6), pipeline, "sprites/pool.png")
    gpuBall7 = createTextureGPUShape(createTextureNormalSphere(50, 0, 1/3, 2/6, 3/6), pipeline, "sprites/pool.png")
    gpuBall8 = createTextureGPUShape(createTextureNormalSphere(50, 1/3, 2/3, 2/6, 3/6), pipeline, "sprites/pool.png")
    gpuBall9 = createTextureGPUShape(createTextureNormalSphere(50, 2/3, 1, 2/6, 3/6), pipeline, "sprites/pool.png")
    gpuBall10 = createTextureGPUShape(createTextureNormalSphere(50, 0, 1/3, 3/6, 4/6), pipeline, "sprites/pool.png")

    shadow1Node = sg.SceneGraphNode("shadow1")
    shadow1Node.transform = tr.matmul([tr.translate(0,0,-0.6), tr.uniformScale(2)])
    shadow1Node.childs = []

    ball1Node = sg.SceneGraphNode("ball1")
    ball1Node.transform = tr.matmul([tr.translate(0,0,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball1Node.childs = [gpuBall1]

    bola1 = sg.SceneGraphNode("bola 1")
    bola1.childs = [ball1Node, shadow1Node]

    ball2Node = sg.SceneGraphNode("ball2")
    ball2Node.transform = tr.matmul([tr.translate(-0.4,-0.3,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball2Node.childs = [gpuBall2]
    ball3Node = sg.SceneGraphNode("ball3")
    ball3Node.transform = tr.matmul([tr.translate(-0.4,0.3,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball3Node.childs = [gpuBall3]
    ball4Node = sg.SceneGraphNode("ball4")
    ball4Node.transform = tr.matmul([tr.translate(-0.9,-0.4,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball4Node.childs = [gpuBall4]
    ball5Node = sg.SceneGraphNode("ball5")
    ball5Node.transform = tr.matmul([tr.translate(-0.9,0,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball5Node.childs = [gpuBall5]
    ball6Node = sg.SceneGraphNode("ball6")
    ball6Node.transform = tr.matmul([tr.translate(-0.9,0.4,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball6Node.childs = [gpuBall6]
    ball7Node = sg.SceneGraphNode("ball7")
    ball7Node.transform = tr.matmul([tr.translate(-1.4,-0.7,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball7Node.childs = [gpuBall7]
    ball8Node = sg.SceneGraphNode("ball8")
    ball8Node.transform = tr.matmul([tr.translate(-1.4,-0.25,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball8Node.childs = [gpuBall8]
    ball9Node = sg.SceneGraphNode("ball9")
    ball9Node.transform = tr.matmul([tr.translate(-1.4,0.25,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball9Node.childs = [gpuBall9]
    ball10Node = sg.SceneGraphNode("ball10")
    ball10Node.transform = tr.matmul([tr.translate(-1.4, 0.7,-0.5),tr.uniformScale(0.5),tr.rotationZ(np.pi/2)])
    ball10Node.childs = [gpuBall10]

    setOfBalls = sg.SceneGraphNode("set of balls")
    setOfBalls.transform = tr.matmul([tr.translate(0,0,-0.88),tr.uniformScale(0.08)])
    setOfBalls.childs = [bola1, ball2Node, ball3Node, ball4Node, ball5Node, ball6Node, ball7Node, ball8Node, ball9Node, ball10Node]

    return setOfBalls

def createCircleScore_v2(pipeline):
    gpuScore = createGPUShape(pipeline, createBlackCircle(64))

    score1Node = sg.SceneGraphNode("Score 1")
    score1Node.transform = tr.matmul([tr.translate(0.9,-0.45,-0.93),tr.uniformScale(0.1)])
    score1Node.childs = [gpuScore]

    score2Node = sg.SceneGraphNode("Score 2")
    score2Node.transform = tr.matmul([tr.translate(0.9, 0.45,-0.93),tr.uniformScale(0.1)])
    score2Node.childs = [gpuScore]

    score3Node = sg.SceneGraphNode("Score 3")
    score3Node.transform = tr.matmul([tr.translate(0.0,-0.45,-0.93),tr.uniformScale(0.1)])
    score3Node.childs = [gpuScore]

    score4Node = sg.SceneGraphNode("Score 4")
    score4Node.transform = tr.matmul([tr.translate(0.0, 0.45,-0.93),tr.uniformScale(0.1)])
    score4Node.childs = [gpuScore]

    score5Node = sg.SceneGraphNode("Score 5")
    score5Node.transform = tr.matmul([tr.translate(-0.9,-0.45,-0.93),tr.uniformScale(0.1)])
    score5Node.childs = [gpuScore]

    score6Node = sg.SceneGraphNode("Score 6")
    score6Node.transform = tr.matmul([tr.translate(-0.9, 0.45,-0.93),tr.uniformScale(0.1)])
    score6Node.childs = [gpuScore]

    scoreNode = sg.SceneGraphNode("Scores")
    scoreNode.childs = [score1Node, score2Node, score3Node, score4Node, score5Node, score6Node]

    return scoreNode

def createShadows(pipeline):
    gpuShadow = createGPUShape(pipeline, createBlackCircle(64))

    shadow1Node = sg.SceneGraphNode("Shadow1")
    shadow1Node.childs = [gpuShadow]

    shadow2Node = sg.SceneGraphNode("Shadow2")
    shadow2Node.childs = [gpuShadow]

    shadow3Node = sg.SceneGraphNode("Shadow3")
    shadow3Node.childs = [gpuShadow]

    shadow4Node = sg.SceneGraphNode("Shadow4")
    shadow4Node.childs = [gpuShadow]

    shadow5Node = sg.SceneGraphNode("Shadow5")
    shadow5Node.childs = [gpuShadow]

    shadow6Node = sg.SceneGraphNode("Shadow6")
    shadow6Node.childs = [gpuShadow]

    shadow7Node = sg.SceneGraphNode("Shadow7")
    shadow7Node.childs = [gpuShadow]

    shadow8Node = sg.SceneGraphNode("Shadow8")
    shadow8Node.childs = [gpuShadow]

    shadow9Node = sg.SceneGraphNode("Shadow9")
    shadow9Node.childs = [gpuShadow]

    shadow10Node = sg.SceneGraphNode("Shadow10")
    shadow10Node.childs = [gpuShadow]

    shadowMainNode = sg.SceneGraphNode("ShadowMain")
    shadowMainNode.childs = [gpuShadow]

    shadowNode = sg.SceneGraphNode("Scores")
    shadowNode.childs = [shadow10Node, shadow1Node, shadow2Node, shadow3Node, shadow4Node, shadow5Node,
                        shadow6Node, shadow7Node, shadow8Node, shadow9Node, shadowMainNode]

    return shadowNode


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

def createColorNormalsBorder(r, g, b):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions         colors   normals
    # Z+
        -0.5, -0.5,  0.5, r, g, b, 0,0,1,
         0.5, -0.5,  0.5, r, g, b, 0,0,1,
         0.4,  0.5,  0.5, r, g, b, 0,0,1,
        -0.4,  0.5,  0.5, r, g, b, 0,0,1,

    # Z-
        -0.5, -0.5, -0.5, r, g, b, 0,0,-1,
         0.5, -0.5, -0.5, r, g, b, 0,0,-1,
         0.4,  0.5, -0.5, r, g, b, 0,0,-1,
        -0.4,  0.5, -0.5, r, g, b, 0,0,-1,
        
    # X+
        0.5, -0.5, -0.5, r, g, b, 1,0,0,
        0.4,  0.5, -0.5, r, g, b, 1,0,0,
        0.4,  0.5,  0.5, r, g, b, 1,0,0,
        0.5, -0.5,  0.5, r, g, b, 1,0,0,
 
    # X-
        -0.5, -0.5, -0.5, r, g, b, -1,0,0,
        -0.4,  0.5, -0.5, r, g, b, -1,0,0,
        -0.4,  0.5,  0.5, r, g, b, -1,0,0,
        -0.5, -0.5,  0.5, r, g, b, -1,0,0,

    # Y+
        -0.4, 0.5, -0.5, r, g, b, 0,1,0,
         0.4, 0.5, -0.5, r, g, b, 0,1,0,
         0.4, 0.5,  0.5, r, g, b, 0,1,0,
        -0.4, 0.5,  0.5, r, g, b, 0,1,0,

    # Y-
        -0.5, -0.5, -0.5, r, g, b, 0,-1,0,
         0.5, -0.5, -0.5, r, g, b, 0,-1,0,
         0.5, -0.5,  0.5, r, g, b, 0,-1,0,
        -0.5, -0.5,  0.5, r, g, b, 0,-1,0
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


def createTable(pipeline):
    gpuGreenCube = createGPUShape(pipeline, bs.createColorNormalsCube(13/255, 145/255, 44/255))
    gpuBrownCube = createGPUShape(pipeline, bs.createColorNormalsCube(125/255, 58/255, 7/255))
    gpuBorder = createGPUShape(pipeline, createColorNormalsBorder(13/255, 145/255, 44/255))

    greenTableNode = sg.SceneGraphNode("Green Table")
    greenTableNode.transform = tr.matmul([tr.translate(0,0,-1.0),tr.scale(2.0, 1.0, 0.1)])
    greenTableNode.childs = [gpuGreenCube]
    
    sideTableNode1 = sg.SceneGraphNode("Side Table 1")
    sideTableNode1.transform = tr.matmul([tr.translate(0, 0.55, -1.0), tr.scale(2.0, 0.1, 0.2)])
    sideTableNode1.childs = [gpuBrownCube]
    sideTableNode2 = sg.SceneGraphNode("Side Table 2")
    sideTableNode2.transform = tr.matmul([tr.translate(1.0, 0, -1.0),tr.rotationZ(np.pi/2), tr.scale(1.2, 0.1, 0.2)])
    sideTableNode2.childs = [gpuBrownCube]
    sideTableNode3 = sg.SceneGraphNode("Side Table 3")
    sideTableNode3.transform = tr.matmul([tr.translate(0, -0.55, -1.0), tr.scale(2.0, 0.1, 0.2)])
    sideTableNode3.childs = [gpuBrownCube]
    sideTableNode4 = sg.SceneGraphNode("Side Table 4")
    sideTableNode4.transform = tr.matmul([tr.translate(-1.0, 0, -1.0),tr.rotationZ(np.pi/2), tr.scale(1.2, 0.1, 0.2)])
    sideTableNode4.childs = [gpuBrownCube]

    sideTableNode = sg.SceneGraphNode("SideTable")
    sideTableNode.childs = [sideTableNode1, sideTableNode2, sideTableNode3, sideTableNode4]

    border1Node = sg.SceneGraphNode("border1")
    border1Node.transform = tr.matmul([tr.translate(0.45, -0.47, -0.927) ,tr.scale(0.9, 0.07, 0.05)])
    border1Node.childs = [gpuBorder]

    border2Node = sg.SceneGraphNode("border2")
    border2Node.transform = tr.matmul([tr.translate(-0.45, -0.47, -0.927) ,tr.scale(0.9, 0.07, 0.05)])
    border2Node.childs = [gpuBorder]

    border3Node = sg.SceneGraphNode("border3")
    border3Node.transform = tr.matmul([tr.translate(0.45, 0.47, -0.927),tr.rotationZ(np.pi) ,tr.scale(0.9, 0.07, 0.05)])
    border3Node.childs = [gpuBorder]

    border4Node = sg.SceneGraphNode("border4")
    border4Node.transform = tr.matmul([tr.translate(-0.45, 0.47, -0.927),tr.rotationZ(np.pi) ,tr.scale(0.9, 0.07, 0.05)])
    border4Node.childs = [gpuBorder]

    border5Node = sg.SceneGraphNode("border5")
    border5Node.transform = tr.matmul([tr.translate(0.919, 0, -0.927),tr.rotationZ(np.pi/2) ,tr.scale(0.9, 0.07, 0.05)])
    border5Node.childs = [gpuBorder]

    border6Node = sg.SceneGraphNode("border6")
    border6Node.transform = tr.matmul([tr.translate(-0.919, 0, -0.927),tr.rotationZ(-np.pi/2) ,tr.scale(0.9, 0.07, 0.05)])
    border6Node.childs = [gpuBorder]

    bordersNode = sg.SceneGraphNode("borders")
    bordersNode.childs = [border1Node, border2Node, border3Node, border4Node, border5Node, border6Node]

    mainTableNode = sg.SceneGraphNode("Main Table")
    mainTableNode.childs = [greenTableNode, sideTableNode, bordersNode]

    return mainTableNode

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