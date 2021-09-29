import pygame
import os
from enum import Enum

WIDTH, HEIGHT = 1280, 700

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEAPrototype")

LIGHTBLUE = (0, 180, 255)

FPS = 144
SPEED = 3

PLAYER_TEXTURE = pygame.image.load(os.path.join('Textures', 'player.png'))
PLAYER = pygame.transform.scale(PLAYER_TEXTURE, (80, 150))
GRASS_TEXTURE = pygame.image.load(os.path.join('Textures', 'grass.png'))
STONE_TEXTURE = pygame.image.load(os.path.join('Textures', 'stone.png'))
DIRT_TEXTURE = pygame.image.load(os.path.join('Textures', 'dirt.png'))

class BlockType(Enum):
    GRASS = 1
    DIRT = 2
    STONE = 3

class Player:
    def __init__(self, position):
        self.position = position

class Block:
    def __init__(self, position, blockType, texture):
        self.position = position
        self.blockType = blockType
        self.texture = texture


def draw_window(playerPosition, grass):
    WIN.fill(LIGHTBLUE)
    WIN.blit(PLAYER, playerPosition)
    WIN.blit(grass.texture, grass.position)
    pygame.display.update()

def movement(keys_pressed, playerPosition):
    if(keys_pressed[pygame.K_w]):
        print("No jumping yet!")
    if(keys_pressed[pygame.K_a]):
        playerPosition[0] -= SPEED
    if(keys_pressed[pygame.K_s]):
        print("Not this either.")
    if(keys_pressed[pygame.K_d]):
        playerPosition[0] += SPEED 

def main():

    player1 = Player([640, 260])
    grass1 = Block([300, 300], BlockType.GRASS, GRASS_TEXTURE)
    
    clock = pygame.time.Clock()
    
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                run = False
                
        keys_pressed = pygame.key.get_pressed()
        movement(keys_pressed, player1.position)
        draw_window(player1.position, grass1)        
    pygame.quit()
    
if __name__ == "__main__":
    main()