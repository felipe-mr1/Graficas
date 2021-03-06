""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import random as rd
import grafica.transformations as tr

class Player():
    # Clase que contiene al modelo del player / auro
    def __init__(self, size):
        self.pos = [0,-0.65] # Posicion en el escenario
        self.vel = [0.3,0.3] # Velocidad de desplazamiento
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.1 # distancia para realiozar los calculos de colision
        self.infected = 0.0 # atributo de infeccion
        self.zombie = 0 # atributo de estado

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model


    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller


    def update(self, delta, direction):
        # Se actualiza la posicion del auto
        # Si detecta la tecla [D] presionada se mueve hacia la derecha
        if self.controller.is_d_pressed and self.pos[0] < 0.6 and self.zombie==0:
            self.pos[0] += self.vel[0] * delta
        # Si detecta la tecla [A] presionada se mueve hacia la izquierda
        if self.controller.is_a_pressed and self.pos[0] > -0.6 and self.zombie==0:
            self.pos[0] -= self.vel[0] * delta
        # Si detecta la tecla [W] presionada y no se ha salido de la pista se mueve hacia arriba
        if self.controller.is_w_pressed and self.pos[1] < 0.85 and self.zombie==0:
            self.pos[1] += self.vel[1] * delta
        # Si detecta la tecla [S] presionada y no se ha salido de la pista se mueve hacia abajo
        if self.controller.is_s_pressed and self.pos[1] > -0.85 and self.zombie==0:
            self.pos[1] -= self.vel[1] * delta
        # Se le aplica la transformacion de traslado segun la posicion actual
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0), tr.scale(direction * self.size, self.size*2, 1)])

    def collision(self, cargas):
        # Funcion para detectar las colisiones con las cargas
        # Se recorren las cargas
        for carga in cargas:
            # si la distancia a la carga es menor que la suma de los radios ha ocurrido en la colision
            if (self.radio+carga.radio)**2 > ((self.pos[0]- carga.pos[0])**2 + (self.pos[1]-carga.pos[1])**2 ):
                if(carga.zombie==1):
                    self.zombie=1
                    #self.model = self.zmodel
                if carga.infected > 0:
                    self.infected = 1
                return
        

    def objective(self, aStore):
        if (self.radio+aStore.radio)**2 > ((self.pos[0]- aStore.pos[0])**2 + (self.pos[1]-aStore.pos[1])**2 ):
            return True
        else:
            return False
        
class Humanoid():

    # Clase para contener las caracteristicas de un objeto que representa un humanoide: estudiante/zombie

    def __init__(self, posx, posy, size, typeOfNpc, aName):
        self.pos = [posx, posy]
        self.radio = 0.12
        self.size = size
        self.model = None
        self.infected = (typeOfNpc + rd.randint(0, 1))/2
        self.zombie = typeOfNpc
        self.point1 = [posx, posy]
        self.point2 = [-0.65, rd.randint(10, 90)/100]
        self.point3 = [0.65, rd.randint(10, 90)/100]
        self.point4 = [rd.uniform(-0.55, 0.55), -1.1]
        self.t = 0.0
        self.name = aName
    
    def set_model(self, new_model):
        self.model = new_model


    def update(self):
        # Se posiciona el nodo referenciado
        if self.t < 1.1:
            self.pos[0] = ((1-(self.t))**3)*self.point1[0] + (self.t)*((1-(self.t))**2)*self.point2[0] + ((self.t)**2)*(1-(self.t))*self.point3[0] + ((self.t)**3)*self.point4[0]
            self.pos[1] = ((1-(self.t))**3)*self.point1[1] + (self.t)*((1-(self.t))**2)*self.point2[1] + ((self.t)**2)*(1-(self.t))*self.point3[1] + ((self.t)**3)*self.point4[1]
            self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0), tr.scale(self.size, self.size, 1)])

    def collision(self, cargas):
        for carga in cargas:
            if carga.name != self.name:
                if (self.radio+carga.radio)**2 > ((self.pos[0]- carga.pos[0])**2 + (self.pos[1]-carga.pos[1])**2 ):
                    if carga.infected > 0:
                        self.infected = 1
                    if carga.zombie == 1:
                        self.zombie = 1

class Store():
    # clase para representar al objetivo
    def __init__(self, posx, posy):
        self.pos = [posx, posy]
        self.radio = 0.3
        self.model = None

    def set_model(self, new_model):
        self.model = new_model
