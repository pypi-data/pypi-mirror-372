import pygame

class Rect:
    def __init__(self, pos, dim, color, width=0):
        self.pos = pos
        self.color = color
        self.width = width
        self.rect = pygame.rect.Rect(pos, dim)
    def display(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, self.width)
    def move(self, x, y, add=True):
        if add:
            self.pos.x+=x
            self.pos.y+=y
        else:
            self.pos = x, y
        self.rect.move(self.pos)
    def resize(self, width, height):
        self.rect.size = width, height
    def change_color(self, color):
        self.color = color

class Text:
    def __init__(self, text, pos, size, color="black"):
        self.font = pygame.font.Font(None, size)
        self.textSurf = self.font.render(text, False, color)
        self.pos = pos

    def display(self, screen):
        screen.blit(self.textSurf, self.pos)