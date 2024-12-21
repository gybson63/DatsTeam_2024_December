import DataDef
import DataDef as gamedata
from typing import List

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Enemy:

    def __init__(self, data : DataDef.Enemy):
        self.points = []
        for pos in data.geometry:
            self.points.append(Point(pos.root[0], pos.root[1], pos.root[2]))
            #self.pos = Point(data.geometry[0], data.geometry[1], data.geometry[2])
        self.kills = data.kills

class Fence:
    def __init__(self, data_):
       data = data_.root
       self.pos = Point(data[0], data[1], data[2])


class Food:
    def __init__(self, data : DataDef.Food):
       self.pos = Point(data.c.geometry[0], data.c.geometry[1], data.c.geometry[2])
       self.points = data.points


class Snake:

    def __init__(self, data : DataDef.Snake):
        self.points = []
        for pos in data.geometry:
            self.points.append(Point(pos.root[0], pos.root[1], pos.root[2]))
            #self.pos = Point(data.geometry[0], data.geometry[1], data.geometry[2])
        self.status = data.status
        self.deathCount = data.deathCount
class GameState:

    def __init__(self, data):
        gs = gamedata.GameState.parse_obj(data)
        self.width = gs.mapSize[0]
        self.high = gs.mapSize[1]
        self.depth = gs.mapSize[2]

        self.enemies = []
        for enemy in gs.enemies:
            self.enemies.append(Enemy(enemy))

        self.fences = []
        for fence in gs.fences:
            self.fences.append(Fence(fence))

        self.foods = []
        for food in gs.foods:
            self.foods.append(Food(food))

        self.turn = data.turn
        self.time_to_end = gs.reviveTimeoutSec
        self.tickRemainMS = gs.tickRemainMs
        self.points = gs.points

        test = 1