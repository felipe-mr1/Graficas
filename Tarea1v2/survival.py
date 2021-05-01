""" P3 [Drive simulator] """

import glfw
import OpenGL.GL.shaders
import numpy as np
import random
import sys
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

    
    # Grafo de escena para Hinata
    gpuHinata = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "Tarea1v2/sprites/hinata2.png")
    hinataNode = sg.SceneGraphNode("Hinata")
    hinataNode.childs = [gpuHinata]
    
    # Grafo de escena del auto
    car = createCar(pipeline)
    # Grafo de escena del background
    mainScene2 = createScene(pipeline)

    
    mundo2 = sg.SceneGraphNode("2")
    mundo2.childs += [mainScene2]
    
    

    worlds = sg.SceneGraphNode("paisaje")
    worlds.childs += [mundo2]

    supahScene= sg.SceneGraphNode("entire_world")
    supahScene.childs += [worlds]

    # Se instancia el modelo del auto
    player = Player(0.2)
    # Se indican las referencias del nodo y el controller al modelo
    player.set_model(hinataNode)
    player.set_controller(controller)

    # Shape con textura de la carga
    garbage = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/sidewalk.jpg")
    gpuZombie = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/zombie.png")
    gpuHuman = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/estudiante5.png")


    forest = createTextureScene(tex_pipeline)

    # Se crean dos nodos de carga
    garbage1Node = sg.SceneGraphNode("garbage1")
    garbage1Node.childs = [garbage]

    garbage2Node = sg.SceneGraphNode("garbage2")
    garbage2Node.childs = [garbage]

    gpuStore = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "Tarea1v2/sprites/tienda.png")
    storeNode = sg.SceneGraphNode("store")
    storeNode.transform = tr.matmul([tr.translate(-0.8, 0.7, 0),tr.rotationZ(1.57), tr.scale(0.5,0.35,1)])
    storeNode.childs = [gpuStore]

    # Se crean el grafo de escena con textura y se agregan las cargas
    tex_scene = sg.SceneGraphNode("textureScene")
    tex_scene.childs = [garbage1Node, garbage2Node, hinataNode, forest, storeNode]

    # Se crean los modelos de la carga, se indican su nodo y se actualiza la posicion fija
    carga1 = Carga(0.2, -0.55, 0.1)
    carga1.set_model(garbage1Node)
    carga1.update()

    carga2 = Carga(0.7, -0.75, 0.1)
    carga2.set_model(garbage2Node)
    carga2.update()

    # Lista con todas las cargas
    cargas = [carga1, carga2]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    g0 = t0



    # Inputs del usuario
    var_z = int(sys.argv[1]) # Cantidad de zombies
    var_h = int(sys.argv[2]) # Cantidad de humanos
    var_t = int(sys.argv[3]) # Tiempo en el cual deben aparecer humanos o zombies
    var_p = int(sys.argv[4]) # Probabilidad de que un humano zombifique cada T segundos



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


        # Escena principal
        escena = sg.findNode(supahScene, "paisaje")
        escena.transform = tr.translate(0.0, 0.0, 0.0)

        
        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(supahScene, pipeline, "transform")

        # Se crean basuras cada 5 segundos
        if(gelta > var_t):
            next_npc = random.randint(0, 1)
            if(next_npc == 0 or var_h == 0):
                newZombieNode= sg.SceneGraphNode("zombie" + str(t1))
                newZombieNode.childs+=[gpuZombie]
                tex_scene.childs+=[newZombieNode]
                newZombie = Carga(random.uniform(-0.55,0.55),1.1, 0.3)
                newZombie.set_model(newZombieNode)
                newZombie.update()
                cargas += [newZombie]
            elif(next_npc == 1 or var_z == 0):
                newHumanNode = sg.SceneGraphNode("human" + str(t1))
                newHumanNode.childs+= [gpuHuman]
                tex_scene.childs+=[newHumanNode]
                newHuman = Carga(random.uniform(-0.55,0.55),1.1, 0.3)
                newHuman.set_model(newHumanNode)
                newHuman.update()
                cargas+=[newHuman]
            g0 = t1

        # Las basuras se desplazan
        garbages = sg.findNode(tex_scene, "textureScene")
        garbages.transform = tr.translate(0.0, 0.0, 0.0)



        for x in cargas:
            x.pos[1]-= 0.0007
            x.update()

        player.collision(cargas)
        """
        bosque = sg.findNode(tex_scene, "leftTrees")
        bosque.transform = tr.shearing(0.05 * np.cos(t1), 0,0,0,0,0)
        """

        # Se dibuja el grafo de escena con texturas
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    supahScene.clear()
    mainScene2.clear()
    tex_scene.clear()
    
    glfw.terminate()