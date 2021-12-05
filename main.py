from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from abc import ABCMeta, abstractmethod

res = 100

"""
TO DO LIST:
-implement observer for chunk changing
-finish making 3x3 chunks generate arround player
"""
class ChunkChecker():

    def __init__(self, path):
        self.__path = str(path)

    def hasBeenGenerated(self, chunkCoords):
        #Will check the file of the world save (ChunkData.txt) if the coordinates passed to it exist in the file. And therefore if the chunk has been generated there before.
        file = open(self.__path, 'r')
        data = file.readlines()
        for line in data:
            x = line.split("|")[0].split(",")[0] #returns the x coordinate of a bit of chunk data from file
            y = line.split("|")[0].split(",")[1] #returns the y coordinate
            if((chunkCoords.getX() == x) and (chunkCoords.getY() == y)):
                return True
        return False


class ChunkLocator():

    def __init__(self, player, path):
        self.__player = player
        self.__path = path

    def locate(self, coords):
        x = round((coords.getX()-5) / 10)
        y = round((coords.getZ()-5) / 10)
        return ChunkCoords(x, y)

    def getData(chunkCoords):
        file = open("ChunkData.txt", 'r')
        data = file.readlines()
        for line in data:
            chunkData = line.split("|")[1]
            return chunkData

class ChunkSaver():

    def __init__(self, path, locator):
        self.__path = path
        self.__locator = locator

    def saveChunkData(self, chunkCoords, data):
        yCoordinates = data
        file = open(self.__path, 'a')
        try:
            line = str(chunkCoords.getX()) + "," + str(chunkCoords.getY()) + "| "
            for coordinate in yCoordinates:
                line += " " + str(coordinate)
            file.write(line + "\n")
        finally:
            file.close()

class ChunkGenerator():

    def __init__(self, checker, noise, saver):
        self.__checker = checker
        self.__noise = noise
        self.saver = saver

    def generate(self, coordinates):
        ycoordinates = []
        chunkData = ChunkData(coordinates)
        #pixel will be the coordinate of the noise for the block, which needs to be adjusted as the coordinates are chunk coordinates
        pixelX = coordinates.getX()*10
        pixelY = coordinates.getY()*10
        for z in range(10):
            for x in range(10):
                #instantiates a block at the location
                #the noise refers to a float which will be the height of the block
                #saving to chunkData allows for the blocks to be changed after being instantiated
                #saving to ycoordinates so that the chunkdata can be saved
                block = Block(position = (pixelX + x, round(self.__noise([(pixelX + x)/res, (pixelY + z)/res])*3), pixelY + z))
                chunkData.addBlock(block)
                ycoordinates.append(round(self.__noise([(pixelX + x)/res, (pixelY + z)/res])*3))
        self.saver.saveChunkData(coordinates, ycoordinates)
        return chunkData

class Block(Entity):

    def __init__(self, position = (0,0,0)):
        super().__init__(
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = './Textures/grass.png',
            color = color.white
            )

class ChunkData():

    def __init__(self, coords, blocks = []):
        #list of Block entities
        self.__blocks = blocks
        #chunk coords
        self.__coords = coords

    def getCoords(self):
        return self.__coords

    def getBlocks(self):
        return self.__blocks

    def addBlock(self, block):
        self.__blocks.append(block)


class ChunkCoords():

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def __eq__(self, other):
        if(isinstance(other, ChunkCoords)):
            return self.__x == other.getX() and self.__y == other.getY()
        return False

    def getX(self):
        return self.__x

    def getY(self):
        return self.__y

class UserCoords():

    def __init__(self, x, z):
        self.__x = x
        self.__z = z

    def getX(self):
        return self.__x

    def getZ(self):
        return self.__z

class MovementHandler():

    def __init__(self, locator):
        self.__locator = locator
        self.currentChunk = ChunkCoords(0, 0)
        self.previousChunkCoords = ChunkCoords(0, 0)
        self.userCoords = UserCoords(0, 0)
        self.previousUserCoords = UserCoords(0, 0)

    def chunkChanged(self):
        if(self.currentChunk != self.previousChunkCoords):
            print(str(self.currentChunk.getX()) + " " + str(self.currentChunk.getY()))
            print(str(self.previousChunkCoords.getX()) + " " + str(self.previousChunkCoords.getY()))
            return True
        return False

    def changeCoords(self, newCoords):
        self.previousUserCoords = self.userCoords
        self.userCoords = newCoords

    def changeChunkCoords(self, newCoords):
        self.previousChunkCoords = self.currentChunk
        self.currentChunk = newCoords

class Game():

    def __init__(self, player, noise):
        self.player = player
        self.noise = noise
        self.locator = ChunkLocator(player, "ChunkData.txt")
        self.movementHandler = MovementHandler(ChunkLocator(player, "ChunkData.txt")) # Initiates movement handler.
        self.generator = ChunkGenerator(ChunkChecker("ChunkData.txt"), noise, ChunkSaver("ChunkData.txt", self.locator))
        self.chunkData = []

    def start(self):
        #creates starting chunk for the player to see
        self.chunkData.append(self.generator.generate(ChunkCoords(0, 0)))
    def update(self):
        self.updateCoords()
        if(self.movementHandler.chunkChanged()):
            self.updateChunks()

        self.handle_input()

    def updateChunks(self):
        #creates chunks in a 3x3 grid around the player
        currentChunk = self.movementHandler.currentChunk
        self.chunkData.append(self.generator.generate(currentChunk))

    def deleteChunk(self):
        chunk = self.chunkData.pop()
        for block in chunk.getBlocks():
            block.enabled = False        

    def updateCoords(self):
        self.movementHandler.changeCoords(UserCoords(self.player.x, self.player.z))
        self.movementHandler.changeChunkCoords(self.locator.locate(UserCoords(self.player.x, self.player.z)))

    def handle_input(self):
        #time.dt is the difference between a second and the frequency of the game being run so that the game speed is the same regardless of 
        #different FPS values
        if(held_keys['left shift']):
            self.player.y -= 3 * time.dt
        elif(held_keys['space']):
            self.player.y += 3 * time.dt
        elif(held_keys['escape']):
            quit()
        elif(held_keys['g']):
            self.player.gravity = (1 if self.player.gravity == 0 else 0)



app = Ursina()

game = Game(FirstPersonController(gravity=0), PerlinNoise(octaves = 16, seed = 1))
game.start()


#ursina functions can't make oop
def update():
    game.update()

def input(key):
    if(key == 'c'):
        game.deleteChunk()

app.run()
