"""P5) [Efectos con Shaders] Realice un par de shaders, donde el primero solo dibuje los píxeles con un tono verde
 y el segundo represente un modo atardecer. Además agregue la funcionalidad de que se puedan alternar entre los shaders
apretando teclas. Con [Q] activa el primer efecto, y con [W] activa el segundo ejemplo"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from gpu_shape import GPUShape, SIZE_IN_BYTES

# A class to store the application control
class Controller:
    fillPolygon = True
    effect1 = False
    effect2 = False


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

    elif key == glfw.KEY_Q:
        controller.effect1 = not controller.effect1

    elif key == glfw.KEY_W:
        controller.effect2 = not controller.effect2

    else:
        print('Unknown key')
    
# A simple class container to store vertices and indices that define a shape
class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

class SimpleShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                outColor = vec4(newColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class GreenShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                float grayColor = (newColor.r + newColor.g + newColor.b) / 3.0;
                vec3 finalColor = newColor;
                if (newColor.g < newColor.r +0.1|| newColor.g < newColor.b +0.1)
                {
                    finalColor = vec3(grayColor, grayColor, grayColor);
                }
                outColor = vec4(finalColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class SunsetShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {   
                vec3 finalColor = vec3((newColor.r + 0.4) , newColor.g + 0.2, newColor.b * 0.1 );
                outColor = vec4(finalColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def create_sky(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.0, 1.0, 1.0,
         1.0, y0, 0.0,  0.0, 1.0, 1.0,
         1.0, y1, 0.0,  0.8, 1.0, 1.0,
        -1.0, y1, 0.0,  0.8, 1.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_ocean(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.0, 0.0, 0.5,
         1.0, y0, 0.0,  0.0, 0.0, 0.5,
         1.0, y1, 0.0,  0.2, 0.4, 1.0,
        -1.0, y1, 0.0,  0.2, 0.4, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_island(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions                           colors
         x0,         y0,               0.0,  0.63, 0.25, 0.0,
         x0 + width/2,  y0 - height,      0.0,  0.63, 0.25, 0.0,
         x0 + width/2,  y0 - height *0.4, 0.0,  0.63, 0.25, 0.0,

         x0 + width/2,  y0 - height,      0.0,  0.9, 0.49, 0.13,
         x0 + width, y0,               0.0,  0.9, 0.49, 0.13,
         x0 + width/2,  y0 - height *0.4, 0.0,  0.9, 0.49, 0.13,

         x0,         y0,               0.0,  0.0, 0.7, 0.0,
         x0 + width/2,  y0 - height *0.4, 0.0,  0.1, 1.0, 0.0,
         x0 + width, y0,               0.0,  0.0, 0.7, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices =  [0, 1, 2,
                3, 4, 5,
                6, 7, 8]

    return Shape(vertices, indices)

def create_volcano(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
         x0, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.8, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.4, y0 + height, 0.0,  0.6, 0.31, 0.17,

         x0 + width*0.2, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.6, y0 + height, 0.0, 0.6, 0.31, 0.17]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                3, 4, 5]

    return Shape(vertices, indices)

def create_moon_and_star():
    vertices=[
        -1.0, 0.5, 0, 1, 0, 0,
        -0.75, 0.5, 0, 1, 0, 0, # luna1
        -0.5, 0, 0, 1, 0, 0,

        -1.0, 0.5, 0, 1, 0, 0,
        -0.75, 0.5, 0, 1, 0, 0, # luna2
        -0.5, 1, 0, 1, 0 , 0,
        
        -0.35, 0.5, 0, 1, 0, 0,
        -0.15, 0.5, 0, 1, 0, 0, # triangulo apuntando a la izq
        -0.15, 0.3, 0, 1, 0, 0,

        -0.05, 0.5, 0, 1, 0, 0,
        -0.25, 0.5, 0, 1, 0, 0, # triangulo apuntando a la der
        -0.25, 0.3, 0, 1, 0, 0,

        -0.25, 0.5, 0, 1, 0, 0,
        -0.15, 0.5, 0, 1, 0, 0, # triangulo sup
        -0.2, 0.6, 0, 1, 0, 0
    ]
    indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    return Shape(vertices, indices)

def create_cross():
    vertices=[
        0.5, 0.15, 0, 0, 1, 0,
        0.65, 0.15, 0, 0, 1, 0, # triangulo vertical 1
        0.65, 1, 0, 0, 1, 0,

        0.65, 1, 0, 0, 1, 0,
        0.5, 1, 0, 0, 1, 0, # triangulo vertical 2
        0.5, 0.15, 0, 0, 1, 0,

        0.25, 0.6, 0, 0, 1, 0,
        0.25, 0.75, 0, 0, 1, 0,
        0.9, 0.75, 0, 0, 1, 0,

        0.9, 0.75, 0, 0, 1, 0,
        0.9, 0.6, 0, 0, 1, 0,
        0.25, 0.6, 0, 0, 1, 0
    ]
    indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    return Shape(vertices, indices)

def create_star():
    vertices=[
        -0.25, -0.75, 0, 0, 0, 1,
        0.25, -0.75, 0, 0, 0, 1,
        0, -0.32, 0, 0, 0, 1,

        -0.25, -0.53+ 0.09, 0, 0, 0, 1,
        0.25, -0.53+ 0.09, 0, 0, 0, 1,
        0, -0.96+ 0.09, 0, 0, 0, 1
    ]
    indices = [0,1,2,3,4,5]
    return Shape(vertices, indices)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800

    window = glfw.create_window(width, height, "P5: Efectos con shaders", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    simplePipeline = SimpleShaderProgram()
    greenPipeline = GreenShaderProgram()
    sunsetPipeline = SunsetShaderProgram()

    # Creating shapes on GPU memory
    sky_shape = create_sky(y0=-0.2, y1=1.0)
    gpu_sky = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_sky)
    greenPipeline.setupVAO(gpu_sky)
    sunsetPipeline.setupVAO(gpu_sky)
    gpu_sky.fillBuffers(sky_shape.vertices, sky_shape.indices, GL_STATIC_DRAW)

    ocean_shape = create_ocean(y0=-1.0, y1=-0.2)
    gpu_ocean = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_ocean)
    greenPipeline.setupVAO(gpu_ocean)
    sunsetPipeline.setupVAO(gpu_ocean)
    gpu_ocean.fillBuffers(ocean_shape.vertices, ocean_shape.indices, GL_STATIC_DRAW)

    island_shape = create_island(x0=-0.8, y0=-0.2, width=1.6, height=0.4)
    gpu_island = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_island)
    greenPipeline.setupVAO(gpu_island)
    sunsetPipeline.setupVAO(gpu_island)
    gpu_island.fillBuffers(island_shape.vertices, island_shape.indices, GL_STATIC_DRAW)

    volcano_shape = create_volcano(x0=-0.3, y0=-0.22, width=0.6, height=0.4)
    gpu_volcano = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_volcano)
    greenPipeline.setupVAO(gpu_volcano)
    sunsetPipeline.setupVAO(gpu_volcano)
    gpu_volcano.fillBuffers(volcano_shape.vertices, volcano_shape.indices, GL_STATIC_DRAW)

    moon_and_star_shape = create_moon_and_star()
    gpu_moon = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_moon)
    greenPipeline.setupVAO(gpu_moon)
    sunsetPipeline.setupVAO(gpu_moon)
    gpu_moon.fillBuffers(moon_and_star_shape.vertices, moon_and_star_shape.indices, GL_STATIC_DRAW)

    cross_shape = create_cross()
    gpu_cross = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_cross)
    greenPipeline.setupVAO(gpu_cross)
    sunsetPipeline.setupVAO(gpu_cross)
    gpu_cross.fillBuffers(cross_shape.vertices, cross_shape.indices, GL_STATIC_DRAW)

    star_shape = create_star()
    gpu_star = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_star)
    greenPipeline.setupVAO(gpu_star)
    sunsetPipeline.setupVAO(gpu_star)
    gpu_star.fillBuffers(star_shape.vertices, star_shape.indices, GL_STATIC_DRAW)


    # Setting up the clear screen color
    glClearColor(0.2, 0.2, 0.2, 1.0)

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

        if (controller.effect1):
            glUseProgram(greenPipeline.shaderProgram)
            greenPipeline.drawCall(gpu_sky)
            greenPipeline.drawCall(gpu_ocean)
            greenPipeline.drawCall(gpu_island)
            greenPipeline.drawCall(gpu_volcano)
            greenPipeline.drawCall(gpu_moon)
            greenPipeline.drawCall(gpu_cross)
            greenPipeline.drawCall(gpu_star)
        elif (controller.effect2):
            glUseProgram(sunsetPipeline.shaderProgram)
            sunsetPipeline.drawCall(gpu_sky)
            sunsetPipeline.drawCall(gpu_ocean)
            sunsetPipeline.drawCall(gpu_island)
            sunsetPipeline.drawCall(gpu_volcano)
            sunsetPipeline.drawCall(gpu_moon)
            sunsetPipeline.drawCall(gpu_cross)
            sunsetPipeline.drawCall(gpu_star)
        else:
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_ocean)
            simplePipeline.drawCall(gpu_island)
            simplePipeline.drawCall(gpu_volcano)
            simplePipeline.drawCall(gpu_moon)
            simplePipeline.drawCall(gpu_cross)
            simplePipeline.drawCall(gpu_star)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_ocean.clear()
    gpu_island.clear()
    gpu_volcano.clear()
    gpu_moon.clear()
    gpu_cross.clear()
    gpu_star.clear()

    glfw.terminate()