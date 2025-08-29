import pygame

class Input:
    def mouse_leftClick(self):
        return pygame.mouse.get_pressed(3)[0]
    def mouse_rightClick(self):
        return pygame.mouse.get_pressed(3)[2]
    def is_pressed(self, key):
        keys = pygame.key.get_pressed()
        look = f"pygame.K_{key}"
        return keys[look]
