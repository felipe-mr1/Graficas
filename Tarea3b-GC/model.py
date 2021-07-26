""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import random as rd
import grafica.transformations as tr

def sentido(velocity):
    if velocity > 0:
        return -9.8
    else:
        return 9.8

def detenida(velocidadX, velocidadY):
    return velocidadX == 0 and velocidadY == 0

class poolBall():
    def __init__(self, aRadius, coefRestitucion, friccion, position, velocity):
        self.radius = aRadius
        self.gravityAceleration = 9.8
        self.coefRestitucion = coefRestitucion
        self.friccion = friccion
        self.position = position
        self.velocity = velocity
        self.model = None
        self.detenida = True

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model
        self.transform = self.model.transform

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def action(self, deltaTime):
        # Euler integration
        gravedad_0 = sentido(self.velocity[0])
        if abs(self.velocity[0]) > 0.1:
            self.velocity[0] += deltaTime * (gravedad_0 * self.friccion)
        else:
            self.velocity[0] = 0
        gravedad_1 = sentido(self.velocity[1])
        if abs(self.velocity[1]) > 0.1:
            self.velocity[1] += deltaTime * (gravedad_1 * self.friccion)
        else:
            self.velocity[1] = 0
        self.position[0] += self.velocity[0] * deltaTime
        self.position[1] += self.velocity[1] * deltaTime
        self.model.transform = tr.matmul([tr.translate(self.position[0], self.position[1], 0), self.transform])
        self.detenida = detenida(self.velocity[0], self.velocity[1])
        #self.model.transform = tr.matmul([self.transform])
        #print(self.velocity[0])

    def borderCollide(self):
        if self.position[0] + self.radius < -1.0:
            self.velocity[0] = abs(self.velocity[0] * self.coefRestitucion)

        if self.position[0]  > 1.0 + self.radius:
            self.velocity[0] = -abs(self.velocity[0] * self.coefRestitucion)

        if self.position[1] + self.radius < -0.05:
            self.velocity[1] = abs(self.velocity[1] * self.coefRestitucion)

        if self.position[1]  > 0.05 + self.radius:
            self.velocity[1] = -abs(self.velocity[1] * self.coefRestitucion)

class scoreHole():
    def __init__(self, aRadius):
        self.radius = aRadius

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model
        self.transform = self.model.transform

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller
