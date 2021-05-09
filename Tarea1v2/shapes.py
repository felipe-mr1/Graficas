"""Funciones para crear distintas figuras y escenas """

import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.ex_curves as cv
import grafica.scene_graph as sg

def createGPUShape(shape, pipeline, mode = GL_STATIC_DRAW):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, mode) # mode = GL_STATIC_DRAW
    return gpuShape

def createTextureGPUShape(shape, pipeline, path, drawMode, mipmap, mode = GL_CLAMP_TO_EDGE): #mipmap
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, drawMode)
    if mipmap:
        gpuShape.texture = es.textureSimpleSetup(
            path, mode, mode, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        gpuShape.texture = es.textureSimpleSetup(
            path, mode, mode, GL_NEAREST, GL_NEAREST)
    return gpuShape


def createCrossShape():
    vertices = [
        -0.2, 0.6, 0.0, 0.0, 1.0, 0.0,
        
        -0.6, 0.2, 0.0, 0.0, 1.0, 0.0,
        -0.6, -0.2, 0.0, 0.0, 1.0, 0.0,
        
        -0.2, -0.6, 0.0, 0.0, 1.0, 0.0,
        0.2, -0.6, 0.0, 0.0, 1.0, 0.0,
        
        0.6, -0.2, 0.0, 0.0, 1.0, 0.0,
        0.6, 0.2, 0.0, 0.0, 1.0, 0.0,
        
        0.2, 0.6, 0.0, 0.0, 1.0, 0.0
    ]

    indices = [
        0,3,4,
        4,7,0,

        1,2,5,
        5,6,1
    ]
    return bs.Shape(vertices,indices)

def createPowerUp():
    vertices = [
        0.0, 0.5, 0.0, 1.0, 1.0, 1.0,
        -0.3, -0.1, 0.0, 0.0, 0.0, 1.0,
        0.12, -0.1, 0.0, 0.0, 0.0, 1.0,
        -0.1, -0.5, 0.0, 0.0, 0.0, 1.0,
        0.4, 0.1, 0.0, 0.0, 0.0, 1.0, 
        -0.07, 0.1, 0.0, 1.0, 1.0, 1.0
    ]

    indices = [
        0,1,5,
        5,1,4,
        4,1,2,
        2,3,4
    ]

    return bs.Shape(vertices, indices)


def createTextureScene(tex_pipeline):
    gpuTree = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "sprites/tree2.png", GL_DYNAMIC_DRAW, True)
    gpuSidewalk = createTextureGPUShape(bs.createTextureQuad(1.0,3.0), tex_pipeline, "sprites/sidewalk.jpg",GL_STATIC_DRAW, True, GL_REPEAT)
    gpuTreeRepeat = createTextureGPUShape(bs.createTextureQuad(1, 4), tex_pipeline, "sprites/tree2.png",GL_DYNAMIC_DRAW, True, GL_REPEAT)
    gpuGate = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/gate4.png", GL_STATIC_DRAW, False)
    gpuStore = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "sprites/tienda.png",GL_STATIC_DRAW, False)

    gateNode = sg.SceneGraphNode("gate")
    gateNode.transform = tr.matmul([tr.translate(0.7, 0.0, 0.0),tr.uniformScale(0.25)])
    gateNode.childs = [gpuGate]

    storeNode = sg.SceneGraphNode("store")
    storeNode.transform = tr.matmul([tr.translate(-0.8, 0.75, 0),tr.rotationZ(1.57), tr.scale(0.5,0.35,1)])
    storeNode.childs = [gpuStore]

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
    treeNode = sg.SceneGraphNode("tree")
    treeNode.transform = tr.scale(0.3, 0.3, 1)
    treeNode.childs = [gpuTree]
    # Nodo del shearing
    shearingTreeNode = sg.SceneGraphNode("shearing")
    shearingTreeNode.childs= [treeNode]
    # Nodo del primer arbol
    tree1Node = sg.SceneGraphNode("tree2")
    tree1Node.transform = tr.translate(0.0, -0.8, 0)
    tree1Node.childs = [shearingTreeNode]
    # Nodo del segundo arbol
    tree2Node = sg.SceneGraphNode("tree2")
    tree2Node.transform = tr.translate(0.0, -0.3, 0)
    tree2Node.childs = [shearingTreeNode]
    # Nodo del tercer arbol
    tree3Node = sg.SceneGraphNode("tree3")
    tree3Node.transform = tr.translate(0.0, 0.3, 0)
    tree3Node.childs = [shearingTreeNode]
    # Nodo del cuarto arbol
    tree4Node = sg.SceneGraphNode("tree4")
    tree4Node.transform = tr.translate(0.0, 0.8, 0)
    tree4Node.childs = [shearingTreeNode]
    # Nodo del conjunto de arboles
    setOfTreesNode = sg.SceneGraphNode("set of trees")
    setOfTreesNode.childs = [tree1Node, tree2Node, tree3Node, tree4Node]
    # Nodo de los arboles de la izquirda
    leftTreeNode = sg.SceneGraphNode("leftTrees")
    leftTreeNode.transform = tr.translate(-0.75,0.0,1.0)
    leftTreeNode.childs = [setOfTreesNode]
    # Nodo de los arboles de la derecha
    rightTreeNode = sg.SceneGraphNode("rightTrees")
    rightTreeNode.transform = tr.translate(0.75,0.0,1.0)
    rightTreeNode.childs = [setOfTreesNode]
    # Nodo del bosque
    forestNode = sg.SceneGraphNode("trees")
    forestNode.childs = [leftTreeNode, rightTreeNode]
    # Escena
    sceneNode = sg.SceneGraphNode("world")
    sceneNode.childs = [forestNode, sidewalkNode, storeNode, gateNode]

    return sceneNode

def createScene(pipeline):
    # Funcion que crea la escena de la pregunta 2

    # Se crean las shapes en GPU
    gpuGrayQuad = createGPUShape(bs.createColorQuad(0.5, 0.5, 0.5), pipeline) # Shape del quad gris
    gpuWhiteQuad = createGPUShape(bs.createColorQuad(1,1,1), pipeline) # Shape del quad blanco
    gpuGreenQuad =  createGPUShape(bs.createColorQuad(68/255, 168/255, 50/255), pipeline) # Shape del quad verde

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

    

    # Nodo de la calle completa
    streetNode = sg.SceneGraphNode("street")
    streetNode.childs = [highwayNode, line1Node, line2Node]

    # Nodo del background con todos los nodos anteriores
    backGroundNode = sg.SceneGraphNode("background")
    backGroundNode.childs = [grassNode, highwayNode, streetNode] # sunNode pasa abajo # tengo que quitar el highway

    # Nodo padre de la escena
    sceneNode = sg.SceneGraphNode("world")
    sceneNode.childs = [backGroundNode]

    return sceneNode



