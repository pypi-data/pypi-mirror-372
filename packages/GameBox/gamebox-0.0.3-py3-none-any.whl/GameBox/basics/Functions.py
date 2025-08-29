import pygame

def DisplayText(text, color, size, pos, screen):
    font = pygame.font.Font(None, size)
    textSurf = font.render(text, False, color)
    screen.blit(textSurf, pos)

def getTilePosInGrid(pos,  grid_size):
    x, y = pos
    return (x // grid_size, y // grid_size)