from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

res = 100

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

def createChunk(coordinates):
    #Rewrite this to produce the chunk to go from 0,0 to 10,10 rather than -5,-5 to 5,5
    #This is so that I can pass a chunk coordinate and it will get generated there
    for z in range(coordinates[0]-5,coordinates[1]+5):
        for x in range(coordinates[0]-5,coordinates[1]+5):
            y = noise([x/res,z/res])
            print(y)
            block = Block(position = (x,y*5,z))

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
createChunk((0,0))

player = FirstPersonController(gravity=0)

def update():
    currentChunk = whatChunkAmIIn()
    #Here another chunk will be created based on what chunk the player is in
    #but a check needs to be made for wether the chunk has already been loaded.
    #Maybe this value can be held in a list of tuples for loaded chunks.
    handle_movement()

app.run()