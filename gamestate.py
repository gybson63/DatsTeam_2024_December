import DataDef
import DataDef as gamedata
from typing import List
import networkx as nx
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Время выполнения {func.__name__}: {end_time - start_time:.4f} секунд")
        return result
    #print(wrapper)
    return wrapper

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_tuple(self):
        return (self.x, self.y, self.z)

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
       self.pos = Point(data.c.root[0], data.c.root[1], data.c.root[2])
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
        for food in gs.food:
            self.foods.append(Food(food))

        self.snakes = []
        for snake in gs.snakes:
            self.snakes.append(Snake(snake))
        
        self.turn = gs.turn
        self.time_to_end = gs.reviveTimeoutSec
        self.tickRemainMS = gs.tickRemainMs
        self.points = gs.points

        self.make_grid()

    def get_snake(self, x, y, z):
        for snake in self.snakes:
            if snake.points[0].x == x and snake.points[0].y == y and snake.points[0].z == z:
                return snake

    @timing_decorator
    def get_obstacles(self):
        obstacles = []
        for fence in self.fences:
            obstacles.append(fence.pos.get_tuple())
        for enemy in self.enemies:
            for point in enemy.points:
                obstacles.append(point.get_tuple())
        for snake in self.snakes:
            for point in snake.points:
                obstacles.append(point.get_tuple())
        return obstacles


    @timing_decorator
    def make_grid(self):
        self.G = nx.Graph()
    
        obstacles = self.get_obstacles()
        obstacles_set = set(obstacles)
        
        # Предварительно вычисляем возможные смещения для соседей
        neighbor_offsets = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
        
        # Добавление узлов и рёбер
        for x in range(self.width):
            for y in range(self.high):
                for z in range(self.depth):
                    if (x, y, z) not in obstacles_set:
                        self.G.add_node((x, y, z))
                        for dx, dy, dz in neighbor_offsets:
                            neighbor = (x + dx, y + dy, z + dz)
                            if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.high and 0 <= neighbor[2] < self.depth:
                                if neighbor not in obstacles_set:
                                    self.G.add_edge((x, y, z), neighbor)
                    else:
                        obstacles_set.remove((x, y, z))
    

    def find_way(self, point1, point2):
        try:
            path = nx.astar_path(self.G, point1.get_tuple(), point2.get_tuple())
            return path
        except nx.NetworkXNoPath:
            return None
        
    def get_directions(self):
        snakes_arr = []
        for snake in self.snakes:
            snakes_arr.append(snake.points[0].get_tuple())

        food_arr = []
        for food in self.foods:
            food_arr.append(food.pos.get_tuple())

        #distance_matrix = cdist(snakes_arr, food_arr, metric='cityblock')
        distance_matrix = cdist(snakes_arr, food_arr)
        row_ind, col_ind = linear_sum_assignment(distance_matrix)
        for hunter_index, target_index in zip(row_ind, col_ind):
            snake = snakes_arr[hunter_index]
            food = food_arr[target_index]
            print(f"Охотник на позиции {snake} назначен к цели на позиции {food}, расстояние: {distance_matrix[hunter_index, target_index]:.2f}")