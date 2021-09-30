from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

res = 100

class Block(Entity):
    def __init__(self, position = (0,0,0)):
        super().__init__(
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = './Textures/stone.png',
            color = color.gray
            )

def whatChunkAmIIn():
    #The -5 changes it from rounding to 10 when value is 5 do more accurately show where you are
    x = round((player.x-5) / 10)
    z = round((player.z-5) / 10)
    return (x,z)

def createChunk(coordinates, loadedChunks):
    if(coordinates not in set(loadedChunks)):
        pixelX = coordinates[0]*10
        pixelY = coordinates[1]*10
        for z in range(10):
            for x in range(10):
                Block(position = (pixelX + x, round(noise([(pixelX + x)/res, (pixelY + z)/res])*3), pixelY + z))
        loadedChunks.append(coordinates)

def handle_movement():
    #time.dt is the difference between a second and the frequency of the game being run so that the game speed is the same regardless of 
    #different FPS values
    if(held_keys['left shift']):
        player.y -= 3 * time.dt
    elif(held_keys['space']):
        player.y += 3 * time.dt

def toggleGravity():
    player.gravity = (1 if player.gravity == 0 else 0)

def input(key):
    if(key == 'escape'):
        quit()
    elif(key == 'g'):
        toggleGravity()



app = Ursina()

noise = PerlinNoise(octaves = 16)

#This creates the first chunk of the game.

player = FirstPersonController(gravity=0)
loadedChunks = []
createChunk((0,0), loadedChunks)

def update():
    currentChunk = whatChunkAmIIn()
    createChunk(currentChunk, loadedChunks)
    #Here another chunk will be created based on what chunk the player is in
    #but a check needs to be made for wether the chunk has already been loaded.
    #Maybe this value can be held in a list of tuples for loaded chunks.
    handle_movement()

app.run()