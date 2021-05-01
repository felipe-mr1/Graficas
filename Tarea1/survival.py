# coding=utf-8
"""Textures and transformations in 2D"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path

from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
from PIL import Image

__author__ = "Daniel Calderon"
__license__ = "MIT"

###########################################################################
# Creamos nuestro vertex shader
class SimpleNewTextureTransformShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;
            uniform float texture_index;

            in vec2 position;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 0, 1.0f);

                if(position.x>0 && position.y>0){
                    outTexCoords = vec2(1, 0); 
                }
                else if(position.x<0 && position.y>0){
                    outTexCoords = vec2(0, 0);
                }
                else if(position.x>0 && position.y<0){
                    outTexCoords = vec2(1, 1);
                }
                else{
                    outTexCoords = vec2(0, 1);
                }
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 2d vertices => 2*4 = 8 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def createTextureQuad():

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions
        -0.5, -0.5,
         0.5, -0.5,
         0.5,  0.5,
        -0.5,  0.5,]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return bs.Shape(vertices, indices)

##################################################################################################

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
#####################################################################################################
        self.actual_rain = 1
        self.actual_sprite = 1
        self.direction = 1

#####################################################################################################


# global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

#####################################################################################################

    elif key == glfw.KEY_RIGHT:
        controller.actual_sprite = (controller.actual_sprite + 1)%10
        #controller.actual_rain = (controller.actual_rain + 1)%5
        controller.direction = 1
    
    elif key == glfw.KEY_LEFT:
        controller.actual_sprite = (controller.actual_sprite - 1)%10
        #controller.actual_rain = (controller.actual_rain + 1)%5
        controller.direction = -1

#####################################################################################################

    else:
        print('Unknown key')


if __name__ == "__main__":
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Boo!", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

#####################################################################################################

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = SimpleNewTextureTransformShaderProgram()

#####################################################################################################
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

######################################################################################################


    # Creating shapes on GPU memory

    #shapeKnight = createTextureQuad()

    #shapeRain = createTextureQuad()

    shapeZombie = createTextureQuad()

    shapeStudient = createTextureQuad()

    shapeStore = createTextureQuad()

    shapeHinata = createTextureQuad()

    #gpuKnight = GPUShape().initBuffers()
    #pipeline.setupVAO(gpuKnight)

    #gpuRain = GPUShape().initBuffers()
    #pipeline.setupVAO(gpuRain)

    gpuZombie = GPUShape().initBuffers()
    pipeline.setupVAO(gpuZombie)

    gpuStudient = GPUShape().initBuffers()
    pipeline.setupVAO(gpuStudient)

    gpuStore = GPUShape().initBuffers()
    pipeline.setupVAO(gpuStore)

    gpuHinata = GPUShape().initBuffers()
    pipeline.setupVAO(gpuHinata)

    # Definimos donde se encuentra la textura
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    texturesDirectory = os.path.join(thisFolderPath, "textures")
    zombiePath = os.path.join(texturesDirectory, "zombie.png")
    studientPath = os.path.join(texturesDirectory, "estudiante5.png")
    storePath = os.path.join(texturesDirectory, "tienda.png")
    hinataPath = os.path.join(texturesDirectory, "hinata2.png")
    #spritePath = os.path.join(spritesDirectory, "sprites.png")
    #rainPath = os.path.join(spritesDirectory, "pngegg.png")

    """
    gpuKnight.texture = es.textureSimpleSetup(
        spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    gpuRain.texture = es.textureSimpleSetup(
        rainPath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    """
    gpuZombie.texture = es.textureSimpleSetup(
        zombiePath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    
    gpuStudient.texture = es.textureSimpleSetup(
        studientPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    
    gpuStore.texture = es.textureSimpleSetup(
        storePath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    gpuHinata.texture = es.textureSimpleSetup(
        hinataPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    

    #gpuKnight.fillBuffers(shapeKnight.vertices, shapeKnight.indices, GL_STATIC_DRAW)

    #gpuRain.fillBuffers(shapeRain.vertices, shapeRain.indices, GL_STATIC_DRAW)

    gpuZombie.fillBuffers(shapeZombie.vertices, shapeZombie.indices, GL_STATIC_DRAW)

    gpuStore.fillBuffers(shapeStore.vertices, shapeStore.indices, GL_STATIC_DRAW)
    
    gpuStudient.fillBuffers(shapeStudient.vertices, shapeStudient.indices, GL_STATIC_DRAW)

    gpuHinata.fillBuffers(shapeHinata.vertices, shapeHinata.indices, GL_STATIC_DRAW)

#######################################################################################################    

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        #controller.actual_rain = (controller.actual_rain + 1)%10  # continuous rain

        time = glfw.get_time()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the shapes

##############################################################################################################

        

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.uniformScale(0.5),
            tr.translate(0.0,-0.5,0.0)
        ]))

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "texture_index"), controller.actual_rain)

        pipeline.drawCall(gpuStore)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.uniformScale(0.5),
            tr.translate(0.5,0,0)
        ]))

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "texture_index"), controller.actual_sprite)

        pipeline.drawCall(gpuZombie)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.uniformScale(0.5),
            tr.translate(-0.5,0,0)
        ]))

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "texture_index"), controller.actual_sprite)
        
        pipeline.drawCall(gpuStudient)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.uniformScale(0.5),
            tr.translate(0,0.5,0)
        ]))

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "texture_index"), controller.actual_sprite)
        
        pipeline.drawCall(gpuHinata)

        """

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.uniformScale(0.5),
            tr.translate(-0.5,0.0,0.0)
        ]))

        pipeline.drawCall(gpuStudient)
        """

        
##############################################################################################################

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    #gpuKnight.clear()
    #gpuRain.clear()
    gpuZombie.clear()
    gpuStudient.clear()
    gpuStore.clear()

    glfw.terminate()
