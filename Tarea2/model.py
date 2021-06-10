""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import random as rd
import grafica.transformations as tr

class articulation():
    def __init__(self, aCurve, aFinalTransform):
        self.curve = aCurve
        self.index = 0
        self.pos = self.curve[0]
        self.finalTransform = aFinalTransform

    def move(self):
        if self.index < len(self.curve) -4:
            self.index += 1
            self.pos = self.curve[self.index]
    
    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model
        self.transform = self.model.transform

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller
    
    def update(self):
        self.model.transform = tr.matmul([tr.rotationX(self.pos[1]),self.transform]) # self.transform

# tr.translate(self.finalTransform[0], self.finalTransform[1],self.finalTransform[2])