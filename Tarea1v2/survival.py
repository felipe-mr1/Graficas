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

from grafica.gpu_shape import GPUShape

# We will use 32 bits data, so an integer has 4 bytes

# 1 byte = 8 bits

SIZE_IN_BYTES = 4


class infectedPipeline:


    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;

            uniform float infected;

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

            uniform float infectedd;

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
                if(infectedd > 0.0){
                    outColor.g = 1.0f;
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


class switchingColorPipeline:


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

            uniform float switchColor;
            
            in vec3 newColor;

            out vec4 outColor;

            void main()
            {
                outColor = vec4(newColor, 1.0f);
                if(switchColor > 0.0){
                    if(newColor.b>0){
                        outColor.b = 0.5f;
                    } else{
                        outColor.g = 0.5f;
                    }
                } else {
                    if(newColor.b>0){
                        outColor.b = 1.0f;
                    } else{
                        outColor.g = 1.0f;
                    }
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


# Clase controlador con variables para manejar el estado de ciertos botone
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
        controller.glasses = not controller.glasses
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
    # Switching pipeline
    switchingPipeline = switchingColorPipeline()

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Shape de hinata
    gpuHinata = createTextureGPUShape(bs.createTextureQuad(1, 1), green_pipeline, "Tarea1v2/sprites/hinata2.png", GL_DYNAMIC_DRAW, True)
    gpuHealthPack =createGPUShape(createCrossShape(), switchingPipeline,GL_STREAM_DRAW)
    gpuPowerPack =createGPUShape(createPowerUp(), switchingPipeline,GL_STREAM_DRAW)

    # Grafo de power ups
    powerUpNode = sg.SceneGraphNode("Power UP")
    powerUpNode.childs = [gpuPowerPack]

    # Grafo paraHealth
    healthNode= sg.SceneGraphNode("health")
    healthNode.childs = [gpuPowerPack]

    #GrafoPower
    bonusNode= sg.SceneGraphNode("bonus")
    bonusNode.childs = [powerUpNode,healthNode]
    
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

    #garbage = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/sidewalk.jpg")
    gpuZombie = createTextureGPUShape(bs.createTextureQuad(1,1), green_pipeline, "Tarea1v2/sprites/zombie.png", GL_DYNAMIC_DRAW, True)
    gpuHuman = createTextureGPUShape(bs.createTextureQuad(1,1), green_pipeline, "Tarea1v2/sprites/estudiante5.png", GL_DYNAMIC_DRAW, True)
    gpuGameOver = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/game_over.png", GL_DYNAMIC_DRAW, True)
    gpuWin = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "Tarea1v2/sprites/win2.png", GL_DYNAMIC_DRAW, True)


    zombieNode = sg.SceneGraphNode("Zombie")
    zombieNode.childs = [gpuZombie]

    gameoverNode = sg.SceneGraphNode("game over")
    gameoverNode.childs = [gpuGameOver]

    winNode = sg.SceneGraphNode("win")
    winNode.childs = [gpuWin]

    # Se instancia el modelo del hinata
    player = Player(0.2)
    player.set_model(hinataNode)
    player.set_controller(controller)

    forest = createTextureScene(tex_pipeline)

    gpuStore = createTextureGPUShape(bs.createTextureQuad(1, 1), tex_pipeline, "Tarea1v2/sprites/tienda.png",GL_STATIC_DRAW, False)
    storeNode = sg.SceneGraphNode("store")
    storeNode.transform = tr.matmul([tr.translate(-0.8, 0.75, 0),tr.rotationZ(1.57), tr.scale(0.5,0.35,1)])
    storeNode.childs = [gpuStore]
    store = Store(-0.8, 0.75)

    # Se crean el grafo de escena con textura

    tex_scene = sg.SceneGraphNode("textureScene")
    tex_scene.childs = [forest, storeNode] # Hinata node

    tex_scene_green = sg.SceneGraphNode("green scene")
    tex_scene_green.childs = [hinataNode]

    # Lista con todos los NPC's
    enemies = []

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
    switch = True

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
        player.collision(enemies)
        if player.objective(store) and notGameOver:
            tex_scene.childs += [winNode]
            notGameOver = True

        winNode.transform = tr.matmul([tr.uniformScale(1 + 0.5*np.cos(-t1)), tr.rotationZ(-t1*0.5)])
        # Se llama al metodo del player para actualizar su posicion
        player.update(delta)
   
        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(supahScene, pipeline, "transform")

        shearing = sg.findNode(tex_scene, "shearing")
        shearing.transform = tr.shearing(0, 0.1 * np.cos(t1), 0, 0, 0, 0)

        # Se crean basuras cada 5 segundos
        if(gelta > var_t):
            next_npc = random.randint(0, 1)
            prob = random.uniform(0, 1)
            # Se crea un zombie
            if((next_npc == 0 or var_h == 0) and var_z > 0):
                newZombieNode= sg.SceneGraphNode("zombie" + str(t1))
                newZombieNode.childs+=[gpuZombie]
                tex_scene_green.childs+=[newZombieNode] #green
                newZombie = Humanoid(random.uniform(-0.55,0.55),1.1, 0.3, 1, "z" + str(t1))
                newZombie.set_model(newZombieNode)
                newZombie.update()
                enemies += [newZombie]
                var_z-=1
            # Se crea un humano
            elif((next_npc == 1 or var_z == 0) and var_h > 0):
                newHumanNode = sg.SceneGraphNode("human" + str(t1))
                newHumanNode.childs+= [gpuHuman]
                tex_scene_green.childs+=[newHumanNode] #green
                newHuman = Humanoid(random.uniform(-0.55,0.55),1.1, 0.3, 0, "h" + str(t1))
                newHuman.set_model(newHumanNode)
                newHuman.update()
                enemies +=[newHuman]
                var_h-=1
            # Cada T segundos se verifica si hinata esta contagiada
            # y existe una probabilidad de P de perder
            if(player.infected == 1 and prob < var_p):
                player.zombie = 1
                player.childs = [gpuZombie]
                player.set_model(zombieNode)
            # Cada T segundos se verifica si un humano pasa a ser zombie
            for carga in enemies:
                new_prob = random.uniform(0, 1)
                if(carga.zombie == 0 and carga.infected > 0 and new_prob < var_p):
                    carga.zombie = 1
                    carga.model.childs = [gpuZombie]
            """
            if switch:
                glUniform1f(glGetUniformLocation(switchingPipeline.shaderProgram, "switchColor"), 1.0)
            else:
                glUniform1f(glGetUniformLocation(switchingPipeline.shaderProgram, "switchColor"), 0.0)
            """
            switch = not switch
            g0 = t1

        for character in enemies:
            if character.t < 1.1:
                character.t += 0.0001
                character.update()
                character.collision(enemies)
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
        player.collision(enemies)

        # Se dibuja el grafo de escena con texturas
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")

        glUseProgram(green_pipeline.shaderProgram)


        for character in enemies:
            if controller.glasses:
                glUniform1f(glGetUniformLocation(green_pipeline.shaderProgram, "infectedd"), float(character.infected))
            else:
                glUniform1f(glGetUniformLocation(green_pipeline.shaderProgram, "infectedd"), 0.0)
            sg.drawSceneGraphNode(character.model, green_pipeline, "transform")

        if(controller.glasses):
            glUniform1f(glGetUniformLocation(green_pipeline.shaderProgram, "infectedd"), float(player.infected))
        else:
            glUniform1f(glGetUniformLocation(green_pipeline.shaderProgram, "infectedd"), 0.0)
        sg.drawSceneGraphNode(hinataNode, green_pipeline, "transform")

        glUseProgram(switchingPipeline.shaderProgram)

        #sg.drawSceneGraphNode(bonusNode, switchingPipeline, "switchColor")

        #switchingPipeline.drawCall(gpuHealthPack, GL_LINES)
        #switchingPipeline.drawCall(gpuPowerPack, GL_LINES)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    supahScene.clear()
    mainScene2.clear()
    tex_scene.clear()
    
    glfw.terminate()