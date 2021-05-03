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

class infectedPipeline:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;
            

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 130

            uniform float infected;

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                if(infected == 1)
                {
                    outColor = texture(samplerTex, outTexCoords);
                } else 
                {
                    outColor = texture(samplerTex, outTexCoords);
                }
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

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


# Clase controlador con variables para manejar el estado de ciertos botones
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.is_w_pressed = False
        self.is_s_pressed = False
        self.is_a_pressed = False
        self.is_d_pressed = False
        self.glasses = False


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

    # Caso de detecar la barra espaciadora, se utilizan los lentes
    if key == glfw.KEY_SPACE and action ==glfw.PRESS:
        controller.glasses = True
        #controller.fillPolygon = not controller.fillPolygon

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
    title = "Survival Game"
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
    # Pipeline de los lentes
    green_pipeline = infectedPipeline()

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Shape de hinata
    gpuHinata = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "Tarea1v2/sprites/hinata2.png")

    # Grafo de escena para Hinata
    hinataNode = sg.SceneGraphNode("Hinata")
    hinataNode.childs = [gpuHinata]
    
    # Grafo de escena del background
    mainScene2 = createScene(pipeline)

    
    mundo2 = sg.SceneGraphNode("2")
    mundo2.childs += [mainScene2]
    
    

    worlds = sg.SceneGraphNode("paisaje")
    worlds.childs += [mundo2]

    supahScene= sg.SceneGraphNode("entire_world")
    supahScene.childs += [worlds]
    

    # Shape con texturas
    garbage = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/sidewalk.jpg")
    gpuZombie = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/zombie.png")
    gpuHuman = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/estudiante5.png")
    gpuGameOver = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/game_over.png")

    zombieNode = sg.SceneGraphNode("Zombie")
    zombieNode.childs = [gpuZombie]

    gameoverNode = sg.SceneGraphNode("game over")
    gameoverNode.childs = [gpuGameOver]

    # Se instancia el modelo del hinata
    player = Player(0.2)
    player.set_model(hinataNode)
    player.set_controller(controller)


    forest = createTextureScene(tex_pipeline)


    gpuStore = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "Tarea1v2/sprites/tienda.png")
    storeNode = sg.SceneGraphNode("store")
    storeNode.transform = tr.matmul([tr.translate(-0.8, 0.7, 0),tr.rotationZ(1.57), tr.scale(0.5,0.35,1)])
    storeNode.childs = [gpuStore]

    # Se crean el grafo de escena con textura y se agregan las cargas
    tex_scene = sg.SceneGraphNode("textureScene")
    tex_scene.childs = [forest, storeNode, hinataNode]


    # Lista con todas las cargas de NPC's
    cargas = []

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    g0 = t0

    # Inputs del usuario
    var_z = int(sys.argv[1]) # Cantidad de zombies
    var_h = int(sys.argv[2]) # Cantidad de humanos
    var_t = int(sys.argv[3]) # Tiempo en el cual deben aparecer humanos o zombies
    var_p = float(sys.argv[4]) # Probabilidad de que un humano zombifique cada T segundos

    notGameOver = True

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

        if controller.glasses:
            currentPipeline = green_pipeline
        else:
            currentPipeline = tex_pipeline

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Se llama al metodo del player para detectar colisiones
        player.collision(cargas)
        # Se llama al metodo del player para actualizar su posicion
        player.update(delta)
   
        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(supahScene, pipeline, "transform")

        shearing = sg.findNode(tex_scene, "shearing1")
        shearing.transform = tr.shearing(0, 0.1 * np.cos(t1), 0, 0, 0, 0)

        # Se crean basuras cada 5 segundos
        if(gelta > var_t):
            next_npc = random.randint(0, 1)
            prob = random.uniform(0, 1)
            # Se crea un zombie
            if((next_npc == 0 or var_h == 0) and var_z > 0):
                newZombieNode= sg.SceneGraphNode("zombie" + str(t1))
                newZombieNode.childs+=[gpuZombie]
                tex_scene.childs+=[newZombieNode]
                newZombie = Carga(random.uniform(-0.55,0.55),1.1, 0.3, 1, "z" + str(t1))
                newZombie.set_model(newZombieNode)
                newZombie.update()
                cargas += [newZombie]
                var_z-=1
            # Se crea un humano
            elif((next_npc == 1 or var_z == 0) and var_h > 0):
                newHumanNode = sg.SceneGraphNode("human" + str(t1))
                newHumanNode.childs+= [gpuHuman]
                tex_scene.childs+=[newHumanNode]
                newHuman = Carga(random.uniform(-0.55,0.55),1.1, 0.3, 0, "h" + str(t1))
                newHuman.set_model(newHumanNode)
                newHuman.update()
                cargas+=[newHuman]
                var_h-=1
            # Cada T segundos se verifica si hinata esta contagiada
            # y existe una probabilidad de P de perder
            if(player.infected == 1 and prob < var_p):
                player.zombie = 1
                player.childs = [gpuZombie]
                player.set_model(zombieNode)
            # Cada T segundos se verifica si un humano pasa a ser zombie
            for carga in cargas:
                if(carga.zombie == 0 and carga.infected > 0 and prob < var_p):
                    carga.zombie = 1
                    carga.model.childs = [gpuZombie]
                    #carga.set_model(zombieNode)
            g0 = t1

        # Las basuras se desplazan
        garbages = sg.findNode(tex_scene, "textureScene")
        garbages.transform = tr.translate(0.0, 0.0, 0.0)


        for character in cargas:
            #x.pos[1]-= 0.0007
            #x.pos[0]+= (5-random.randint(1,10))/10000
            character.t += 0.0001
            character.update()
            character.collision(cargas)
            if character.zombie == 1:
                character.childs = [gpuZombie]
                character.model.childs = [gpuZombie]
                #x.set_model(zombieNode)

        if player.zombie==1 and notGameOver:
            hinataNode.childs = [gpuZombie]
            player.set_model(zombieNode)
            tex_scene.childs+=[gameoverNode]
            notGameOver = False

        gameoverNode.transform = tr.scale(1 + 0.5*np.cos(t1), 1 + 0.2*np.sin(t1), 1)

        player.collision(cargas)

        """
        bosque = sg.findNode(tex_scene, "leftTrees")
        bosque.transform = tr.shearing(0.05 * np.cos(t1), 0.05 * np.cos(t1),0,0,0,0)
        """

        # Se dibuja el grafo de escena con texturas
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")

        """
        glUseProgram(currentPipeline.shaderProgram)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "infected"), player.infected)
        sg.drawSceneGraphNode(npc_scene, currentPipeline, "transform")
        """

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    supahScene.clear()
    mainScene2.clear()
    tex_scene.clear()
    
    glfw.terminate()