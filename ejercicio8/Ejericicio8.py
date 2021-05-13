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

import imgui
from imgui.integrations.glfw import GlfwRenderer

class PolarCamera:
    def __init__(self):
        self.center = np.array([0.0, 0.0, -0.5])
        self.theta = 0
        self.rho = 5
        self.eye = np.array([0.0, 0.0, 0.0])
        self.height = 0.5
        self.up = np.array([0, 0, 1])
        self.viewMatrix = None

    def set_theta(self, delta):
        self.theta = (self.theta + delta) % (np.pi * 2)

    def set_rho(self, delta):
        if ((self.rho + delta) > 0.1):
            self.rho += delta

    def update_view(self):
        self.eye[0] = self.rho * np.sin(self.theta) + self.center[0]
        self.eye[1] = self.rho * np.cos(self.theta) + self.center[1]
        self.eye[2] = self.height + self.center[2]

        viewMatrix = tr.lookAt(
            self.eye,
            self.center,
            self.up
        )
        return viewMatrix

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True

        self.is_up_pressed = False
        self.is_down_pressed = False
        self.is_left_pressed = False
        self.is_right_pressed = False

        self.polar_camera = PolarCamera()

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

    controller = Controller()
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

     # Different shader programs for different lighting strategies
    phongPipeline = ls.SimplePhongShaderProgram()
    phongPipeline2 = ls.SimplePhongShaderProgram()
    phongTexPipeline = ls.SimpleTexturePhongShaderProgram()

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
    cube1 = createCube1(phongPipeline)
    cube2 = createCube2(phongPipeline)
    sphere = createSphereNode(0.3, 0.3, 0.3, phongPipeline)
    tex_sphere = createTexSphereNode(phongTexPipeline)
    torus = createTorusNode(phongPipeline)
    torus2 = createTexTorusNode(phongTexPipeline, -0.1)
    torus3 = createTorusNode(phongPipeline2, 0.1)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()
    s = t0

    # initilize imgui context (see documentation)
    imgui.create_context()
    impl = GlfwRenderer(window)

    controller = Controller()
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
   

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()
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

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawCall(gpuAxis, GL_LINES)

        lightingPipeline = phongPipeline
        lightingPipeline2 = phongPipeline2
        #lightposition = [1*np.cos(t1), 1*np.sin(t1), 2.3]
        lightposition = [0, 0, locationZ]

        #r = np.abs(((0.5*t1+0.00) % 2)-1)
        #g = np.abs(((0.5*t1+0.33) % 2)-1)
        #b = np.abs(((0.5*t1+0.66) % 2)-1)

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
            #aux_r = (aux_r + 0.333)%1
            #aux_g = (aux_g + 0.333)%1
            #aux_b = (aux_b + 0.333)%1
            s=t1
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
        #sg.drawSceneGraphNode(cube1, lightingPipeline, "model")
        #sg.drawSceneGraphNode(cube2, lightingPipeline, "model")
        #sg.drawSceneGraphNode(sphere, lightingPipeline, "model")
        sg.drawSceneGraphNode(torus, lightingPipeline, "model")
        #sg.drawSceneGraphNode(torus2, lightingPipeline, "model")
        
        
        glUseProgram(phongTexPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "La"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ld"), aux_r, aux_g, aux_b)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ls"), aux_r, aux_g, aux_b)

        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "lightPosition"), lightposition[0], lightposition[1], lightposition[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(phongTexPipeline.shaderProgram, "shininess"), int(shininess))

        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "constantAttenuation"), cte_at)
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "linearAttenuation"), lnr_at)
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "quadraticAttenuation"), qud_at)
        
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        #sg.drawSceneGraphNode(tex_sphere, phongTexPipeline, "model")
        sg.drawSceneGraphNode(torus2, phongTexPipeline, "model")

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

        sg.drawSceneGraphNode(torus3, lightingPipeline2, "model")
        
        # Drawing the imgui texture over our drawing
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        impl.render(imgui.get_draw_data())

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuAxis.clear()
    impl.shutdown()
    scene.clear()
    cube1.clear()
    cube2.clear()

    glfw.terminate()