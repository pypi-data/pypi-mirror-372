import pygame
import math
from ..basics.Functions import DisplayText
from ..basics.Functions import getTilePosInGrid as getTilePos

class Editor:
    def __init__(self, tilesize, file, winDim, fileDim, imageDict, layers, size, currentLayer):
        print("""====INGAME EDITOR ENABLED, PRESS "e" TO USE====""")
        self.Tsize = tilesize
        self.image = file
        self.width = winDim[0]
        self.height = winDim[1]
        self.fileDim = fileDim
        self.images = imageDict
        self.layers = layers
        self.currentLayer = currentLayer

        self.active = False
        self.Constdis = {
            "title" : "TileMap Editor",
            "T_color" : "white",
            "T_size" : 50,
            "T_pos" : (self.width-(self.width/4)+40, self.height-(self.height/6)+40)
        }

        self.state = "standby"
        self.selectedTile = (0, 0)
        self.SelTileDict = [0, 0]
        self.DictPos = (0, 0)
        self.imageSize = size

        #self.space_pressed_last = False

    def update(self, cam):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_e] and not self.e_pressed_last:
            self.active = not self.active
        self.e_pressed_last = keys[pygame.K_e]
        if self.active:
            self.key_toggles(keys)
        else:
            self.resetStates()
        #erase tiles
        if pygame.mouse.get_pressed(3)[2] and self.active:
            mx, my = pygame.mouse.get_pos()
            # Convert mouse to world coordinates
            world_x = mx + cam.pos[0]
            world_y = my + cam.pos[1]
            # Snap to grid
            x, y = getTilePos((world_x, world_y), self.Tsize)
            # Remove any tile at that world grid position
            tiles = self.layers[self.currentLayer]
            tiles = [tile for tile in tiles if tile[1] != [x, y]]
            self.layers[self.currentLayer] = tiles


    def display(self, screen, cam):
        if self.active:
            self.basicUI(screen)
            if self.state == "picking":
                self.Picking(screen)
            if self.state == "paint":
                self.Paint(screen, cam)

    def Paint(self, screen, cam):
        mx, my = pygame.mouse.get_pos()
        # 1. Convert screen pos → world pos
        world_x = mx + cam.pos[0]
        world_y = my + cam.pos[1]
        # 2. Snap world pos → grid
        x, y = getTilePos((world_x, world_y), self.Tsize)
        # 3. Draw highlight (subtract camera for screen-space display)
        pygame.draw.rect(
            screen, "white",
            pygame.Rect(x*self.Tsize - cam.pos[0], y*self.Tsize - cam.pos[1], self.Tsize, self.Tsize),
            5
        )
        # 4. Place tile in world grid space
        if pygame.mouse.get_pressed(3)[0]:
            tiles = self.layers[self.currentLayer]
            tiles = [tile for tile in tiles if tile[1] != [x, y]]
            tiles.append([self.SelTileDict, [x, y]])
            self.layers[self.currentLayer] = tiles


    def Picking(self, screen):
        #display tileset / tile follow mouse
        screen.blit(self.image, (10, 10))
        x, y = pygame.mouse.get_pos()
        pos = getTilePos((int(x), int(y)), self.imageSize)   # (grid_x, grid_y)
        x = ((pos[0]) * self.imageSize)+10
        y = ((pos[1]) * self.imageSize)+10
        pygame.draw.rect(screen, "white", pygame.Rect((x, y), (self.imageSize, self.imageSize)), 2)
        #wait for selection
        X = int(pos[0])
        Y = int(pos[1])
        if pygame.mouse.get_pressed(3)[0] and X<self.fileDim[0] and Y<self.fileDim[1]:
            self.state = "paint"
            #get sellected tile
            self.selectedTile = self.images[str([X,Y])]
            self.SelTileDict = [X, Y]
        self.DF_DictPos(screen,pos[0], pos[1])

    def DF_DictPos(self, screen, x, y):
        DisplayText(str((x, y)), "green", 35, (self.width//2, self.height//2), screen)
        DisplayText(str(self.imageSize), "green", 35, (self.width//2, self.height//2-50), screen)

    def key_toggles(self, keys):
        #toggle
        if keys[pygame.K_TAB] and self.active:
            #pick tile
            self.state = "picking"
        if keys[pygame.K_ESCAPE] and self.state == "picking":
            self.state = "standby"
        elif keys[pygame.K_ESCAPE] and self.state == "paint":
            self.state = "picking"
        self.switchLayers(keys)

    def switchLayers(self, keys):
        if keys[pygame.K_SPACE] and not self.space_pressed_last:
            layer_names = list(self.layers.keys())
            idx = layer_names.index(self.currentLayer)
            self.currentLayer = layer_names[(idx + 1) % len(layer_names)]
        self.space_pressed_last = keys[pygame.K_SPACE]

    def resetStates(self):
        self.state = "standby"

    def basicUI(self, screen):
        #render rect / title text
        pygame.draw.rect(screen, (136, 148, 150), pygame.Rect(self.width-(self.width/4), self.height-(self.height/6), self.width-(self.width/4), self.height-(self.height/6)), 0, 25)
        data = self.Constdis
        DisplayText(data["title"], data["T_color"], data["T_size"], data["T_pos"], screen)
        DisplayText(f"State: {self.state}", "white", 35, (self.width-(self.width/4)+40, self.height-(self.height/6)+75), screen)
        DisplayText(f"Layer: {self.currentLayer}", "white", 35, (self.width-(self.width/4)+40, self.height-(self.height/6)+115), screen)
        #draw sellected tile
        if self.state == "paint":
            screen.blit(self.selectedTile, ((self.width-self.Tsize)-20, (self.height-self.Tsize)-20))