from model import poolBall, scoreHole
from curves import evalCurveBezier, evalCurveCR, evalCurveCR9, evalCurveHermite, evalCurveHermiteAndBezier
import glfw
from OpenGL.GL import *
import sys
import json
import OpenGL.GL.shaders
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.performance_monitor as pm
import grafica.lighting_shaders as ls
import grafica.scene_graph as sg
from shapes3d import *
from grafica.gpu_shape import GPUShape
import openmesh as om
from time import sleep, thread_time
import shader as sh
import shapes3d as s3d

import imgui
from imgui.integrations.glfw import GlfwRenderer

LIGHT_CEL_SHADING = 0
LIGHT_PHONG = 1

# Funciones del repositiorio del curso

def rotate2D(vector, theta):
    """
    Direct application of a 2D rotation
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        cos_theta * vector[0] - sin_theta * vector[1],
        sin_theta * vector[0] + cos_theta * vector[1]
    ], dtype = np.float32)


def collide(circle1, circle2):
    """
    If there are a collision between the circles, it modifies the velocity of
    both circles in a way that preserves energy and momentum.
    """
    
    normal = circle2.position - circle1.position
    normal /= np.linalg.norm(normal)

    circle1MovingToNormal = np.dot(circle2.velocity, normal) > 0.0
    circle2MovingToNormal = np.dot(circle1.velocity, normal) < 0.0

    if not (circle1MovingToNormal and circle2MovingToNormal):

        # obtaining the tangent direction
        tangent = rotate2D(normal, np.pi/2.0)

        # Projecting the velocity vector over the normal and tangent directions
        # for both circles, 1 and 2.
        v1n = np.dot(circle1.velocity, normal) * normal
        v1t = np.dot(circle1.velocity, tangent) * tangent

        v2n = np.dot(circle2.velocity, normal) * normal
        v2t = np.dot(circle2.velocity, tangent) * tangent

        # swaping the normal components...
        # this means that we applying energy and momentum conservation
        circle1.velocity = v2n + v1t
        circle2.velocity = v1n + v2t


def areColliding(ball1, ball2):

    difference = ball2.position - ball1.position
    distance = np.linalg.norm(difference)
    collisionDistance = ball2.radius + ball1.radius
    return distance < collisionDistance

    # Fin de funciones del repositorio del curso

def readFaceVertex(faceDescription):

    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]

    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex



def readOBJ(filename, color):

    vertices = []
    normals = []
    textCoords= []
    faces = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split()
            
            if aux[0] == 'v':
                vertices += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                #assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                textCoords += [[float(coord) for coord in aux[1:3]]]

            elif aux[0] == 'f':
                N = len(aux)                
                faces += [[readFaceVertex(faceVertex) for faceVertex in aux[1:4]]]
                for i in range(3, N-1):
                    faces += [[readFaceVertex(faceVertex) for faceVertex in [aux[i], aux[i+1], aux[1]]]]

        vertexData = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0,3):
                vertex = vertices[face[i][0]-1]
                #tex = vertices[face[i][1]-0]
                normal = normals[face[i][2]-1]

                vertexData += [
                    vertex[0], vertex[1], vertex[2],
                    color[0], color[1], color[2], # reemplazar por texturas tex[0],tex[1]
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3        

        return bs.Shape(vertexData, indices)

class PolarCamera:
    def __init__(self, aCurve):
        self.center = np.array([0.0, -0.5, -0.5]) # z = -0.5
        self.theta = 0
        self.rho = 1 # r = 5
        self.eye = np.array([0.0, 0.0, 0.0])
        self.height = 0.5
        self.up = np.array([0, 0, 1])
        self.viewMatrix = None
        self.curve = aCurve
        self.pos = [0,0,0]
        self.index = 0

    def set_theta(self, delta):
        self.theta = (self.theta + delta) % (np.pi * 2)

    def set_rho(self, delta):
        if ((self.rho + delta) > 0.3 and (self.rho + delta) < 1.5):
            self.rho += delta

    def update_view(self, posX, posY):
        # Un osho parametrizado:
        # x: self.rho *(np.cos(self.theta) / ((np.sin(self.theta)**2) + 1)) + self.center[0]
        # y: self.rho *((np.cos(self.theta) * np.sin(self.theta)) / ((np.sin(self.theta)**2)+ 1)) + self.center[1]

        #self.eye[0] = self.rho *(np.cos(self.theta) / ((np.sin(self.theta)**2) + 1)) + self.center[0] #self.rho * np.sin(self.theta) + self.center[0]
        #self.eye[1] = self.rho *(((np.cos(self.theta) * np.sin(self.theta)) / ((np.sin(self.theta)**2)+ 1))) + 1.0 #self.rho * np.cos(self.theta) + self.center[1]
        #self.eye[2] = self.height + self.center[2]
        self.eye[0] = posX + (self.rho * np.cos(self.theta))
        self.eye[1] = posY + (self.rho * np.sin(self.theta))
        self.eye[2] = -0.5
        viewMatrix = tr.lookAt(
            self.eye,
            np.array([posX, posY, -1.0]),  # center
            self.up
        )
        return viewMatrix
    
    def upperView(self):
        self.eye[0] = 0
        self.eye[1] = 0
        self.eye[2] = 1.5
        viewMatrix = tr.lookAt(
            self.eye,
            np.array([0.0, 0, 0]),
            np.array([-1, 0, 0])
        )
        return viewMatrix
        

    def update_autoview(self):
        self.index += 1
        if self.index == len(self.curve):
            self.index = 0
        self.pos = self.curve[self.index]
        self.eye[0] = self.pos[0]
        self.eye[1] = self.pos[1]
        self.eye[2] = self.pos[2]
        viewMatrix = tr.lookAt(
            self.eye,
            np.array([0.0, 0.0, -1.0]),
            self.up
        )
        return viewMatrix

class Controller:
    def __init__(self, cameraCurve):
        self.fillPolygon = True
        self.showAxis = True

        self.is_up_pressed = False
        self.is_down_pressed = False
        self.is_left_pressed = False
        self.is_right_pressed = False

        self.polar_camera = PolarCamera(cameraCurve)

        self.lightingModel = LIGHT_CEL_SHADING

        self.slowMotion = False

        self.autoCameraView = False

        self.fourTones = False

        self.spotLight = False

        self.topView = False

        self.hit = False

    def get_camera(self):
        return self.polar_camera

    def on_key(self, window, key, scancode, action, mods):

        if key == glfw.KEY_UP:
            if action == glfw.PRESS:
                self.is_up_pressed = True
            elif action == glfw.RELEASE:
                self.is_up_pressed = False

        if key == glfw.KEY_DOWN:
            if action == glfw.PRESS:
                self.is_down_pressed = True
            elif action == glfw.RELEASE:
                self.is_down_pressed = False

        if key == glfw.KEY_RIGHT:
            if action == glfw.PRESS:
                self.is_right_pressed = True
            elif action == glfw.RELEASE:
                self.is_right_pressed = False

        if key == glfw.KEY_LEFT:
            if action == glfw.PRESS:
                self.is_left_pressed = True
            elif action == glfw.RELEASE:
                self.is_left_pressed = False
        
        if key == glfw.KEY_SPACE:
            if action == glfw.PRESS:
                self.fillPolygon = not self.fillPolygon

        if key == glfw.KEY_ESCAPE:
            if action == glfw.PRESS:
                glfw.set_window_should_close(window, True)

        if key == glfw.KEY_TAB:
            if action == glfw.PRESS:
                self.lightingModel = LIGHT_PHONG
            elif action == glfw.RELEASE:
                self.lightingModel = LIGHT_CEL_SHADING

        if key == glfw.KEY_1:
            if action == glfw.PRESS:
                self.topView = not self.topView

        if key == glfw.KEY_2:
            if action == glfw.PRESS:
                self.autoCameraView = not self.autoCameraView

        if key == glfw.KEY_3:
            if action == glfw.PRESS:
                self.fourTones = True
            elif action == glfw.RELEASE:
                self.fourTones = False

        if key == glfw.KEY_4:
            if action == glfw.PRESS:
                self.spotLight = True
            elif action == glfw.RELEASE:
                self.spotLight = False

        if key == glfw.KEY_Z:
            if action == glfw.PRESS:
                self.hit = True
            elif action == glfw.RELEASE:
                self.hit = False

        elif key == glfw.KEY_LEFT_CONTROL:
            if action == glfw.PRESS:
                self.showAxis = not self.showAxis


    #Funcion que recibe el input para manejar la camara
    def update_camera(self, delta):
        if self.is_left_pressed:
            self.polar_camera.set_theta(-2 * delta)

        if self.is_right_pressed:
            self.polar_camera.set_theta( 2 * delta)

        if self.is_up_pressed:
            self.polar_camera.set_rho(-5 * delta)

        if self.is_down_pressed:
            self.polar_camera.set_rho(5 * delta)

    def autoCamera(self):
        self.polar_camera.update_autoview()

def transformGuiOverlay(locationZ, la, ld, ls, cte_at, lnr_at, qud_at, shininess):

    # start new frame context
    imgui.new_frame()

    # open new window context
    imgui.begin("Light control", False, imgui.WINDOW_ALWAYS_AUTO_RESIZE)

    # draw text label inside of current window
    imgui.text("Configuration sliders")

    edited, locationZ = imgui.slider_float("location Z", locationZ, -1.0, 2.3)
    edited, la = imgui.color_edit3("la", la[0], la[1], la[2])
    if imgui.button("clean la"):
        la = (1.0, 1.0, 1.0)
    edited, ld = imgui.color_edit3("ld", ld[0], ld[1], ld[2])
    if imgui.button("clean ld"):
        ld = (1.0, 1.0, 1.0)
    edited, ls = imgui.color_edit3("ls", ls[0], ls[1], ls[2])
    if imgui.button("clean ls"):
        ls = (1.0, 1.0, 1.0)
    edited, cte_at = imgui.slider_float("constant Att.", cte_at, 0.0001, 0.2)
    edited, lnr_at = imgui.slider_float("linear Att.", lnr_at, 0.01, 0.1)
    edited, qud_at = imgui.slider_float("quadratic Att.", qud_at, 0.005, 0.1)
    edited, shininess = imgui.slider_float("shininess", shininess, 0.1, 200)

    # close current window context
    imgui.end()

    # pass all drawing comands to the rendering pipeline
    # and close frame context
    imgui.render()
    imgui.end_frame()

    return locationZ, la, ld, ls, cte_at, lnr_at, qud_at, shininess


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Pool Party"

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    cameraPoints = [
        -0.2, 1.5, -0.4,      # 0
        0, 0.8+0.3, -0.35,    # 1
        0.4+0.3, 0.5, -0.3,   # 2
        0, 0.15+0.3, -0.25,   # 3
        -0.4-0.3, -0.5, -0.2, # 4
        0, -1, -0.1,          # 5
        0.4+0.3, -0.5, -0.2,  # 6
        0, 0.15+0.3, -0.2,    # 7
        -0.4-0.3, 0.5, -0.3,  # 8
        0, 0.8+0.3, -0.35,    # 9
        0.2, 1.5, -0.4        # 10
    ]

    cameraCurve = evalCurveCR9(1800, cameraPoints)
    controller = Controller(cameraCurve)
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

     # Different shader programs for different lighting strategies
    pipeline1 = ls.SimpleFlatShaderProgram()
    phongPipeline = sh.CelShadingPhongShaderProgram()
    phongPipeline2 = ls.SimplePhongShaderProgram()
    phongPipeline3 = ls.SimplePhongShaderProgram()
    CSphongTexPipeline2 = sh.CelShading4TonesPhongShaderProgram()
    phongTexPipeline = ls.SimpleTexturePhongShaderProgram()
    CSphongTexPipeline = sh.CelShadingTexturePhongShaderProgram()
    CSspotlightPipeline = sh.CelShadingSpotLight()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    shadowPipeline = es.SimpleTextureModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(mvpPipeline, bs.createAxis(4))

    gpuRedCube = createGPUShape(phongPipeline, bs.createColorNormalsCube(1,0,0))

    scene = createScene(phongPipeline)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    

    Torus = createTextureGPUShapeX(createTextureTorus(50), CSphongTexPipeline, 
    GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST, 'sprites/metal.png')
    torusNode = sg.SceneGraphNode("torus")
    torusNode.transform = tr.matmul([tr.translate(-2.0,-1.5,-2.0),tr.scale(0.5, 0.5, 2.0)])
    torusNode.childs = [Torus]

    shapeStick = readOBJ('sprites/palito.obj',(0,0,0))
    gpuBaby = createGPUShape(phongPipeline, shapeStick)

    dababy = sg.SceneGraphNode("baby")
    dababy.transform = tr.matmul([tr.translate(4.0,0,-0.45),tr.rotationZ(np.pi),tr.rotationY(np.pi * 0.515),tr.uniformScale(0.025)])
    #tr.matmul([tr.translate(3.9,0,-0.5),tr.rotationZ(np.pi),tr.rotationY(np.pi/2),tr.uniformScale(0.025)])
    dababy.childs = [gpuBaby]

    palitoNode = sg.SceneGraphNode("palito")
    palitoNode.childs = [dababy]

    sphereMesh = createSphereMesh(64,0,0,0)
    sphereMesh_vertices, sphereMesh_indices = get_vertexs_and_indexes(sphereMesh, [0.66,0.66,0.66])

    gpuSphere = es.GPUShape().initBuffers()
    pipeline1.setupVAO(gpuSphere)
    gpuSphere.fillBuffers(sphereMesh_vertices, sphereMesh_indices, GL_STATIC_DRAW)

    sphereNode = sg.SceneGraphNode("sphereMeshRot")
    sphereNode.childs = [gpuSphere]

    sphereNodeLoc = sg.SceneGraphNode("sphereMesh")
    sphereNodeLoc.transform = tr.matmul([tr.translate(2.0, -2.0, -2.0)])
    sphereNodeLoc.childs = [sphereNode]

    hangerShape = hanger()
    gpuHanger = es.GPUShape().initBuffers()
    mvpPipeline.setupVAO(gpuHanger)
    gpuHanger.fillBuffers(hangerShape.vertices, hangerShape.indices, GL_STATIC_DRAW)

    screenShape = s3d.createTextureNormalsCube(2,2)
    gpuScreen = es.GPUShape().initBuffers() 
    CSphongTexPipeline.setupVAO(gpuScreen)
    gpuScreen.texture = es.textureSimpleSetup("sprites/something.png", GL_REPEAT, GL_REPEAT, GL_NEAREST_MIPMAP_LINEAR, GL_NEAREST)
    gpuScreen.fillBuffers(screenShape.vertices, screenShape.indices, GL_STATIC_DRAW)
    glGenerateMipmap(GL_TEXTURE_2D)

    screenNode = sg.SceneGraphNode("screen")
    screenNode.transform = tr.translate(-1.0, -2.9, 0)
    screenNode.childs = [gpuScreen]

    # Reutilizamos vertices e indices de la figura anterior
    gpuScreen2 = copy.deepcopy(gpuScreen)
    CSphongTexPipeline.setupVAO(gpuScreen2)
    gpuScreen2.texture = es.textureSimpleSetup("sprites/lavalamp.jpg", GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    gpuScreen2.fillBuffers(screenShape.vertices, screenShape.indices, GL_STATIC_DRAW)
    glGenerateMipmap(GL_TEXTURE_2D)

    screen2Node = sg.SceneGraphNode("screen")
    screen2Node.transform = tr.translate(1.0, -2.9, 0.0)
    screen2Node.childs = [gpuScreen2]

    gpuTest = createTextureGPUShape(bs.createTextureQuad(1, 1), shadowPipeline, "sprites/blacko2.png")
    testNode = sg.SceneGraphNode("test")
    testNode.transform = tr.matmul([tr.translate(0,0,-0.94), tr.uniformScale(0.05)])
    testNode.childs = [gpuTest]

    gpuWhiteBall = createGPUShape(phongPipeline ,createColorNormalSphere(50, 1, 1, 1))
    whiteBallNode = sg.SceneGraphNode("White Ball")
    whiteBallNode.transform = tr.matmul([tr.translate(0.5,0, -0.93),tr.uniformScale(0.04)])
    whiteBallNode.childs = [gpuWhiteBall]

    ballsNode = createPoolBalls(phongTexPipeline)

    shadows = createShadows(mvpPipeline)

    table = createTable(phongPipeline)
    
    score = createCircleScore_v2(mvpPipeline)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()
    s = t0
    
    controller = Controller(cameraCurve)
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    locationZ = 2.3
    la = [1.0, 1.0, 1.0] 
    ld = [1.0, 1.0, 1.0] 
    ls = [1.0, 1.0, 1.0]
    cte_at = 0.0001
    lnr_at= 0.03
    qud_at = 0.01
    shininess = 100
    aux_r = 0.7
    aux_g = 0.7
    aux_b = 0.7

    var = 0

    # Abrir archivo JSON

    jason = str(sys.argv[1])
    with open(jason,"r") as config:
        data = json.load(config)
    fric = data['friccion']
    rest = data['restitucion']

    # Buscando nodos

    ball1 = sg.findNode(ballsNode, "ball1")
    shadow1 = sg.findNode(shadows, "Shadow1")
    bola1 = poolBall(0.04, rest, fric, [0,0], [0,0])
    bola1.set_model(ball1)

    ball2 = sg.findNode(ballsNode, "ball2")
    shadow2 = sg.findNode(shadows, "Shadow2")
    bola2 = poolBall(0.04, rest, fric,[-0.4 * 0.08,-0.3 * 0.08],[0,0])
    bola2.set_model(ball2)

    ball3 = sg.findNode(ballsNode, "ball3")
    shadow3 = sg.findNode(shadows, "Shadow3")
    bola3 = poolBall(0.04, rest, fric,[-0.4 * 0.08, 0.3 * 0.08],[0,0])
    bola3.set_model(ball3)

    ball4 = sg.findNode(ballsNode, "ball4")
    shadow4 = sg.findNode(shadows, "Shadow4")
    bola4 = poolBall(0.04, rest, fric,[-0.9*0.08,-0.4*0.08],[0,0])
    bola4.set_model(ball4)

    ball5 = sg.findNode(ballsNode, "ball5")
    shadow5 = sg.findNode(shadows, "Shadow5")
    bola5 = poolBall(0.04, rest, fric,[-0.9*0.08, 0],[0,0])
    bola5.set_model(ball5)

    ball6 = sg.findNode(ballsNode, "ball6")
    shadow6 = sg.findNode(shadows, "Shadow6")
    bola6 = poolBall(0.04, rest, fric,[-0.9*0.08, 0.4*0.08],[0,0])
    bola6.set_model(ball6)

    ball7 = sg.findNode(ballsNode, "ball7")
    shadow7 = sg.findNode(shadows, "Shadow7")
    bola7 = poolBall(0.04, rest, fric,[-1.4*0.08,-0.7*0.08],[0,0])
    bola7.set_model(ball7)

    ball8 = sg.findNode(ballsNode, "ball8")
    shadow8 = sg.findNode(shadows, "Shadow8")
    bola8 = poolBall(0.04, rest, fric,[-1.4*0.08,-0.25*0.08],[0,0])
    bola8.set_model(ball8)

    ball9 = sg.findNode(ballsNode, "ball9")
    shadow9 = sg.findNode(shadows, "Shadow9")
    bola9 = poolBall(0.04, rest, fric,[-1.4*0.08, 0.25*0.08],[0,0])
    bola9.set_model(ball9)

    ball10 = sg.findNode(ballsNode, "ball10")
    shadow10 = sg.findNode(shadows, "Shadow10")
    bola10 = poolBall(0.04, rest, fric,[-1.4*0.08, 0.7*0.08],[0,0])
    bola10.set_model(ball10)

    bolaBlanca = poolBall(0.4, rest, fric, [0, 0], [0, 0])
    bolaBlanca.set_model(whiteBallNode)
    bolaBlanca.set_controller(controller)

    mainShadow = sg.findNode(shadows, "ShadowMain")

    score1Node = sg.findNode(score, "Score 1")
    score1 = scoreHole(0.1)
    score1.set_model(score1Node)
    score2Node = sg.findNode(score, "Score 2")
    score2 = scoreHole(0.1)
    score2.set_model(score2Node)
    score3Node = sg.findNode(score, "Score 3")
    score3 = scoreHole(0.1)
    score3.set_model(score3Node)
    score4Node = sg.findNode(score, "Score 4")
    score4 = scoreHole(0.1)
    score4.set_model(score4Node)
    score5Node = sg.findNode(score, "Score 5")
    score5 = scoreHole(0.1)
    score5.set_model(score5Node)
    score6Node = sg.findNode(score, "Score 6")
    score6 = scoreHole(0.1)
    score6.set_model(score6Node)

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()
        theta = np.sin(3.0 * glfw.get_time())
        delta = t1 -t0
        selta = t1-s
        t0 = t1
        
        #impl.process_inputs()
        # Using GLFW to check for input events
        glfw.poll_events()

        controller.update_camera(delta)
        camera = controller.get_camera()
        viewMatrix = camera.update_view(0.5, 0)
        if controller.topView:
            viewMatrix = camera.upperView()

        # Setting up the projection transform
        projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if (controller.slowMotion):
            sleep(0.03)

        if (controller.autoCameraView):
            viewMatrix = camera.update_autoview()

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
            #glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE,
             tr.matmul([tr.translate(0, -2.3, 0),tr.rotationX(np.pi/2), tr.uniformScale(0.5)])) # tr.identity
            #mvpPipeline.drawCall(gpuAxis, GL_LINES)
            mvpPipeline.drawCall(gpuHanger, GL_LINES)

        glUseProgram(mvpPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        # las traslaciones son la posicion original (o actual) por el escalado del nodo de las bolas -> 0.08
        shadow1.transform = tr.matmul([tr.translate(0,0,-0.935),tr.uniformScale(0.04)])
        shadow2.transform = tr.matmul([tr.translate(-0.4 * 0.08,-0.3 * 0.08,-0.935),tr.uniformScale(0.04)])
        shadow3.transform = tr.matmul([tr.translate(-0.4 * 0.08,0.3 * 0.08,-0.935),tr.uniformScale(0.04)])
        shadow4.transform = tr.matmul([tr.translate(-0.9*0.08,-0.4*0.08,-0.935),tr.uniformScale(0.04)])
        shadow5.transform = tr.matmul([tr.translate(-0.9*0.08,0,-0.935),tr.uniformScale(0.04)])
        shadow6.transform = tr.matmul([tr.translate(-0.9*0.08,0.4*0.08,-0.935),tr.uniformScale(0.04)])
        shadow7.transform = tr.matmul([tr.translate(-1.4*0.08,-0.7*0.08,-0.935),tr.uniformScale(0.04)])
        shadow8.transform = tr.matmul([tr.translate(-1.4*0.08,-0.25*0.08,-0.935),tr.uniformScale(0.04)])
        shadow9.transform = tr.matmul([tr.translate(-1.4*0.08,0.25*0.08,-0.935),tr.uniformScale(0.04)])
        shadow10.transform = tr.matmul([tr.translate(-1.4*0.08,0.7* 0.08,-0.935),tr.uniformScale(0.04)])
        mainShadow.transform = tr.matmul([tr.translate(bolaBlanca.position[0], bolaBlanca.position[1], 0),tr.translate(0.5,0,-0.945),tr.uniformScale(0.04)])
        sg.drawSceneGraphNode(shadows, mvpPipeline, "model")
        sg.drawSceneGraphNode(score, mvpPipeline, "model")
        
        glUseProgram(shadowPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(shadowPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(shadowPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(shadowPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        lightingPipeline = phongPipeline
        lightingPipeline2 = phongPipeline2
        texPipeline = CSphongTexPipeline
        lightposition = [0, 0, locationZ]

        if controller.lightingModel == LIGHT_CEL_SHADING:
            lightingPipeline = phongPipeline
            texPipeline = CSphongTexPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            lightingPipeline = phongPipeline3
            texPipeline = phongTexPipeline
        if controller.fourTones == True:
            lightingPipeline = CSphongTexPipeline2
        if controller.spotLight == True:
            lightingPipeline = CSspotlightPipeline
            glUseProgram(lightingPipeline.shaderProgram)
            glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "concentrationP"), 100.0)
            glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "spotDirR"), 0.0, 0.0, -3.0)

        # Setting all uniform shader variables
        
        glUseProgram(lightingPipeline.shaderProgram)

        palitoNode.transform = tr.matmul([tr.translate(0.5,0,0),tr.rotationZ(camera.theta)])
        # White light in all components: ambient, diffuse and specular.
        if selta > 0.75:
            if var%3 == 0:
                aux_r = 0.7
                aux_g = 0.7
                aux_b = 0.7
            if var%3 == 1:
                aux_r = 0.7
                aux_g = 0.7
                aux_b = 0.7
            if var%3 == 2:
                aux_r = 0.4
                aux_g = 0.4
                aux_b = 0.4
            var += 1
            s=t1

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 0.3, 0.3, 0.3)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), lightposition[0], lightposition[1], lightposition[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), int(shininess))
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), cte_at)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), lnr_at)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), qud_at)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        # Drawing
        sg.drawSceneGraphNode(scene, lightingPipeline, "model")
        sg.drawSceneGraphNode(palitoNode, lightingPipeline, "model")
        sg.drawSceneGraphNode(table, lightingPipeline, "model")
        sg.drawSceneGraphNode(whiteBallNode, lightingPipeline, "model")
        
        
        glUseProgram(texPipeline.shaderProgram)

        if controller.hit and bolaBlanca.detenida:
            bolaBlanca.detenida = False
            bolaBlanca.velocity = [-2 * np.cos(camera.theta), -2 * np.sin(camera.theta)]
            print(bolaBlanca.velocity)
        
        bolaBlanca.action(delta)
        bolaBlanca.borderCollide()

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "lightPosition"), lightposition[0], lightposition[1], lightposition[2])
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(texPipeline.shaderProgram, "shininess"), int(shininess))

        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "constantAttenuation"), cte_at)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "linearAttenuation"), lnr_at)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "quadraticAttenuation"), qud_at)
        
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Kd"), 0.8, 0.8, 0.8)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        #sg.drawSceneGraphNode(toraxNode, texPipeline, "model")
        sg.drawSceneGraphNode(screenNode, texPipeline, "model")
        sg.drawSceneGraphNode(screen2Node, texPipeline, "model")
        sg.drawSceneGraphNode(ballsNode, texPipeline, "model")

        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        sg.drawSceneGraphNode(torusNode, texPipeline, "model")
        
        glUseProgram(CSspotlightPipeline.shaderProgram)
        # Light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        # Object is barely visible at only ambient. Diffuse behavior is slightly grey. Sparkles are white
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "Ka"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "Ks"), 0.8, 0.8, 0.8)

        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "lightPosition"), lightposition[0], lightposition[1], lightposition[2])
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "shininess"), int(shininess))
        
        glUniform1f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "constantAttenuation"), cte_at)
        glUniform1f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "linearAttenuation"), lnr_at)
        glUniform1f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "quadraticAttenuation"), qud_at)
        glUniform1f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "concentrationP"), 100.0)
        glUniform3f(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "spotDirR"), 0.0, 0.0, -3.0)

        glUniformMatrix4fv(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(CSspotlightPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        #sg.drawSceneGraphNode(testNode, CSspotlightPipeline, "model")

        glUseProgram(pipeline1.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "Ka"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "Ks"), 0.9, 0.9, 0.9)

        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "lightPosition"), lightposition[0], lightposition[1], lightposition[2])
        glUniform3f(glGetUniformLocation(pipeline1.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(pipeline1.shaderProgram, "shininess"), int(shininess))
        
        glUniform1f(glGetUniformLocation(pipeline1.shaderProgram, "constantAttenuation"), cte_at)
        glUniform1f(glGetUniformLocation(pipeline1.shaderProgram, "linearAttenuation"), lnr_at)
        glUniform1f(glGetUniformLocation(pipeline1.shaderProgram, "quadraticAttenuation"), qud_at)

        glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(sphereNodeLoc, pipeline1,"model")
        
        # Drawing the imgui texture over our drawing
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #impl.render(imgui.get_draw_data())

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuAxis.clear()
    #impl.shutdown()
    scene.clear()
    #cube1.clear()
    #cube2.clear()
    screenNode.clear()
    screen2Node.clear()
    torusNode.clear()
    dababy.clear()
    sphereNode.clear()

    glfw.terminate()