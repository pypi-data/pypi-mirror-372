import pygame

class Game:
    def __init__(self, width, height,  background_color = "black"):
        pygame.font.init()
        self.dim = width, height
        self.color = background_color
        self.objects = []
        self.screen = pygame.display.set_mode((width, height))


    def show(self, obj):
        self.objects.append(obj)

    def update(self):
        self.screen.fill(self.color)
        for obj in self.objects:
            obj.display(self.screen)
        pygame.display.update()