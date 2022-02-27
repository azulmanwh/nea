from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
from random import randint

class ChunkChecker():

    def __init__(self, path):
        self.__path = str(path)

    def hasBeenGenerated(self, chunkCoords):
        #Will check the file of the world save (ChunkData.txt) if the coordinates passed to it exist in the file. And therefore if the chunk has been generated there before.
        file = open(self.__path, 'r')
        data = file.readlines()
        for line in data:
            x = line.split(";")[0].split(",")[0] #returns the x coordinate of a bit of chunk data from file
            y = line.split(";")[0].split(",")[1] #returns the y coordinate
            if((chunkCoords.getX() == int(x)) and (chunkCoords.getY() == int(y))):
                file.close()
                return True
        file.close()
        return False


class ChunkLocator():

    def __init__(self, player, path):
        self.__player = player
        self.__path = path

    def locate(self, coords):
        x = round((coords.getX()-5) / 10)
        y = round((coords.getZ()-5) / 10)
        return ChunkCoords(x, y)

    def getData(self, chunkCoords):
        file = open("ChunkData.txt", 'r')
        data = file.readlines()
        for line in data:
            split_line = line.split(";")
            chunkData = split_line[1]
            coords = ChunkCoords(int(split_line[0].split(",")[0]), int(split_line[0].split(",")[1]))
            if(coords == chunkCoords):
                file.close()
                return chunkData
        file.close()
        raise NameError("Chunk not found in file!")

class ChunkSaver():

    def __init__(self, path, locator):
        self.__path = path
        self.__locator = locator

    def saveChunkData(self, chunkCoords, data):
        """
        Chunk data is stored as the chunk coordinates of the chunk and then the y values of each block
        stored as comma separated values. The chunk coordinates in the beginning are comma separated as well
        the chunk coordinates and block coordinates are separated by a semicolon.
        Example-->
        -1,1;2,2,2,2,2,2,1,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,0,1,1,2,1,1,1,0,0,0,0,1,2,2,2,1,1,0,0,0,1,2,2,3,2,2,1,0,-1
        
        """
        yCoordinates = data
        file = open(self.__path, 'a')
        try:
            line = str(chunkCoords.getX()) + "," + str(chunkCoords.getY()) + ";"
            for coordinate in yCoordinates:
                line += str(coordinate) + ","
            file.write(line + "\n")
        finally:
            file.close()

class ChunkGenerator():

    def __init__(self, checker, noises, saver, locator):
        self.__checker = checker
        self.__noises = noises
        self.__locator = locator
        self.saver = saver

    def generate(self, coordinates):
        #All the terrain lines of code increase the fps of the program  by about 100.
        #the terrain lines of code stop the individual access of blocks
        if(self.__checker.hasBeenGenerated(coordinates)):
            return(self.load(coordinates))
        else:
            ycoordinates = []
            #topterrain = Entity(model=None, collider=None)
            #underterrain = Entity(model=None, collider=None)
            chunkData = ChunkData(coordinates, [])
            depth = 4 #how many blocks are rendered underneath the top block
            #pixel will be the coordinate of the noise for the block, which needs to be adjusted as the coordinates are chunk coordinates
            pixelX = coordinates.getX()*10
            pixelY = coordinates.getY()*10
            heightScale = 30 #how high the blocks will spawn multiplier
            res = 500 #"width" of the noisemap
            for z in range(10):
                for x in range(10):
                    #instantiates a block at the location
                    #the noise refers to a float which will be the height of the block
                    #saving to chunkData allows for the blocks to be changed after being instantiated
                    #saving to ycoordinates so that the chunkdata can be saved
                    y_value = round(self.__noises[0]([(pixelX + x)/res, (pixelY + z)/res])*heightScale)
                    y_value += round(0.5 * self.__noises[1]([(pixelX + x)/res, (pixelY + z)/res])*heightScale)
                    y_value += round(0.25 * self.__noises[2]([(pixelX + x)/res, (pixelY + z)/res])*heightScale)
                    y_value += round(0.125 * self.__noises[3]([(pixelX + x)/res, (pixelY + z)/res])*heightScale)
                    topblock = Block(position = (pixelX + x, y_value, pixelY + z), type = 'grass')
                    #topblock.parent = topterrain
                    chunkData.addBlock(topblock)
                    for i in range(1,depth):
                        block = Block(position = (pixelX + x, y_value-i, pixelY + z), type = 'dirt')
                        #block.parent = underterrain
                        chunkData.addBlock(block)
                    ycoordinates.append(y_value)
            #topterrain.combine()
            #topterrain.texture = './Textures/grass.png'
            #underterrain.combine()
            #underterrain.texture = './Textures/stone.png'
            self.saver.saveChunkData(coordinates, ycoordinates)
            return chunkData

    def load(self, coordinates):
        topterrain = Entity(model=None, collider=None)
        underterrain = Entity(model=None, collider=None)
        pixelX = coordinates.getX()*10
        pixelY = coordinates.getY()*10
        depth = 4
        y_coordinates = str(self.__locator.getData(coordinates)).split(",")
        chunkData = ChunkData(coordinates, [])
        i = 0
        for z in range(10):
            for x in range(10):
                y_value = int(y_coordinates[i])
                topblock = Block(position = (pixelX + x, y_value, pixelY + z), type = 'grass')
                #topblock.parent = topterrain
                chunkData.addBlock(topblock)
                for j in range(1,depth):
                        block = Block(position = (pixelX + x, y_value-j, pixelY + z), type = 'dirt')
                        #block.parent = underterrain
                        chunkData.addBlock(block)
                i += 1
        #topterrain.combine()
        #topterrain.texture = './Textures/grass.png'
        #underterrain.combine()
        #underterrain.texture = './Textures/stone.png'
        return chunkData


class Block(Entity):

    blockType = { 
        'stone': 0,
        'dirt': 1,
        'grass': 2
    }

    blockTypeTextures = {
        'stone': './Textures/stone.png',
        'dirt': './Textures/dirt.png',
        'grass': './Textures/grass.png'
    }

    def __init__(self, position = (0,0,0), type = 'stone'):
        super().__init__(
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = self.blockTypeTextures.get(type),
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

    def getDistance(chunk1, chunk2):
        return (math.sqrt(((chunk2.getX() - chunk1.getX()) ** 2) + ((chunk2.getY() - chunk1.getY()) ** 2)))

    def getPossibleCoords(currentChunkCoords, r):
        #r = radius
        #this function will generate a "circle" of possible chunk coordinates around a given chunk coordinate
        #this function is used to know which chunks could be generated at at a given time
        coords = []
        for y in range(-r, r+1):
            for x in range(-r, r+1):
                coords.append(ChunkCoords(currentChunkCoords.getX()+x, currentChunkCoords.getY()+y))
        return coords
        

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
        return True if self.currentChunk != self.previousChunkCoords else False

    def changeCoords(self, newCoords):
        self.previousUserCoords = self.userCoords
        self.userCoords = newCoords

    def changeChunkCoords(self, newCoords):
        self.previousChunkCoords = self.currentChunk
        self.currentChunk = newCoords

class Game():

    def __init__(self, player, noises):
        self.player = player
        self.noises = noises
        self.locator = ChunkLocator(player, "ChunkData.txt")
        self.movementHandler = MovementHandler(ChunkLocator(player, "ChunkData.txt")) # Initiates movement handler.
        self.generator = ChunkGenerator(ChunkChecker("ChunkData.txt"), noises, ChunkSaver("ChunkData.txt", self.locator), self.locator)
        self.chunkDataList = []
        self.__renderDistance = 5

    def start(self):
        #creates starting chunk for the player to see
        self.chunkDataList.append(self.generator.generate(self.movementHandler.currentChunk))
        self.updateChunks()
    def update(self):
        self.culling()
        self.updateCoords()
        if(self.movementHandler.chunkChanged()):
            self.updateChunks()
        

        self.handle_input()

    def updateChunks(self):
        #creates chunks in a 3x3 grid around the player
        currentChunk = self.movementHandler.currentChunk
        x = currentChunk.getX()
        y = currentChunk.getY()

        # 0 1 2
        # 3 4 5
        # 6 7 8
        newChunks = []
        newChunks.append(ChunkCoords(x-1,y+1))
        newChunks.append(ChunkCoords(x,y+1))
        newChunks.append(ChunkCoords(x+1,y+1))
        newChunks.append(ChunkCoords(x-1, y))
        newChunks.append(ChunkCoords(x+1, y))
        newChunks.append(ChunkCoords(x-1, y-1))
        newChunks.append(ChunkCoords(x, y-1))
        newChunks.append(ChunkCoords(x+1, y-1))
       
        for i in range(len(self.chunkDataList)):
            if(self.chunkDataList[i].getCoords() in newChunks):
                newChunks.remove(self.chunkDataList[i].getCoords())
        for i in range(len(newChunks)):
            self.chunkDataList.append(self.generator.generate(newChunks[i]))

    def deleteChunk(self, index):
        #index refers to the index of the chunk in the chunkDataList array
        chunkDataObject = self.chunkDataList[index]
        for block in chunkDataObject.getBlocks():
            block.disable()
            del block
        del self.chunkDataList[index]

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
        elif(held_keys['l']):
            self.updateChunks()

    def culling(self):
        #identifies all non-visible entities (raycasting?)
        #disables entities if they are not already disabled
        pass


app = Ursina()

seed = 420
noises = []
noises.append(PerlinNoise(12,seed))
noises.append(PerlinNoise(6,seed))
noises.append(PerlinNoise(24,seed))
noises.append(PerlinNoise(3,seed))

game = Game(FirstPersonController(gravity=0), noises)
game.start()

#ursina functions can't make oop
def update():
    game.update()

def input(key):
    if(key == 'c'):
        game.deleteChunk(4)

app.run()
