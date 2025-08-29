import pygame
from scr.GameFrame import game
from scr.GameFrame.basics import camera, player, shapes
from scr.GameFrame.tilemap import tilemap

width, height = 1800, 950
win = game.Game(width, height)
cam = camera.Camera(width, height, "dynamic")
player_obj = player.Player((500, 400), "tests\sprites\playerSprite.png", cam, 0.3)

image = pygame.image.load("tests\sprites\image.png")
map = tilemap.Tilemap(32, (13, 3), image, cam, 2)
map.load_map("SavedMap.json")
map.enable_editor(width, height)


win.show(map)
win.show(player_obj)



#loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            map.save_map("SavedMap.json")
            pygame.quit()
            quit()

    player_obj.move_by_WSAD(1)

    win.update()
