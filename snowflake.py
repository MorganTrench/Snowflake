import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np
from math import sqrt
import copy

root = sqrt(3)/2

alpha = 1
beta = 0.1
gamma = 0.1


class Cell:
    def __init__(self, pos, water):
        self.pos = pos
        self.water = water
    
    def getCartesian(self):
        plotx = 0.5 * (self.pos[0] - self.pos[1])
        ploty = root * (self.pos[2])
        return (plotx, ploty)

    def isReceptive(self, grid):
        if (self.water >= 1):
            return True
        for cell in [grid[coord] for coord in self.getNeighbourCoordinates()]:
            if (cell.water >= 1):
                return True
        return False

    def getNeighbourCoordinates(self):
        # Neighbors along each cubic 'axis'
        neighbourCoords = [
            # X axis neighbours ±[0, -1, 1]
            (self.pos[0], self.pos[1] - 1, self.pos[2] + 1), (self.pos[0], self.pos[1] + 1, self.pos[2] - 1),
            # Y axis neighbours ±[1, 0, -1]
            (self.pos[0] + 1, self.pos[1], self.pos[2] - 1), (self.pos[0] - 1, self.pos[1], self.pos[2] + 1),
            # Z axis neighbours ±[-1, 1, 0]
            (self.pos[0] - 1, self.pos[1] + 1, self.pos[2]), (self.pos[0] + 1, self.pos[1] - 1, self.pos[2])
        ]
        return neighbourCoords
        # return [grid[coord] for coord in neighbourCoords]

    def toDiffuseCell(self, grid):
        if (not self.isReceptive(grid)):
            return Cell(self.pos, self.water)
        else:
            return Cell(self.pos, 0)
    
    def toReceptiveCell(self, grid):
        if (self.isReceptive(grid)):
            return Cell(self.pos, self.water)
        else:
            return Cell(self.pos, 0)
    
    def calcLocalDiffusion(self, diffuseGrid, newDiffuseGrid):
        neighbours = [diffuseGrid[coord] for coord in self.getNeighbourCoordinates()]
        newDiffuseGrid[self.pos] = Cell(self.pos, self.water + 0.5*(-self.water + sum(n.water for n in neighbours) / len(neighbours)))

    def addConstant(self):
        self.water += gamma


class HexGrid:
    def __init__(self, radius, beta, gamma):
        self.data = {}
        self.beta = beta
        self.gamma = gamma
        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):
                for z in range(-radius, radius+1):
                    if ((x + y + z) == 0):
                        self.data[(x, y, z)] = Cell((x, y, z), beta)

    def step(self, step):
        # Diffusion map
        non_receptive = {}
        for cell in self.data.values():
            non_receptive[cell.pos] = cell.toDiffuseCell()
        diffusion = {}
        for cell in non_receptive.values():
            cell.calcLocalDiffusion(non_receptive, diffusion)
        
        # Receptive map
        receptive = {}
        for cell in self.data.values():
            receptive[cell.pos] = cell.toReceptiveCell()
        for cell in receptive.values():
            cell.addConstant()
        
        # Update all the values
        for cell in self.data.values():
            cell.water = receptive[cell.pos].water + diffusion[cell.pos].water

def drawGrid(grid):
    plt.axes()
    for cell in grid.data.values():
        plotx = (cell.pos[0] - 0.5*cell.pos[1] - 0.5*cell.pos[2])
        ploty = np.sin(60) * (cell.pos[1] - cell.pos[2])
        hexagon = RegularPolygon(
            cell.getCartesian(), radius=0.5, numVertices=6, edgecolor='k')
        plt.gca().add_patch(hexagon)
    plt.axis('scaled')
    plt.show()


grid = HexGrid(5, beta, gamma)
drawGrid(grid)
input("Press Enter to close...")

