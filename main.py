from perlin_noise import PerlinNoise
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

res = 100

'''
'''



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

# class ChunkLoader():

#     def __init__(self, path):
#         self.__path = path

#     def load(self, chunkCoords):
#         data = ChunkLocator.getData(chunkCoords)
        


class ChunkGenerator():

    def __init__(self, checker, noise, saver):
        self.__checker = checker
        self.__noise = noise
        self.saver = saver

    def generate(self, coordinates):
        ycoordinates = []
        pixelX = coordinates.getX()*10
        pixelY = coordinates.getY()*10
        for z in range(10):
            for x in range(10):
                Block(position = (pixelX + x, round(self.__noise([(pixelX + x)/res, (pixelY + z)/res])*3), pixelY + z))
                ycoordinates.append(round(self.__noise([(pixelX + x)/res, (pixelY + z)/res])*3))
        self.saver.saveChunkData(coordinates, ycoordinates)

class Block(Entity):

    def __init__(self, position = (0,0,0)):
        super().__init__(
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = './Textures/stone.png',
            color = color.gray
            )

class ChunkCoords():

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

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
        self.userCoords = UserCoords(0, 0)
        self.previousUserCoords = UserCoords(0, 0)

    def chunkChanged(self):
        if((self.__locator.locate(self.userCoords)) == (self.__locator.locate(self.previousUserCoords))):
            print(self.__locator.locate(self.userCoords))
            print(self.__locator.locate(self.previousUserCoords))
            return True

    def changedCoords(self, newCoords):
        self.previousUserCoords = self.userCoords
        self.userCoords = newCoords

class Game():

    def __init__(self, player, noise):
        self.player = player
        self.noise = noise
        self.locator = ChunkLocator(player, "ChunkData.txt")
        self.movementHandler = MovementHandler(ChunkLocator(player, "ChunkData.txt")) # Initiates movement handler.
        self.generator = ChunkGenerator(ChunkChecker("ChunkData.txt"), noise, ChunkSaver("ChunkData.txt", self.locator))

    def start(self):
        self.generator.generate(ChunkCoords(0, 0))
    def update(self):
        self.updateCoords()
        if(self.movementHandler.chunkChanged()):
            self.generator.generate(locator(movementHandler.userCoords))

        self.handle_input()

    def updateCoords(self):
        self.movementHandler.changedCoords(UserCoords(self.player.x, self.player.z))

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

def update():
    game.update()

app.run()
