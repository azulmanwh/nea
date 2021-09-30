from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

res = 60

class Block(Button):
    def __init__(self, position = (0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = './Textures/stone.png',
            color = color.gray,
            highlight_color = color.light_gray,
            collider = 'box'
            )

def whatChunkAmIIn():
    #The -5 changes it from rounding to 10 when value is 5 do more accurately show where you are
    x = round((player.x-5) / 10)
    z = round((player.z-5) / 10)
    return (x,z)

def createChunk(coordinates, loadedChunks, playerCoordinates):
    if(coordinates not in set(loadedChunks)):
        print(loadedChunks)
        for z in range(10):
            for x in range(10):
                y = noise([((coordinates[0]*10) + x)/res,((coordinates[1]*10) + z)/res])
                block = Block(position = ((coordinates[0]*10) + x,y*3,(coordinates[1]*10) + z))
        loadedChunks.append(coordinates)
    else:
        return

def handle_movement():
    #time.dt is the difference between a second and the frequency of the game being run so that the game speed is the same regardless of 
    #different FPS values
    if(held_keys['left shift']):
        player.y -= 3 * time.dt
    elif(held_keys['space']):
        player.y += 3 * time.dt

def toggleGravity():
    if(player.gravity == 0):
        player.gravity = 1
    else:
        player.gravity = 0

def input(key):
    if(key == 'escape'):
        quit()
    elif(key == 'g'):
        toggleGravity()



app = Ursina()

noise = PerlinNoise(octaves = 10)

#This creates the first chunk of the game.

player = FirstPersonController(gravity=0)
loadedChunks = []
createChunk((0,0), loadedChunks, (0,0))

chunkCoordinates = Text()

def update():
    currentChunk = whatChunkAmIIn()
    chunkCoordinates.text = str(currentChunk[0]) + str(currentChunk[1])
    createChunk(currentChunk, loadedChunks, (player.x, player.z))
    #Here another chunk will be created based on what chunk the player is in
    #but a check needs to be made for wether the chunk has already been loaded.
    #Maybe this value can be held in a list of tuples for loaded chunks.
    handle_movement()

app.run()