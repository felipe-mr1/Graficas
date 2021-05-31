import openmesh as om
import numpy as np
import math
import random
import grafica.easy_shaders as es
import grafica.basic_shapes as bs
import grafica.transformations as tr
import grafica.scene_graph as sg
import glfw
from OpenGL.GL import *

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def create_quad():
    # Creamos una malla de triangulos
    mesh = om.TriMesh()

    #  2 ==== 1
    #  |\   0 |
    #  | \    |
    #  |   \  |
    #  |    \ |
    #  | 1   \|
    #  3 ==== 0

    # Agregamos algunos vertices a la malla
    vh0 = mesh.add_vertex([0.5, -0.5, 0])
    vh1 = mesh.add_vertex([0.5, 0.5, 0])
    vh2 = mesh.add_vertex([-0.5, 0.5, 0])
    vh3 = mesh.add_vertex([-0.5, -0.5, 0])

    # Agregamos algunas caras a la malla
    fh0 = mesh.add_face(vh0, vh1, vh2)
    fh1 = mesh.add_face(vh0, vh2, vh3)

    return mesh

def create_gaussiana(N, a):

    # Definimos la función de la gaussiana
    def gaussiana(x, y, a):
        return a * math.exp(-.5*x**2 + -.5*y**2)

    # Creamos arreglos entre -5 y 5, de tamaño N
    xs = np.linspace(-5, 5, N)
    ys = np.linspace(-5, 5, N)

    # Creamos una malla de triangulos
    gaussiana_mesh = om.TriMesh()

    # Generamos un vertice para cada x,y,z
    for i in range(len(xs)):
        for j in range(len(ys)):
            x = xs[i]
            y = ys[j]
            z = gaussiana(x, y, a)
            
            # Agregamos el vertice a la malla
            gaussiana_mesh.add_vertex([x, y, z])

    # Podemos calcular el indice de cada punto (i,j) de la siguiente manera
    index = lambda i, j: i*len(ys) + j 
    
    # Creamos caras para cada cuadrado de la malla
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):

            # Conseguimos los indices por cada cuadrado
            isw = index(i,j)
            ise = index(i+1,j)
            ine = index(i+1,j+1)
            inw = index(i,j+1)

            # Obtenemos los vertices, y agregamos las caras
            vertexs = list(gaussiana_mesh.vertices())

            gaussiana_mesh.add_face(vertexs[isw], vertexs[ise], vertexs[ine])
            gaussiana_mesh.add_face(vertexs[ine], vertexs[inw], vertexs[isw])

    return gaussiana_mesh

def get_vertexs_and_indexes(mesh):
    # Obtenemos las caras de la malla
    faces = mesh.faces()

    # Creamos una lista para los vertices e indices
    vertexs = []

    # Obtenemos los vertices y los recorremos
    for vertex in mesh.points():
        vertexs += vertex.tolist()
        # Agregamos un color al azar
        vertexs += [random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)]

    indexes = []

    for face in faces:
        # Obtenemos los vertices de la cara
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            # Obtenemos el numero de indice y lo agregamos a la lista
            indexes += [vertex.idx()]

    return vertexs, indexes

####################################################################################################
# Funciones para conseguir la isosuperficie
####################################################################################################

def get_isosurface_triangle(mesh, min_value, max_value):
    # Obtenemos las caras de la malla
    mesh_faces = mesh.faces()

    # Recorremos las caras
    for face in mesh_faces:
        # Si encontramos una que este en el rango buscado la devolvemos
        if face_in_range(mesh, face, min_value, max_value):
            return face
    
    # Si no encontramos cara, no devolvemos nada
    return

def face_in_range(mesh, face, min_value, max_value):
    # Obtenemos los vertices de la cara
    face_vertexes = list(mesh.fv(face))

    # Obtenemos las posiciones de los 3 vertices
    first_vertex = mesh.point(face_vertexes[0]).tolist()
    second_vertex = mesh.point(face_vertexes[1]).tolist()
    third_vertex = mesh.point(face_vertexes[2]).tolist()

    # Revisamos si alguno de los vertices esta en el rango buscado, devolvemos true si esta dentro del rango
    if (min_value <= first_vertex[2] <= max_value) or (min_value <= second_vertex[2] <= max_value) or (
            min_value <= third_vertex[2] <= max_value):
            return True
    
    return False

def get_in_range_faces(mesh, face, min_value, max_value, in_range_faces):
    # Si la cara no esta en el rango, o si ya pasamos por ella, terminamos de revisar
    # Darse cuenta que si la cara no esta en rango, entonces no seguiremos revisando las caras que siguen de aquella, ya que las caras de la isosuperficie estarán conectadas
    if not face_in_range(mesh, face, min_value, max_value) or face in in_range_faces:
        return in_range_faces

    # En otro caso agregamos la cara a una lista que contiene las caras que estan en rango
    in_range_faces += [face]

    # Obtenemos las caras adjacentes de la cara entregada
    adjacent_faces = mesh.ff(face)

    # Por cada cara adjacente recorremos recursivamente buscando las caras en rango
    # Darse cuenta que la linea 134 es para que no se quede infinitamente revisando todas las caras.
    for adjacent_face in adjacent_faces:
        in_range_faces = get_in_range_faces(mesh, adjacent_face, min_value, max_value, in_range_faces)

    # Devolvemos la lista de caras en rango
    return in_range_faces


def create_new_mesh(faces_list, old_mesh):
    # Creamos una malla nueva
    mesh = om.TriMesh()

    # Recorremos las caras
    for face in faces_list:
        # Obtenemos los vertices de la cara y sus posiciones
        vertexs = list(old_mesh.fv(face))
        vertex1 = list(old_mesh.point(vertexs[0]))
        vertex2 = list(old_mesh.point(vertexs[1]))
        vertex3 = list(old_mesh.point(vertexs[2]))

        # Añadimos los vertices a la malla nueva
        v1 = mesh.add_vertex(vertex1)
        v2 = mesh.add_vertex(vertex2)
        v3 = mesh.add_vertex(vertex3)

        # Añadimos la cara a la malla nueva
        mesh.add_face(v1, v2, v3)

    return mesh

def create_new_mesh_v2(faces_list, old_mesh):
    # Creamos una malla nueva
    mesh = om.TriMesh()
    vertexs_in_mesh = {}

    # Recorremos las caras
    for face in faces_list:
        # Obtenemos los vertices de la cara y sus posiciones
        vertexs = list(old_mesh.fv(face))
        vertex1 = list(old_mesh.point(vertexs[0]))
        vertex2 = list(old_mesh.point(vertexs[1]))
        vertex3 = list(old_mesh.point(vertexs[2]))

        # Añadimos los vertices a la malla nueva si es que no están, o sino obtenemos el vertice
        if str(vertex1) not in vertexs_in_mesh:
            v1 = mesh.add_vertex(vertex1)
            vertexs_in_mesh[str(vertex1)] = v1
        else:
            v1 = vertexs_in_mesh[str(vertex1)]

        if str(vertex2) not in vertexs_in_mesh:
            v2 = mesh.add_vertex(vertex2)
            vertexs_in_mesh[str(vertex2)] = v2
        else:
            v2 = vertexs_in_mesh[str(vertex2)]

        if str(vertex3) not in vertexs_in_mesh:
            v3 = mesh.add_vertex(vertex3)
            vertexs_in_mesh[str(vertex2)] = v3
        else:
            v3 = vertexs_in_mesh[str(vertex3)]

        # Añadimos la cara a la malla nueva
        mesh.add_face(v1, v2, v3)

    return mesh

def createColorNormalSphere(N, rojo, g, b):

    vertices = []
    indices = []
    dTheta = np.pi /N
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
                vertices += [v0[0], v0[1], v0[2], rojo, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], rojo, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], rojo, g, b, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], rojo, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], rojo, g, b, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], rojo, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], rojo, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], rojo, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], rojo, g, b, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], rojo, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)

def createBallNode(pipeline):
    ball = createGPUShape(pipeline, bs.createColorCube(0.1,0.1,0.1))

    ballNode = sg.SceneGraphNode("torus")
    ballNode.transform =tr.matmul([
        tr.translate(-0.00,0.00,-0.0),
        tr.scale(0.3,0.3,0.3)
    ])
    ballNode.childs = [ball]

    scaledBall = sg.SceneGraphNode("sc_sphere")
    scaledBall.transform = tr.scale(5, 5, 5)
    scaledBall.childs = [ballNode]

    return scaledBall

