""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import random as rd
import grafica.transformations as tr

class articulation():
    def __init__(self, aCurve):
        self.curve = aCurve
        self.index = 0

    def move(self):
        if self.index < range(self.curve) -4:
            self.index += 1