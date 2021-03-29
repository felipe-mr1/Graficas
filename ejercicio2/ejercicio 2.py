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
                vec3 newPos = vec3(position[0]/-1, position[1]/-1, position[2]/-1);
                gl_Position = vec4(newPos, 1.0f);
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
                if(newColor.r > newColor.g && newColor.r > newColor.b)
                {
                    vec3 finalColor = vec3(newColor.r + (0.9-newColor.r), newColor.g+ 0.0, newColor.b+0.0);
                    outColor = vec4(finalColor, 1.0f);
                }
                if(newColor.g > newColor.r && newColor.g > newColor.b)
                {
                    vec3 finalColor = vec3( newColor.r+ 0.0,newColor.g + 0.4, newColor.b+0.0);
                    outColor = vec4(finalColor, 1.0f);
                }
                else
                {
                    vec3 finalColor = vec3( newColor.r+ 0.0, newColor.g+0.0,newColor.b + (0.9-newColor.b));
                    outColor = vec4(finalColor, 1.0f);
                }
                
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
        -1.0, y0, 0.0,  0.0, 0.0, 0.36,
         1.0, y0, 0.0,  0.0, 0.0, 0.36,
         1.0, y1, 0.0,  0.0, 0.36, 0.5,
        -1.0, y1, 0.0,  0.0, 0.36, 0.5]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_terrain(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  66/255, 92/255, 11/255,
         1.0, y0, 0.0,  66/255, 92/255, 11/255,
         1.0, y1, 0.0,  88/255, 122/255, 15/255,
        -1.0, y1, 0.0,  88/255, 122/255, 15/255]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

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
        0.5, 0.15, 0, 117/255, 117/255, 117/255,
        0.65, 0.15, 0, 117/255, 117/255, 117/255, # triangulo vertical 1
        0.65, 1, 0, 117/255, 117/255, 117/255,

        0.65, 1, 0, 117/255, 117/255, 117/255,
        0.5, 1, 0, 117/255, 117/255, 117/255, # triangulo vertical 2
        0.5, 0.15, 0, 117/255, 117/255, 117/255,

        0.25, 0.6, 0, 117/255, 117/255, 117/255,
        0.25, 0.75, 0, 117/255, 117/255, 117/255,
        0.9, 0.75, 0, 117/255, 117/255, 117/255,

        0.9, 0.75, 0, 117/255, 117/255, 117/255,
        0.9, 0.6, 0, 117/255, 117/255, 117/255,
        0.25, 0.6, 0, 117/255, 117/255, 117/255
    ]
    indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    return Shape(vertices, indices)

def create_star():
    vertices=[
        -0.25-0.7, -0.75-0.13, 0, 0, 0, 1,
        0.25-0.7, -0.75-0.13, 0, 0, 0, 1,
        0-0.7, -0.32-0.13, 0, 0, 0, 1,

        -0.25-0.7, -0.53+ 0.09-0.13, 0, 0, 0, 1,
        0.25-0.7, -0.53+ 0.09-0.13, 0, 0, 0, 1,
        0-0.7, -0.96+ 0.09-0.13, 0, 0, 0, 1
    ]
    indices = [0,1,2,3,4,5]
    return Shape(vertices, indices)

def create_forest():
    vertices=[
        -0.7, -0.4, 0, 6/255, 74/255, 6/255,
        -0.64, -0.4, 0, 6/255, 74/255, 6/255,
        -0.67, -0.3, 0, 6/255, 74/255, 6/255,

        0.7, -0.4, 0, 6/255, 74/255, 6/255,
        0.64, -0.4, 0, 6/255, 74/255, 6/255,
        0.67, -0.3, 0, 6/255, 74/255, 6/255,

        0, -0.3, 0, 6/255, 74/255, 6/255,
        0.06, -0.3, 0, 6/255, 74/255, 6/255,
        0.03, -0.2, 0, 6/255, 74/255, 6/255,

        0, -0.6, 0, 6/255, 74/255, 6/255,
        0.06, -0.6, 0, 6/255, 74/255, 6/255,
        0.03, -0.5, 0, 6/255, 74/255, 6/255,
    ]
    indices = [0,1,2,3,4,5,6,7,8,9,10,11]
    return Shape(vertices, indices)

def create_lake():
    vertices=[
        -0.6, -0.35, 0, 54/255, 112/255, 113/255,
        0.6, -0.35, 0, 54/255, 112/255, 113/255,
        0.6, -0.45, 0, 54/255, 112/255, 113/255,

        0.6, -0.45, 0, 54/255, 112/255, 113/255,
        -0.6, -0.45, 0, 54/255, 112/255, 113/255,
        -0.6, -0.35, 0, 54/255, 112/255, 113/255,
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

    terrain_shape = create_terrain(y0=-1.0, y1=-0.2)
    gpu_terrain = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_terrain)
    greenPipeline.setupVAO(gpu_terrain)
    sunsetPipeline.setupVAO(gpu_terrain)
    gpu_terrain.fillBuffers(terrain_shape.vertices, terrain_shape.indices, GL_STATIC_DRAW)

    

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

    forest_shape = create_forest()
    gpu_forest = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_forest)
    greenPipeline.setupVAO(gpu_forest)
    sunsetPipeline.setupVAO(gpu_forest)
    gpu_forest.fillBuffers(forest_shape.vertices, forest_shape.indices, GL_STATIC_DRAW)

    lake_shape = create_lake()
    gpu_lake = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_lake)
    greenPipeline.setupVAO(gpu_lake)
    sunsetPipeline.setupVAO(gpu_lake)
    gpu_lake.fillBuffers(lake_shape.vertices, lake_shape.indices, GL_STATIC_DRAW)


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
            greenPipeline.drawCall(gpu_terrain)
            
            greenPipeline.drawCall(gpu_volcano)
            greenPipeline.drawCall(gpu_moon)
            greenPipeline.drawCall(gpu_cross)
            greenPipeline.drawCall(gpu_star)
            greenPipeline.drawCall(gpu_forest)
            greenPipeline.drawCall(gpu_lake)
        elif (controller.effect2):
            glUseProgram(sunsetPipeline.shaderProgram)
            sunsetPipeline.drawCall(gpu_sky)
            sunsetPipeline.drawCall(gpu_terrain)
            
            sunsetPipeline.drawCall(gpu_volcano)
            sunsetPipeline.drawCall(gpu_moon)
            sunsetPipeline.drawCall(gpu_cross)
            sunsetPipeline.drawCall(gpu_star)
            sunsetPipeline.drawCall(gpu_forest)
            sunsetPipeline.drawCall(gpu_lake)
        else:
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_terrain)
            
            simplePipeline.drawCall(gpu_volcano)
            simplePipeline.drawCall(gpu_moon)
            simplePipeline.drawCall(gpu_cross)
            simplePipeline.drawCall(gpu_star)
            simplePipeline.drawCall(gpu_forest)
            simplePipeline.drawCall(gpu_lake)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_terrain.clear()
    
    gpu_volcano.clear()
    gpu_moon.clear()
    gpu_cross.clear()
    gpu_star.clear()
    gpu_forest.clear()
    gpu_lake.clear()

    glfw.terminate()