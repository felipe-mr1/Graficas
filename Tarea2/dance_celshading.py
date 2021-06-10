from curves import evalCurveBezier, evalCurveCR, evalCurveCR9, evalCurveHermite
import glfw
from OpenGL.GL import *
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
LIGHT_PHONG   = 1

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

    def update_view(self):
        # Un osho parametrizado:
        # x: self.rho *(np.cos(self.theta) / ((np.sin(self.theta)**2) + 1)) + self.center[0]
        # y: self.rho *((np.cos(self.theta) * np.sin(self.theta)) / ((np.sin(self.theta)**2)+ 1)) + self.center[1]

        # Cardioide
        # x: self.rho*(np.cos(self.theta)*(1 + np.cos(self.theta))) + 0.5
        # y: self.rho * (np.sin(self.theta)*(1 + np.cos(self.theta))) + 0.5
        self.eye[0] = self.rho *(np.cos(self.theta) / ((np.sin(self.theta)**2) + 1)) + self.center[0] #self.rho * np.sin(self.theta) + self.center[0]
        self.eye[1] = self.rho *(((np.cos(self.theta) * np.sin(self.theta)) / ((np.sin(self.theta)**2)+ 1))) + 1.0 #self.rho * np.cos(self.theta) + self.center[1]
        self.eye[2] = self.height + self.center[2]
        viewMatrix = tr.lookAt(
            self.eye,
            self.center,
            self.up
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
            self.center,
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

        self.actual_sprite = 1

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
                self.slowMotion = not self.slowMotion

        if key == glfw.KEY_2:
            if action == glfw.PRESS:
                self.autoCameraView = not self.autoCameraView

        if key == glfw.KEY_3:
            if action == glfw.PRESS:
                self.actual_sprite += 1

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
    title = "P0 - Scene"

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
        0, -0.8, -0.1,        # 5
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
    CSphongTexPipeline2 = sh.CelShadingTexturePhongShaderProgram2()
    phongTexPipeline = ls.SimpleTexturePhongShaderProgram()
    CSphongTexPipeline = sh.CelShadingTexturePhongShaderProgram()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(mvpPipeline, bs.createAxis(4))

    gpuRedCube = createGPUShape(phongPipeline, bs.createColorNormalsCube(1,0,0))

    scene = createScene(phongPipeline)
    
    # Puntos para la curvas
    curvepoints = [
        0, -np.pi/2,    # 0
        0.2, 0,         # 1
        0.4, np.pi/2,   # 2
        0.5, np.pi,     # 3
        0.6, np.pi/2,   # 4
        0.8, np.pi,     # 5
        1,0             # 6
    ]

    curvepoints2 = [
        0, 0,                # 0
        0.2, np.pi/2,        # 1
        0.4, np.pi * (0.75), # 2
        0.5, np.pi/2,        # 3
        0.6, np.pi * (0.75), # 4
        0.8, 0,              # 5
        1,0                  # 6
    ]

    curvepoints3 = [
        0, -np.pi/2,         # 0
        0.2, 0,              # 1
        0.4, -np.pi * (0.75),# 2
        0.5, -np.pi * (0.25),# 3
        0.6, -np.pi * (0.75),# 4
        0.8, -np.pi * (0.5), # 5
        1,0                  # 6
    ]
    # CTR
    curvepoints4 = [
        0, 0,                # 0
        0.2, 0,              # 1
        0.4, np.pi * (0.75), # 2
        0.5, np.pi * (0.25), # 3
        0.6, np.pi * (0.75), # 4
        0.8, np.pi * (0.5),  # 5
        1,0                  # 6
    ]

    curvepoints5 = [
        0, 0,                 # 0
        0.2, 0,               # 1
        0.4, -np.pi * (0.5),   # 2
        0.5, -np.pi * (0.25),  # 3
        0.6, 0,               # 4
        0.8, -np.pi * (0.5),   # 5
        1,0                   # 6
    ]

    curvepoints6 = [
        0, 0,                 # 0
        0.2, 0,               # 1
        0.4, np.pi * (0.5),   # 2
        0.5, np.pi * (0.25),  # 3
        0.6, 0,               # 4
        0.8, np.pi * (0.5),   # 5
        1,0                   # 6
    ]

    curvepoints7 = [
        0, 0,                 # 0
        0.2, np.pi/2,         # 1
        0.4, np.pi * (0.25),  # 2
        0.5, np.pi * (0.2),   # 3
        0.6, np.pi * (0.1),   # 4
        0.8, 0,               # 5
        1,0                   # 6
    ]

    curvepoints8 = [
        0, 0,                 # 0
        0.2, 0,               # 1
        0.4, np.pi * (0.5),   # 2
        0.5, np.pi * (0.0),   # 3
        0.6, np.pi * (0.5),   # 4
        0.8, np.pi * (0.25),  # 5
        1,0                   # 6
    ]

    bezierPoints = [
        0, 0,         # 0
        0.33, np.pi * 0.2,  # 1
        0.66, -np.pi* 0.2, # 2
        1, 0          # 3
    ]

    bezierPoints2 = [
        0, 0,         # 0
        0.33, np.pi * 0.25,  # 1
        0.66, -np.pi* 0.25, # 2
        1, 0          # 3
    ]

    hermitePoints = [
        0, 0,                # p1
        1, 0,                # p2
        0.947, 9.13 * np.pi, # t1
        1.243, 8.34 * np.pi  # t2
    ]

    # Curves of Splines de catmull rom
    curve1 = evalCurveCR(1800, curvepoints)
    curve2 = evalCurveCR(1800, curvepoints2)
    curve3 = evalCurveCR(1800, curvepoints3)
    curve4 = evalCurveCR(1800, curvepoints4)
    curve5 = evalCurveCR(1800, curvepoints5)
    curve6 = evalCurveCR(1800, curvepoints6)
    curve7 = evalCurveCR(900, curvepoints7)
    curve8 = evalCurveCR(900, curvepoints8)
    cameraCurve = evalCurveCR9(1800, cameraPoints)
    bezierCurve = evalCurveBezier(1800, bezierPoints)
    bezierCurve2 = evalCurveBezier(1800, bezierPoints2)
    hermiteCurve = evalCurveHermite(1800, hermitePoints)

    Torus = createTextureGPUShapeX(createTextureTorus(50), CSphongTexPipeline, 
    GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST, 'sprites/metal.png')
    torusNode = sg.SceneGraphNode("torus")
    torusNode.transform = tr.matmul([tr.translate(-2.0,-1.5,-2.0),tr.scale(0.5, 0.5, 2.0)])
    torusNode.childs = [Torus]

    shapeBaby = readOBJ('sprites/dababy.obj', (0.9, 0.6, 0.2))
    gpuBaby = createGPUShape(phongPipeline, shapeBaby)

    dababy = sg.SceneGraphNode("baby")
    dababy.transform = tr.matmul([tr.translate(0,0,0.0),tr.rotationZ(np.pi),tr.uniformScale(0.025)])
    dababy.childs = [gpuBaby]

    #body = createBodyScene(phongPipeline, dababy)
    body = createBodyScene2(phongPipeline, dababy)
    body.transform = tr.translate(0,-0.4,-0.4)

    sphereMesh = createSphereMesh(64,0,0,0)
    sphereMesh_vertices, sphereMesh_indices = get_vertexs_and_indexes(sphereMesh, [0.66,0.66,0.66])

    gpuSphere = es.GPUShape().initBuffers()
    pipeline1.setupVAO(gpuSphere)
    gpuSphere.fillBuffers(sphereMesh_vertices, sphereMesh_indices, GL_STATIC_DRAW)

    sphereNode = sg.SceneGraphNode("asd")
    sphereNode.childs = [gpuSphere]

    toraxShape = createTorax()
    gpuTorax = es.GPUShape().initBuffers()
    phongTexPipeline.setupVAO(gpuTorax)
    gpuTorax.texture = es.textureSimpleSetup("sprites/tux.png", GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    gpuTorax.fillBuffers(toraxShape.vertices, toraxShape.indices, GL_STATIC_DRAW)

    toraxNode = sg.SceneGraphNode("torax")
    toraxNode.transform = tr.matmul([tr.translate(0.0, -0.4, -0.4 - (0.4)),tr.rotationZ((3/2) *np.pi)]) # y,z -.4
    toraxNode.childs = [gpuTorax]

    screenShape = s3d.createTextureNormalsCube(2,2)
    gpuScreen = es.GPUShape().initBuffers() 
    CSphongTexPipeline.setupVAO(gpuScreen)
    gpuScreen.texture = es.textureSimpleSetup("sprites/something.png", GL_REPEAT, GL_REPEAT, GL_NEAREST_MIPMAP_LINEAR, GL_NEAREST)
    gpuScreen.fillBuffers(screenShape.vertices, screenShape.indices, GL_STATIC_DRAW)
    glGenerateMipmap(GL_TEXTURE_2D)

    screenNode = sg.SceneGraphNode("screen")
    screenNode.transform = tr.translate(-1.0, -2.9, 0)
    screenNode.childs = [gpuScreen]

    gpuScreen2 = copy.deepcopy(gpuScreen)
    CSphongTexPipeline.setupVAO(gpuScreen2)
    gpuScreen2.texture = es.textureSimpleSetup("sprites/metal.png", GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    gpuScreen2.fillBuffers(screenShape.vertices, screenShape.indices, GL_STATIC_DRAW)
    glGenerateMipmap(GL_TEXTURE_2D)

    screen2Node = sg.SceneGraphNode("screen")
    screen2Node.transform = tr.translate(1.0, -2.9, 0.0)
    screen2Node.childs = [gpuScreen2]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()
    s = t0

    # initilize imgui context (see documentation)
    imgui.create_context()
    impl = GlfwRenderer(window)

    
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
    aux_r = 0.6
    aux_g = 0.4
    aux_b = 0.5

    var = 0

    finalTransform = [0,-0.4, -0.4]

    setOfCurvesLA = [curve1,curve3, curve5 ,curve7]
    setOfCurvesRA = [curve1,curve4, curve6,curve7]
    setOfCurvesLFA = [curve2,curve3, curve5 ,curve7]
    setOfCurvesRFA = [curve2,curve4, curve6 ,curve7]
    setOfCurvesRL = [curve8, bezierCurve, bezierCurve2, curve7]

    leftArm = sg.findNode(body, "leftArmRot")
    leftArmArticulation = articulation(setOfCurvesLA)
    leftArmArticulation.set_model(leftArm)

    rightArm = sg.findNode(body, "rightArmRot")
    rightArmArticulation = articulation(setOfCurvesRA)
    rightArmArticulation.set_model(rightArm)

    leftForearm = sg.findNode(body, "leftForearmRot")
    leftForearmArticulation = articulation(setOfCurvesLFA)
    leftForearmArticulation.set_model(leftForearm)

    rightForearm = sg.findNode(body, "rightForearmRot")
    rightForearmArticulation = articulation(setOfCurvesRFA)
    rightForearmArticulation.set_model(rightForearm)
    
    rightLeg1 = sg.findNode(body, "rightLegRot")
    rightLegArticulation = articulation(setOfCurvesRL)
    rightLegArticulation.set_model(rightLeg1)

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()
        theta = np.sin(3.0 * glfw.get_time())
        delta = t1 -t0
        selta = t1-s
        t0 = t1

        
        impl.process_inputs()
        # Using GLFW to check for input events
        glfw.poll_events()

        controller.update_camera(delta)
        camera = controller.get_camera()
        viewMatrix = camera.update_view()

        # Setting up the projection transform
        projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

         # imgui function

        locationZ, la, ld, ls, cte_at, lnr_at, qud_at, shininess = \
            transformGuiOverlay(locationZ, la, ld, ls, cte_at, lnr_at, qud_at, shininess)

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
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawCall(gpuAxis, GL_LINES)

        lightingPipeline = phongPipeline
        lightingPipeline2 = phongPipeline2
        texPipeline = CSphongTexPipeline
        #lightposition = [1*np.cos(t1), 1*np.sin(t1), 2.3]
        lightposition = [0, 0, locationZ]

        if controller.lightingModel == LIGHT_CEL_SHADING:
            lightingPipeline = phongPipeline
            texPipeline = CSphongTexPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            lightingPipeline = phongPipeline3
            texPipeline = phongTexPipeline


        r = 1.0
        g = 1.0
        b = 1.0

        # Setting all uniform shader variables
        
        glUseProgram(lightingPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        if selta > 1:
            if var%3 == 0:
                aux_r = 0.4
                aux_g = 0.7
                aux_b = 0.4
            if var%3 == 1:
                aux_r = 0.4
                aux_g = 0.4
                aux_b = 0.7
            if var%3 == 2:
                aux_r = 0.7
                aux_g = 0.4
                aux_b = 0.4
            var += 1
            s=t1

        leftForearmArticulation.move()
        leftForearmArticulation.update()
        rightForearmArticulation.move()
        rightForearmArticulation.update()
        leftArmArticulation.move()
        leftArmArticulation.update()
        rightArmArticulation.move()
        rightArmArticulation.update()
        rightLegArticulation.move()
        rightLegArticulation.update()

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

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
        ### envio otras transformadas para mas brillo metalico
        sg.drawSceneGraphNode(body, lightingPipeline, "model")
        
        
        glUseProgram(texPipeline.shaderProgram)
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
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        sg.drawSceneGraphNode(toraxNode, texPipeline, "model")
        sg.drawSceneGraphNode(screenNode, texPipeline, "model")
        sg.drawSceneGraphNode(screen2Node, texPipeline, "model")

        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        sg.drawSceneGraphNode(torusNode, texPipeline, "model")

        glUseProgram(lightingPipeline2.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "Ka"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "Ks"), 0.8, 0.8, 0.8)

        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "lightPosition"), lightposition[0], lightposition[1], lightposition[2])
        glUniform3f(glGetUniformLocation(lightingPipeline2.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline2.shaderProgram, "shininess"), int(shininess))
        
        glUniform1f(glGetUniformLocation(lightingPipeline2.shaderProgram, "constantAttenuation"), cte_at)
        glUniform1f(glGetUniformLocation(lightingPipeline2.shaderProgram, "linearAttenuation"), lnr_at)
        glUniform1f(glGetUniformLocation(lightingPipeline2.shaderProgram, "quadraticAttenuation"), qud_at)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline2.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline2.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline2.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        #sg.drawSceneGraphNode(torus3, lightingPipeline2, "model")
        
        # Drawing the imgui texture over our drawing
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        impl.render(imgui.get_draw_data())

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuAxis.clear()
    impl.shutdown()
    scene.clear()
    #cube1.clear()
    #cube2.clear()
    screenNode.clear()
    screen2Node.clear()
    torusNode.clear()
    dababy.clear()
    sphereNode.clear()
    toraxNode.clear()

    glfw.terminate()