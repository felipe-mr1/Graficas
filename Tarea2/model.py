""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import random as rd
import grafica.transformations as tr

# class for each articulation
# works with the curves and model given
# in charge of the movement of each model
class articulation():
    def __init__(self, aSetOfCurves):
        self.curve = aSetOfCurves[0]
        self.index = 0
        self.pos = self.curve[0]
        self.j = 0
        self.setOfCurves = aSetOfCurves
        self.lastTransform = 0

    def move(self):
        if self.index < len(self.curve) -2:
            self.index += 1
            self.pos = self.curve[self.index]
        else:
            self.j += 1
            self.curve = self.setOfCurves[self.j % 4]
            self.index = 0
    
    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model
        self.transform = self.model.transform

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller
    
    def update(self):
        if self.j % 4 == 0:
            self.model.transform = tr.matmul([tr.rotationX(self.pos[1])]) # self.transform
            self.transform1 = tr.rotationX(self.pos[1])
        elif self.j % 4 == 1:
            self.model.transform = tr.matmul([tr.rotationY(self.pos[1]), self.transform1])
            self.transform2 = tr.matmul([tr.rotationY(self.pos[1]), self.transform1])
        elif self.j % 4 == 2:
            self.model.transform = tr.matmul([tr.rotationZ(self.pos[1]), self.transform2])
            self.transform3 = tr.matmul([tr.rotationZ(self.pos[1]), self.transform2])
        else: # self.j % 4 == 3
            self.model.transform = tr.matmul([tr.rotationX(self.pos[1])])

# tr.translate(self.finalTransform[0], self.finalTransform[1],self.finalTransform[2])