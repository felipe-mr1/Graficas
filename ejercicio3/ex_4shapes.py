# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.gpu_shape as gs
import grafica.transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A class to store the application control
class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')


def drawCall(shaderProgram, shape, mode= GL_TRIANGLES):

    # Binding the proper buffers
    glBindVertexArray(shape.vao)
    glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

    # Describing how the data is stored in the VBO
    position = glGetAttribLocation(shaderProgram, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
    
    color = glGetAttribLocation(shaderProgram, "color")
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    # This line tells the active shader program to render the active element buffer with the given size
    glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


def createTriangle():

    # Here the new shape will be stored
    gpuShape = gs.GPUShape()

    # Defining the location and colors of each vertex  of the shape
    vertexData = np.array(
    #     positions       colors
        [-0.7, -0.7, 0.0, 1.0, 0.0, 0.0,
          0.7, -0.7, 0.0, 0.0, 1.0, 0.0,
          0.0,  0.7, 0.0, 0.0, 0.0, 1.0],
          dtype = np.float32) # It is important to use 32 bits data

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = np.array(
        [0, 1, 2], dtype= np.uint32)
        
    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape


def createQuad(aName):

    r=0.0
    b=0.0
    g=0.0
    if aName == "earth":
        r=0.0
        g=0.0
        b=1.0
    if aName == "sun":
        r=0.98
        g=0.77
    if aName == "moon":
        r=0.47
        b=0.47
        g=0.47
    if aName== "orbit":
        r=1.0
        g=1.0
        b=1.0

    # Here the new shape will be stored
    gpuShape = gs.GPUShape()

    # Defining locations and colors for each vertex of the shape
    
    vertexData = np.array([
    #   positions        colors
        -0.5, -0.5, 0.0,  r, g, b,
         0.5, -0.5, 0.0,  r, g, b,
         0.5,  0.5, 0.0,  r, g, b,
        -0.5,  0.5, 0.0,  r, g, b
    # It is important to use 32 bits data
        ], dtype = np.float32)

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = np.array(
        [0, 1, 2,
         2, 3, 0], dtype= np.uint32)

    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    # Vertex data must be attached to a Vertex Buffer Object (VBO)
    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    # Connections among vertices are stored in the Elements Buffer Object (EBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape

def createOrbit(N):

    # Here the new shape will be stored
    gpuShape = gs.GPUShape()

    # First vertex at the center, white color
    vertices = []
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * np.cos(theta), 0.5 * np.sin(theta), 0,

            # white color
                  1.0,       1.0, 1.0]

        # A triangle is created using the center, this and the next vertex
        if i < N-1:
            indices += [ i, i+1] # correcto
        if i == N-1:
            indices += [ i, 0]

    # The final triangle connects back to the second vertex
    #indices += [ N, 0]

    vertices = np.array(vertices, dtype =np.float32)
    indices = np.array(indices, dtype= np.uint32)
        
    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * SIZE_IN_BYTES, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape

def createCircle(N, aName):

    r=0.0
    b=0.0
    g=0.0
    if aName == "earth":
        r=0.0
        g=0.0
        b=1.0
    if aName == "sun":
        r=0.98
        g=0.77
    if aName == "moon":
        r=0.47
        b=0.47
        g=0.47

    # Here the new shape will be stored
    gpuShape = gs.GPUShape()

    # First vertex at the center, white color
    vertices = [0, 0, 0, r, g, b]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * np.cos(theta), 0.5 * np.sin(theta), 0,

            # color generates depending on the name
                  r,       g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    vertices = np.array(vertices, dtype =np.float32)
    indices = np.array(indices, dtype= np.uint32)
        
    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * SIZE_IN_BYTES, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape
    

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Displaying multiple shapes - Modern OpenGL", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Defining shaders for our pipeline
    vertex_shader = """
    #version 130
    in vec3 position;
    in vec3 color;

    out vec3 fragColor;

    uniform mat4 transform;

    void main()
    {
        fragColor = color;
        gl_Position = transform * vec4(position, 1.0f);
    }
    """

    fragment_shader = """
    #version 130

    in vec3 fragColor;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(fragColor, 1.0f);
    }
    """

    # Assembling the shader program (pipeline) with both shaders
    shaderProgram = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    
    # Telling OpenGL to use our shader program
    glUseProgram(shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Creating shapes on GPU memory
    gpuEarth = createCircle(20, "earth")
    gpuMoon = createCircle(20, "moon")
    gpuSun = createCircle(20,"sun")
    gpuOrbit = createOrbit(40)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Using the time as the theta parameter
        theta = glfw.get_time()

        
        # Earth Orbit
        planetOrbitTransform = tr.matmul([
            tr.translate(0.0, 0.0, 0.0),
            tr.uniformScale(1.4)
        ])

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, planetOrbitTransform)

        drawCall(shaderProgram, gpuOrbit, GL_POINTS)
        

        # Sun
        planetTransform = tr.matmul([
            tr.rotationZ(theta),
            tr.uniformScale(0.3)
        ])

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, planetTransform)

        drawCall(shaderProgram, gpuSun)

        # Sun contorno
        sunEdge = tr.matmul([
            tr.uniformScale(0.3)
        ])

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, sunEdge)

        drawCall(shaderProgram, gpuOrbit, GL_LINES)

        # Moon Orbit
        moonOrbitTransform= tr.matmul([
            tr.rotationZ( theta),
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.29),
            tr.rotationZ(-theta)
            
        ])

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, moonOrbitTransform)

        drawCall(shaderProgram, gpuOrbit, GL_POINTS)

        # Moon
        moonTransform = tr.matmul([
            tr.rotationZ( theta),
            tr.translate(0.5+0.1*np.cos(theta) - 0.1*np.sin(theta) , 0.5+ 0.1*np.cos(theta) + 0.1*np.sin(theta), 0),
            tr.uniformScale(0.05)
        ])

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, moonTransform)

        drawCall(shaderProgram, gpuMoon)

        # Moon edge
        moonEdgeTransformation = tr.matmul([
            tr.rotationZ( theta),
            tr.translate(0.5+0.1*np.cos(theta) - 0.1*np.sin(theta) , 0.5+ 0.1*np.cos(theta) + 0.1*np.sin(theta), 0),
            tr.uniformScale(0.05)
        ])

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, moonEdgeTransformation)

        drawCall(shaderProgram, gpuOrbit, GL_LINES)


        

        # Earth
        earthTransform = tr.matmul([
            tr.rotationZ( theta),
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.1),
            tr.rotationZ(theta)
        ])


        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, earthTransform)

        # drawing function
        drawCall(shaderProgram, gpuEarth)

        # Earth Edge
        earthEdgeTransformation = tr.matmul([
            tr.rotationZ(theta),
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.1)
        ])

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, earthEdgeTransformation)

        # drawing function
        drawCall(shaderProgram, gpuOrbit, GL_LINES)

        """
        # Another instance of the triangle
        triangleTransform2 = tr.matmul([
            tr.translate(-0.5, 0.5, 0),
            tr.scale(
                0.5 + 0.2 * np.cos(1.5 * theta),
                0.5 + 0.2 * np.sin(2 * theta),
                0)
        ])
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, triangleTransform2)
        drawCall(shaderProgram, gpuTriangle)

        # Quad
        quadTransform = tr.matmul([
            tr.translate(-0.5, -0.5, 0),
            tr.rotationZ(-theta),
            tr.uniformScale(0.7)
        ])
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, quadTransform)
        drawCall(shaderProgram, gpuQuad)

        # Another instance of the Quad
        quadTransform2 = tr.matmul([
            tr.translate(0.5, -0.5, 0),
            tr.shearing(0.3 * np.cos(theta), 0, 0, 0, 0, 0),
            tr.uniformScale(0.7)
        ])
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, quadTransform2)
        drawCall(shaderProgram, gpuQuad)
        """

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuEarth.clear()
    #gpuQuad.clear()
    gpuMoon.clear()
    #gpuPlanet.clear()
    gpuSun.clear()
    
    glfw.terminate()