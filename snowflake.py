import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np
from math import sqrt
import copy
import random
import time

root = sqrt(3)/2

alpha = 1
beta = 0.35
gamma = 0.001

colors = ['red', 'orange', 'yellow', 'green', 'blue']

class Cell:
    def __init__(self, pos, water):
        self.pos = pos
        self.water = water
        self.patch = None
    
    def getCartesian(self):
        x = 0.5 * (self.pos[0] - self.pos[1])
        y = root * (self.pos[2])
        return (x, y)

    def calcColor(self):
        if self.water < 0.25:
            return 'black'
        if self.water < 0.5:
            return 'darkblue'
        if self.water < 0.75:
            return 'blue'
        if self.water < 1:
            return 'lightsteelblue'
        if self.water >= 1:
            return 'ghostwhite'
        return 'red'

    def getShape(self):
        if self.patch is None:
            self.patch = RegularPolygon(self.getCartesian(), radius=0.5, numVertices=6, edgecolor='k', color=self.calcColor())
        else:
            self.patch.color = self.calcColor()
        return self.patch

    def isReceptive(self, grid):
        if (self.water >= 1):
            return True
        for cell in [grid[coord] for coord in self.getNeighbourCoordinates() if coord in grid]:
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
        neighbours = [diffuseGrid[coord] for coord in self.getNeighbourCoordinates() if coord in diffuseGrid]
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
        self.data[(0, 0, 0)].water = 1

    def step(self):
        # Diffusion map
        non_receptive = {}
        for cell in self.data.values():
            non_receptive[cell.pos] = cell.toDiffuseCell(self.data)
        diffusion = {}
        for cell in non_receptive.values():
            cell.calcLocalDiffusion(non_receptive, diffusion)
        
        # Receptive map
        receptive = {}
        for cell in self.data.values():
            receptive[cell.pos] = cell.toReceptiveCell(self.data)
        for cell in receptive.values():
            cell.addConstant()
        
        # Update all the values
        for cell in self.data.values():
            cell.water = receptive[cell.pos].water + diffusion[cell.pos].water

def drawGrid(grid):
    plt.axes()
    plt.gca().set_facecolor('lightgreen')
    for cell in grid.data.values():
        plt.gca().add_patch(cell.getShape())
    plt.axis('scaled')
    plt.show()

grid = HexGrid(50, beta, gamma)
iterations = 500
for i in range(1, iterations + 1):
    t = time.time()
    grid.step()
    print('{:.1%}'.format(i/iterations), time.time() - t)
drawGrid(grid)
input("Press Enter to close...")

