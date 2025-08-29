import pygame
import json
from .editor import Editor

class Tilemap:
    def __init__(self, tileSize, fileDim, image, camera, scale=1):
        # Scale tile size
        self.size = int(tileSize * scale)

        self.fileDim = fileDim
        self.images = {}
        self.currentLayer = "ground"
        self.layers = {
            "ground": []
        }
        self.camera = camera
        self.loadedImage = image
        self.isEditor = False
        self.scale = scale
        self.Tsize = tileSize

        # Load images (crop each tile)
        for y in range(fileDim[1]):
            for x in range(fileDim[0]):
                # Create a fresh surface for this tile
                surface = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
                # Define the rectangle area on the sheet
                rect = pygame.Rect(
                    x * tileSize,
                    y * tileSize,
                    tileSize,
                    tileSize
                )
                # Copy the correct tile into the new surface
                surface.blit(image, (0, 0), rect)
                # Store it in the images dictionary
                self.images[str([x, y])] = pygame.transform.scale(surface, (self.size, self.size))

    def Add_layer(self, name):
        self.layers[name] = []

    def display(self, screen):
        self.draw_tiles(screen)
        if self.isEditor:
            self.editor.update(self.camera)
            self.editor.display(screen, self.camera)


    def draw_tiles(self, screen):
        if self.isEditor:
            self.layers = self.editor.layers
        for layer in self.layers:
            for item in self.layers[layer]:
                tile, pos = item
                x = pos[0]*self.size
                x -= self.camera.pos[0]
                y = pos[1]*self.size
                y -= self.camera.pos[1]
                screen.blit(self.images[str(tile)], (x, y))
            

    def enable_editor(self, scren_width, screen_height):
        self.isEditor = True
        self.editor = Editor(self.size, self.loadedImage, (scren_width, screen_height), self.fileDim, self.images, self.layers, self.Tsize, self.currentLayer)


    def save_map(self, filepath):
        with open(filepath, "w") as file:
            json.dump(self.layers, file)

    def load_map(self, filepath):
        with open(filepath, "r") as file:
            data = json.load(file)
            self.layers = dict(data)
            self.currentLayer = "ground"

    def get_editor_status(self):
        return self.editor.active

        