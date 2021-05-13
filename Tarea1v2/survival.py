""" survival game """

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
            
            uniform mat4 transform;

            in vec3 position;
            in vec3 color;

            out vec3 newColor;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;

            uniform float switchColor;

            void main()
            {
                outColor = vec4(newColor, 1.0f);
                if(switchColor>0.0){
                    if(outColor.b>0){
                        outColor.b = 0.5f;
                    } else {
                        outColor.g = 0.5f;
                    }
                }
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

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
        self.sprint = False
        self.direction = 1


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
            controller.direction = -1
        elif action == glfw.RELEASE:
            controller.is_a_pressed = False

    # Caso de detectar la tecla [D], actualiza estado de variable
    if key == glfw.KEY_D:
        if action ==glfw.PRESS:
            controller.is_d_pressed = True
            controller.direction = 1
        elif action == glfw.RELEASE:
            controller.is_d_pressed = False

    # Caso de detecar la barra espaciadora, se utilizan los lentes
    if key == glfw.KEY_SPACE:
        if action ==glfw.PRESS:
            controller.glasses = True
        elif action == glfw.RELEASE:
            controller.glasses = False

    # Caso de detectar el shift izq, actualiza la variable
    if key == glfw.KEY_LEFT_SHIFT:
        if action ==glfw.PRESS:
            controller.sprint = True
        elif action == glfw.RELEASE:
            controller.sprint = False

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

    # Shape de Jill
    gpuJill = createTextureGPUShape(bs.createTextureQuad(1, 1), green_pipeline, "sprites/hinata2.png", GL_STATIC_DRAW, True)
    gpuHealthPack =createGPUShape(createCrossShape(), switchingPipeline,GL_STREAM_DRAW)
    gpuPowerPack =createGPUShape(createPowerUp(), switchingPipeline,GL_STREAM_DRAW)

    # Grafo de power ups
    powerUpNode = sg.SceneGraphNode("Power UP")
    powerUpNode.transform = tr.matmul([tr.translate(0.9, -0.2, 0.0),tr.uniformScale(0.3)])
    powerUpNode.childs = [gpuPowerPack]

    # Grafo paraHealth
    healthNode= sg.SceneGraphNode("health")
    healthNode.transform = tr.matmul([tr.translate(0.9, 0.2, 0.0),tr.uniformScale(0.2)])
    healthNode.childs = [gpuHealthPack]

    #GrafoPower
    bonusNode= sg.SceneGraphNode("bonus")
    bonusNode.childs = [powerUpNode,healthNode]
    
    # Grafo de escena para Jill
    jillNode = sg.SceneGraphNode("Jill")
    jillNode.childs = [gpuJill]
    
    # Grafo de escena del background
    mainScene = createScene(pipeline)
    mundo = sg.SceneGraphNode("mundo")
    mundo.childs += [mainScene]
    
    worlds = sg.SceneGraphNode("paisaje")
    worlds.childs += [mundo]
    
    # Shape con texturas
    gpuZombie = createTextureGPUShape(bs.createTextureQuad(1,1), green_pipeline, "sprites/zombie.png", GL_STATIC_DRAW, True)
    gpuHuman = createTextureGPUShape(bs.createTextureQuad(1,1), green_pipeline, "sprites/estudiante5.png", GL_STATIC_DRAW, True)
    #gpuGameOver = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/game_over.png", GL_STATIC_DRAW, True)##
    #gpuWin = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/win2.png", GL_STATIC_DRAW, True)##

    forest = createTextureScene(tex_pipeline) # arriba

    zombieNode = sg.SceneGraphNode("Zombie")
    zombieNode.childs = [gpuZombie]

    gameoverNode = sg.SceneGraphNode("game over")
    #gameoverNode.childs = [gpuGameOver]##

    winNode = sg.SceneGraphNode("win")
    #winNode.childs = [gpuWin]##

    gateNode = sg.findNode(forest, "gate")

    # Se instancia el modelo del Jill
    player = Player(0.2)
    player.set_model(jillNode)
    player.set_controller(controller)

    storeNode = sg.findNode(forest, "store")
    store = Store(-0.8, 0.75)

    # Se crean el grafo de escena con textura

    tex_scene = sg.SceneGraphNode("textureScene")
    tex_scene.childs = [forest]

    tex_scene_green = sg.SceneGraphNode("green scene")
    tex_scene_green.childs = [jillNode]

    supahScene= sg.SceneGraphNode("entire_world")
    supahScene.childs += [worlds, tex_scene, tex_scene_green]

    # Lista con todos los NPC's
    enemies = []

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()
    g0 = t0
    s0 = t0

    # Inputs del usuario
    var_z = int(sys.argv[1]) # Cantidad de zombies
    var_h = int(sys.argv[2]) # Cantidad de humanos
    var_t = int(sys.argv[3]) # Tiempo en el cual deben aparecer humanos o zombies
    var_p = float(sys.argv[4]) # Probabilidad de que un humano zombifique cada T segundos

    notGameOver = True
    gameOver = False
    switch = True

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        gelta = t1 -g0
        selta = t1 -s0
        t0 = t1

        assert var_p < 1 and var_p > 0, "Ingrese valor entre 0 y 1 para la variable P (cuarto parametro)"

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
        #player.collision(enemies)
        if player.objective(store) and notGameOver:
            gpuWin = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/win2.png", GL_STATIC_DRAW, True)##
            winNode.childs= [gpuWin]##
            tex_scene.childs += [winNode]
            notGameOver = not notGameOver
            gameOver = True

        if player.zombie == 1 and gameOver:
            gpuGameOver = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/game_over.png", GL_STATIC_DRAW, True)
            gameoverNode.childs = [gpuGameOver]
            player.model.childs = [gpuZombie]
            winNode.childs = []
            tex_scene.childs+= [gameoverNode]
            gameOver = not gameOver

        winNode.transform = tr.matmul([tr.uniformScale(1 + 0.5*np.cos(-t1)), tr.rotationZ(-t1*0.5)])

        # Se llama al metodo del player para actualizar su posicion
        player.update(delta, controller.direction)
   
        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(worlds, pipeline, "transform")

        shearing = sg.findNode(tex_scene, "shearing")
        shearing.transform = tr.shearing(0, 0.1 * np.cos(t1), 0, 0, 0, 0)
        #######################################################################
        # Se crean personajes cada T segundos
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
            # Cada T segundos se verifica si Jill esta contagiada
            # y existe una probabilidad de P de perder
            if(player.infected == 1 and prob < var_p):
                player.zombie = 1
                player.model.childs = [gpuZombie] ##
            # Cada T segundos se verifica si un humano pasa a ser zombie
            for carga in enemies:
                if carga.zombie == 0 and carga.infected > 0:
                    new_prob = random.uniform(0, 1)
                    if(new_prob < var_p):
                        carga.zombie = 1
                        carga.model.childs = [gpuZombie]
            g0 = t1
        #####################################################################

        # Movemos a los personajes, detectando colisiones e infecciones
        for character in enemies:
            if character.t < 1.1:
                character.t += 0.0001
                character.update()
                character.collision(enemies)
            if character.zombie == 1:
                character.childs = [gpuZombie]
                character.model.childs = [gpuZombie]
            if character.t > 1.1:
                character.model.childs = []

        # Verificamos si el jugador se convierte en zombie
        if player.zombie==1 and notGameOver:
            gpuGameOver = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/game_over.png", GL_STATIC_DRAW, True)##
            gameoverNode.childs = [gpuGameOver]##
            player.model.childs = [gpuZombie]
            tex_scene.childs+=[gameoverNode]
            winNode.clear()
            notGameOver = False

        gameoverNode.transform = tr.scale(1 + 0.5*np.cos(t1), 1 + 0.2*np.sin(t1), 0)
        player.collision(enemies)

        # Se dibuja el grafo de escena con texturas
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")

        # Se usa el siguiente pipeline
        glUseProgram(green_pipeline.shaderProgram)

        # Verificamos si los personajes estan infectados, enviando un mensaje al shader
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
        sg.drawSceneGraphNode(jillNode, green_pipeline, "transform")

        # Se usa el siguiente pipeline
        glUseProgram(switchingPipeline.shaderProgram)

        # Hacemos cambiar los colores de los power ups cada dos segundos enviando un mensaje al shader
        if selta>2:
            if switch:
                glUniform1f(glGetUniformLocation(switchingPipeline.shaderProgram, "switchColor"), float(1))
            else:
                glUniform1f(glGetUniformLocation(switchingPipeline.shaderProgram, "switchColor"), float(0))
            switch = not switch
            s0= t1

        switchingPipeline.drawCall(gpuHealthPack, GL_LINES)
        switchingPipeline.drawCall(gpuPowerPack, GL_TRIANGLE_STRIP)

        # sprint del jugador
        if controller.sprint:
            player.vel = [0.7,0.7]
        else:
            player.vel = [0.3,0.3]

        sg.drawSceneGraphNode(bonusNode, switchingPipeline, "transform")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    supahScene.clear()
    mainScene.clear()
    worlds.clear()
    tex_scene.clear()
    tex_scene_green.clear()
    
    glfw.terminate()