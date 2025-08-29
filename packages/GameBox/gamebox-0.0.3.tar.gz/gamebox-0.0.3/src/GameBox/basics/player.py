import pygame

class Player:
    def __init__(self, pos, spritePath, camera, scale = 1):
        self.pos = pos
        self.camera = camera
        self.sprite = pygame.transform.scale_by(pygame.image.load(spritePath), scale)

    def display(self, screen):
        screen.blit(self.sprite, self.pos)

    def update_position(self, UP_A):
        if self.camera.type == "fixed":
            x, y = self.pos
            x+=UP_A[0]
            y+=UP_A[1]
            self.pos = x, y
        elif self.camera.type == "dynamic":
            self.camera.move(UP_A[0], UP_A[1])

    def move_by_WSAD(self, speed):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Update player position based on key presses\
        x,y = self.pos
        if keys[pygame.K_a]:
            x -= -speed
        if keys[pygame.K_d]:
            x += -speed
        if keys[pygame.K_w]:
            y -= -speed
        if keys[pygame.K_s]:
            y += -speed

        new_x = self.pos[0]
        new_x-=x

        new_y = self.pos[1]
        new_y -= y

        self.update_position((new_x, new_y))

    def move_by_arrows(self, speed):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Update player position based on key presses\
        x,y = self.pos
        if keys[pygame.K_UP]:
            x -= -speed
        if keys[pygame.K_DOWN]:
            x += -speed
        if keys[pygame.K_LEFT]:
            y -= -speed
        if keys[pygame.K_RIGHT]:
            y += -speed

        new_x = self.pos[0]
        new_x-=x

        new_y = self.pos[1]
        new_y -= y

        self.update_position((new_x, new_y))