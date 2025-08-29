import pygame
from ..scr.GameFrame import game
from ..scr.GameFrame.basics import camera, player, shapes

win = game.Game(400, 400)
cam = camera.Camera(400, 400, "fixed")
player_obj = player.Player((0, 0), "playerSprite.png", cam)
rect = shapes.Rect((0, 0), (25, 25), "green")

win.show(player_obj)
win.show(rect)

#loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    player_obj.move_by_WSAD(2)

    win.update()