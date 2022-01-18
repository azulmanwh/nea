from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

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

    def __init__(self, checker, noise, saver, locator):
        self.__checker = checker
        self.__noise = noise
        self.__locator = locator
        self.saver = saver

    def generate(self, coordinates):
        terrain = Entity(model=None, collider=None)
        if(self.__checker.hasBeenGenerated(coordinates)):
            return(self.load(coordinates, terrain))
        else:
            ycoordinates = []
            chunkData = ChunkData(coordinates, [])
            #pixel will be the coordinate of the noise for the block, which needs to be adjusted as the coordinates are chunk coordinates
            pixelX = coordinates.getX()*10
            pixelY = coordinates.getY()*10
            heightScale = 20 #how high the blocks will spawn multiplier
            res = 200 #"width" of the noisemap
            for z in range(10):
                for x in range(10):
                    #instantiates a block at the location
                    #the noise refers to a float which will be the height of the block
                    #saving to chunkData allows for the blocks to be changed after being instantiated
                    #saving to ycoordinates so that the chunkdata can be saved
                    y_value = round(self.__noise([(pixelX + x)/res, (pixelY + z)/res])*heightScale)
                    block = Block(position = (pixelX + x, y_value, pixelY + z))
                    block.parent = terrain
                    chunkData.addBlock(block)
                    ycoordinates.append(y_value)
            terrain.combine()
            terrain.texture = './Textures/stone.png'
            self.saver.saveChunkData(coordinates, ycoordinates)
            return chunkData

    def load(self, coordinates, terrain):
        pixelX = coordinates.getX()*10
        pixelZ = coordinates.getY()*10
        y_coordinates = str(self.__locator.getData(coordinates)).split(",")
        chunkData = ChunkData(coordinates, [])
        i = 0
        for z in range(10):
            for x in range(10):
                y_value = int(y_coordinates[i])
                block = Block(position = (pixelX + x, y_value, pixelZ + z))
                block.parent = terrain
                chunkData.addBlock(block)
                i += 1
        terrain.combine()
        terrain.texture = './Textures/stone.png'
        return chunkData


class Block(Entity):

    def __init__(self, position = (0,0,0)):
        super().__init__(
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = './Textures/stone.png',
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
        return True if self.currentChunk != self.previousChunkCoords else False

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
        self.generator = ChunkGenerator(ChunkChecker("ChunkData.txt"), noise, ChunkSaver("ChunkData.txt", self.locator), self.locator)
        self.chunkDataList = []

    def start(self):
        #creates starting chunk for the player to see
        self.updateChunks()
    def update(self):
        self.updateCoords()
        if(self.movementHandler.chunkChanged()):
            self.updateChunks()

        self.handle_input()

    def updateChunks(self):
        #creates chunks in a 3x3 grid around the player

        currentChunk = self.movementHandler.currentChunk
        x = currentChunk.getX()
        y = currentChunk.getY()

        if(len(self.chunkDataList) != 0):
            for i in range(len(self.chunkDataList)-1,-1,-1):
                self.deleteChunk(i)

        #tl = top left, tc = top center, tr = top right etc.
        tl = ChunkCoords(x-1,y+1)
        tc = ChunkCoords(x,y+1)
        tr = ChunkCoords(x+1,y+1)
        cl = ChunkCoords(x-1, y)
        cr = ChunkCoords(x+1, y)
        bl = ChunkCoords(x-1, y-1)
        bc = ChunkCoords(x, y-1)
        br = ChunkCoords(x+1, y-1)
       

        #startTime = time.time()
        self.chunkDataList.append(self.generator.generate(tl))
        self.chunkDataList.append(self.generator.generate(tc))
        self.chunkDataList.append(self.generator.generate(tr))
        self.chunkDataList.append(self.generator.generate(cl))
        self.chunkDataList.append(self.generator.generate(currentChunk))
        self.chunkDataList.append(self.generator.generate(cr))
        self.chunkDataList.append(self.generator.generate(bl))
        self.chunkDataList.append(self.generator.generate(bc))
        self.chunkDataList.append(self.generator.generate(br))
        #endTime = time.time()

        #print(endTime - startTime)

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
            print("test")



app = Ursina()

game = Game(FirstPersonController(gravity=0), PerlinNoise(octaves = 16, seed = 1))
game.start()


#ursina functions can't make oop
def update():
    game.update()

def input(key):
    if(key == 'c'):
        game.deleteChunk(4)

app.run()
