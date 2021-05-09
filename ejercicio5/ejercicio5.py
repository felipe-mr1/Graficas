""" P3 [Drive simulator] """

import glfw

import OpenGL.GL.shaders

import numpy as np
import random

import grafica.basic_shapes as bs

import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm

import grafica.scene_graph as sg

from shapes import *

from model import *



# We will use 32 bits data, so an integer has 4 bytes

# 1 byte = 8 bits

SIZE_IN_BYTES = 4



# Clase controlador con variables para manejar el estado de ciertos botones

class Controller:

    def __init__(self):

        self.fillPolygon = True

        self.is_w_pressed = False

        self.is_s_pressed = False

        self.is_a_pressed = False

        self.is_d_pressed = False



# we will use the global controller as communication with the callback function

controller = Controller()


# This function will be executed whenever a key is pressed or released

def on_key(window, key, scancode, action, mods):
    

    global controller
    

    # Caso de detectar la tecla [W], actualiza estado de variable

    if key == glfw.KEY_W:

        if action ==glfw.PRESS:

            controller.is_w_pressed = True

        elif action == glfw.RELEASE:

            controller.is_w_pressed = False


    # Caso de detectar la tecla [S], actualiza estado de variable

    if key == glfw.KEY_S:

        if action ==glfw.PRESS:

            controller.is_s_pressed = True

        elif action == glfw.RELEASE:

            controller.is_s_pressed = False


    # Caso de detectar la tecla [A], actualiza estado de variable

    if key == glfw.KEY_A:

        if action ==glfw.PRESS:

            controller.is_a_pressed = True

        elif action == glfw.RELEASE:

            controller.is_a_pressed = False


    # Caso de detectar la tecla [D], actualiza estado de variable

    if key == glfw.KEY_D:

        if action ==glfw.PRESS:

            controller.is_d_pressed = True

        elif action == glfw.RELEASE:

            controller.is_d_pressed = False


    # Caso de detecar la barra espaciadora, se cambia el metodo de dibujo

    if key == glfw.KEY_SPACE and action ==glfw.PRESS:

        controller.fillPolygon = not controller.fillPolygon


    # Caso en que se cierra la ventana

    elif key == glfw.KEY_ESCAPE and action ==glfw.PRESS:

        glfw.set_window_should_close(window, True)




if __name__ == "__main__":


    # Initialize glfw

    if not glfw.init():

        glfw.set_window_should_close(window, True)


    # Creating a glfw window

    width = 800

    height = 800

    title = "P3 - Drive simulator"

    window = glfw.create_window(width, height, title, None, None)


    if not window:
        glfw.terminate()

        glfw.set_window_should_close(window, True)


    glfw.make_context_current(window)


    # Connecting the callback function 'on_key' to handle keyboard events

    glfw.set_key_callback(window, on_key)


    # Pipeline para dibujar shapes con colores interpolados

    pipeline = es.SimpleTransformShaderProgram()

    # Pipeline para dibujar shapes con texturas

    tex_pipeline = es.SimpleTextureTransformShaderProgram()


    # Setting up the clear screen color

    glClearColor(0.15, 0.15, 0.15, 1.0)


    # Enabling transparencies

    glEnable(GL_BLEND)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    


    # Grafo de escena del auto

    car = createCar(pipeline)

    sun = createSun(pipeline)

    # Grafo de escena del background

    mainScene1 = createScene(pipeline)

    mainScene2 = createScene(pipeline)

    mainScene3 = createScene(pipeline)


    mundo1 = sg.SceneGraphNode("1")

    mundo1.childs += [mainScene1]

    mundo2 = sg.SceneGraphNode("2")

    mundo2.childs += [mainScene2]

    mundo3 = sg.SceneGraphNode("3")

    mundo3.childs += [mainScene3]
    


    worlds = sg.SceneGraphNode("paisaje")

    worlds.childs += [mundo1,mundo2, mundo3]


    supahScene= sg.SceneGraphNode("entire_world")

    supahScene.childs += [worlds,car,sun]


    # Se instancia el modelo del auto

    player = Player(0.3)

    # Se indican las referencias del nodo y el controller al modelo

    player.set_model(car)

    player.set_controller(controller)


    # Shape con textura de la carga

    garbage = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "ejercicio5/sprites/bag.png")


    # Se crean dos nodos de carga

    garbage1Node = sg.SceneGraphNode("garbage1")

    garbage1Node.childs = [garbage]


    garbage2Node = sg.SceneGraphNode("garbage2")

    garbage2Node.childs = [garbage]


    # Se crean el grafo de escena con textura y se agregan las cargas

    tex_scene = sg.SceneGraphNode("textureScene")

    tex_scene.childs = [garbage1Node, garbage2Node]


    # Se crean los modelos de la carga, se indican su nodo y se actualiza la posicion fija

    carga1 = Humanoid(0.2, -0.55, 0.1)

    carga1.set_model(garbage1Node)

    carga1.update()


    carga2 = Humanoid(0.7, -0.75, 0.1)

    carga2.set_model(garbage2Node)

    carga2.update()


    # Lista con todas las cargas

    cargas = [carga1, carga2]


    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible

    glfw.swap_interval(0)

    t0 = glfw.get_time()


    g0 = t0


    j = 0


    m1=1

    m2=1

    m3=1


    sg.findNode(supahScene, "sun").transform= tr.matmul([tr.translate(1.0,1.0,0), tr.scale(0.3,0.3,0)])


    world2 = sg.findNode(worlds, "2")

    world2.transform = tr.translate(2.0,0.0,0)


    world1 = sg.findNode(worlds, "1")

    world1.transform = tr.translate(0.0, 0.0,0.0)


    world3 = sg.findNode(worlds, "3")

    world3.transform= tr.translate(4.0, 0.0,0.0)


    # Application loop

    while not glfw.window_should_close(window):

        # Variables del tiempo

        t1 = glfw.get_time()

        delta = t1 -t0

        gelta = t1 -g0

        t0 = t1


        # Measuring performance

        perfMonitor.update(glfw.get_time())

        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events

        glfw.poll_events()


        # Filling or not the shapes depending on the controller state

        if (controller.fillPolygon):

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        else:

            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


        # Clearing the screen

        glClear(GL_COLOR_BUFFER_BIT)


        # Se llama al metodo del player para detectar colisiones

        player.collision(cargas)

        # Se llama al metodo del player para actualizar su posicion

        player.update(delta)


        # Se crea el movimiento de giro de los rotores

        rotor1 = sg.findNode(mundo1, "rtRotor")

        rotor1.transform = tr.rotationZ(t1)


        rotor2 = sg.findNode(mundo2, "rtRotor")

        rotor2.transform = tr.rotationZ(t1)


        rotor3 = sg.findNode(mundo3, "rtRotor")

        rotor3.transform = tr.rotationZ(t1)

        

        world1.transform=tr.translate((0.0)- ((t1%5)/2.5),0.0,0.0)

        world2.transform=tr.translate((2.0)- ((t1%5)/2.5),0.0,0.0)

        world3.transform=tr.translate((4.0)- ((t1%5)/2.5),0.0,0.0)


        

        # Se dibuja el grafo de escena principal

        glUseProgram(pipeline.shaderProgram)

        sg.drawSceneGraphNode(supahScene, pipeline, "transform")


        # Se crean basuras cada 5 segundos

        if(gelta > 2):

            g0 = t1

            newGarbageNode= sg.SceneGraphNode("garbage" + str(t1))

            newGarbageNode.childs+=[garbage]

            tex_scene.childs+=[newGarbageNode]

            newCarga = Humanoid(1.1 + t1/10, -(0.5 + random.uniform(0, 0.3)),0.1)

            newCarga.set_model(newGarbageNode)

            newCarga.update()

            cargas += [newCarga]


            # Aqui en ves de hacer mas basuras puedo

            # trasladar las cargas ya existentes a pos[0] = 1.1

            # esto ocurre cada segundos



        for x in cargas:

            x.pos[0] -= 0.007

            x.update()


        player.collision(cargas)
        


        # Se dibuja el grafo de escena con texturas

        glUseProgram(tex_pipeline.shaderProgram)

        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.

        glfw.swap_buffers(window)


    # freeing GPU memory

    supahScene.clear()

    #mainScene.clear()

    tex_scene.clear()
    
    glfw.terminate()