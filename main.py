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

    def saveChunkData(self, chunkData):
        #format of data being stored is as follows
        #{chunkCoordinate.X},{chunkCoordinate.Y};block1.x,block1.y,block1.z,block1.type:block2.x,block2.y,block2.z,block2.type: and so on
        #before the semi-colon are the chunk coordinates
        #after the semi-colon and inbetween each colon are 3 coordinates and the type
        #one for the x,y and z coordinates respectively and the last is the block type.
        blocks = chunkData.getBlocks()
        file = open(self.__path, 'a')
        try:
            line = str(chunkData.getCoords().getX()) + "," + str(chunkData.getCoords().getY()) + ";"
            for block in blocks:
                line += str(block.X) + "," + str(block.Y) + "," + str(block.Z) + "," + str(block.getType()) + ":"
            file.write(line + "\n")
        finally:
            file.close()

class ChunkGenerator():

    def __init__(self, checker, noises, saver, locator):
        self.checker = checker
        self.__noises = noises
        self.__locator = locator
        self.saver = saver

    def generate(self, coordinates):
        #All the terrain lines of code increase the fps of the program  by about 100.
        #the terrain lines of code stop the individual access of blocks
        if(self.checker.hasBeenGenerated(coordinates)):
            return(self.load(coordinates))
        else:
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
                    topblock = Block(coordinates, position = (pixelX + x, y_value, pixelY + z), blockType = 'dirt')
                    #topblock.parent = topterrain
                    chunkData.addBlock(topblock)
                    for i in range(1,depth):
                        block = Block(coordinates, position = (pixelX + x, y_value-i, pixelY + z), blockType = 'stone')
                        #block.parent = underterrain
                        chunkData.addBlock(block)
            #topterrain.combine()
            #topterrain.texture = './Textures/grass.png'
            #underterrain.combine()
            #underterrain.texture = './Textures/stone.png'
            self.saver.saveChunkData(chunkData)
            return chunkData

    def load(self, chunkCoords):
        chunkData = ChunkData(chunkCoords, [])
        for blockData in self.__locator.getData(chunkCoords).split(":"):
            data = blockData.split(",")
            if data[0] != '\n':
                block = Block(chunkCoords, position = (float(data[0]), float(data[1]), float(data[2])), blockType=data[3])
                chunkData.addBlock(block)
        return chunkData


class Block(Entity):

    blockType = { 
        'stone': 0,
        'dirt': 1,
        'cobble': 3
    }

    blockTypeTextures = {
        'stone': './Textures/stone.png',
        'dirt': './Textures/dirt.png',
        'cobble': './Textures/cobblestone.png'
    }

    def __init__(self, chunkCoords, position = (0,0,0), blockType = 'stone', ):
        super().__init__(
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = self.blockTypeTextures.get(blockType),
            color = color.white,
            collider = 'box'
            )
        self.blockType = blockType
        self.chunkCoordinates = chunkCoords

    def getType(self):
        return self.blockType

    def getChunkCoords(self):
        return self.chunkCoordinates

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

    def removeBlock(self, block):
        self.__blocks.remove(block)

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

    def save(self):
        for chunkData in self.chunkDataList:
            if(not self.generator.checker.hasBeenGenerated(chunkData.getCoords())):
                self.generator.saver.saveChunkData(chunkData)
            chunkDataFile = open("ChunkData.txt", "r")
            data = chunkDataFile.readlines()
            lineNumber = 0
            for i in range(len(data)):
                x = data[i].split(";")[0].split(",")[0] #returns the x coordinate of a bit of chunk data from file
                y = data[i].split(";")[0].split(",")[1] #returns the y coordinate
                if((chunkData.getCoords().getX() == int(x)) and (chunkData.getCoords().getY() == int(y))):
                    lineNumber = i
                    break
            data[lineNumber] = str(chunkData.getCoords().getX()) + "," + str(chunkData.getCoords().getY()) + ";"
            for block in chunkData.getBlocks():
                data[lineNumber] += str(block.X) + "," + str(block.Y) + "," + str(block.Z) + "," + str(block.getType()) + ":"
            data[lineNumber] = data[lineNumber] + "\n"
            chunkDataFile = open("ChunkData.txt", "w")
            chunkDataFile.writelines(data)
            chunkDataFile.close()

    def handle_input(self):
        #time.dt is the difference between a second and the frequency of the game being run so that the game speed is the same regardless of
        #different FPS values
        if(held_keys['left shift']):
            self.player.y -= 3 * time.dt
        elif(held_keys['space']):
            self.player.y += 3 * time.dt
        elif(held_keys['escape']):
            self.save()
            quit()
        elif(held_keys['g']):
            self.player.gravity = not self.player.gravity
        elif(held_keys['l']):
            self.updateChunks()

    def breakBlock(self):
        direction = camera.forward
        origin = self.player.world_position + Vec3(0,2,0)
        hit_info = raycast(origin, direction, ignore=(self.player,), distance=inf, traverse_target=scene, debug=False)
        if(hit_info.entities):
            block = hit_info.entities[0]
            block.disable()
            for chunkData in self.chunkDataList:
                if chunkData.getCoords() == block.getChunkCoords():
                    chunkData.removeBlock(block)
    def placeBlock(self):
        direction = camera.forward
        origin = self.player.world_position + Vec3(0,2,0)
        hit_info = raycast(origin, direction, ignore=(self.player,), distance=inf, traverse_target=scene, debug=False)
        if(hit_info.entities):
            surfaceBlock = hit_info.entities[0]
            for chunkData in self.chunkDataList:
                if chunkData.getCoords() == surfaceBlock.getChunkCoords():
                    block = Block(chunkData.getCoords(), position=(surfaceBlock.X, surfaceBlock.Y+1, surfaceBlock.Z), blockType='cobble')
                    chunkData.addBlock(block)


                


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
    if key == 'left mouse down':
        game.breakBlock()
    elif key == 'right mouse down':
        game.placeBlock()

app.run()
