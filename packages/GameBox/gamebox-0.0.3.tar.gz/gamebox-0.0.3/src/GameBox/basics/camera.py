import pygame

class Camera:
    def __init__(self, width, height, type = "dynamic"):
        """Camera type can be fixed or dynamic depending on your needs. Defaults to dynamic."""
        self.type = type
        self.dim = width, height
        self.pos = 0, 0

    def move(self, x, y):
        X, Y = self.pos
        X+=x
        Y+=y
        self.pos = X, Y