"""Funciones para crear distintas figuras y escenas en 3D """

import numpy as np
import math
from OpenGL.GL import *
from numpy.core.numeric import indices
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg

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

def createBodyScene(pipeline):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.7, 0.7, 0.7))
    gpuSphere = createGPUShape(pipeline, createColorNormalSphere(50, 0.7,0.7,0.7))

    headNode = sg.SceneGraphNode("Head")
    headNode.transform = tr.matmul([tr.translate(0,0,0.2),tr.uniformScale(0.5)])
    headNode.childs = [gpuSphere]

    headRotationNode = sg.SceneGraphNode("headRotation")
    headRotationNode.childs=[headNode]

    centerBody = sg.SceneGraphNode("centerBody")
    centerBody.transform = tr.matmul([tr.translate(0,0,-0.45),tr.scale(0.3,0.3,1.0)])
    centerBody.childs = [gpuGrayCube]

    centerBodyRot = sg.SceneGraphNode("centerBodyRotation")
    centerBodyRot.childs = [centerBody]

    wholeBody = sg.SceneGraphNode("wholeBody")
    wholeBody.childs = [centerBodyRot, headRotationNode]

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

def createColorNormalSphere(N, r, g, b):

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
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)

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