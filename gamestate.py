import DataDef
import DataDef as gamedata
from typing import List
import networkx as nx
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
from scipy.spatial import KDTree

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
    
    def get_list(self):
        return [self.x, self.y, self.z]
    
    def get_distance(self, other):
        """
        Вычисляет евклидово расстояние между двумя точками в трёхмерном пространстве.

        :param point1: Координаты первой точки (x1, y1, z1)
        :param point2: Координаты второй точки (x2, y2, z2)
        :return: Евклидово расстояние между точками
        """
        # Преобразуем точки в массивы NumPy
        point1 = np.array(self.get_list())
        point2 = np.array(other.get_list())
        
        # Вычисляем разность координат и их квадрат
        diff = point2 - point1
        squared_diff = np.dot(diff, diff)
        
        # Вычисляем и возвращаем корень из суммы квадратов
        return np.sqrt(squared_diff)

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
        self.id = data.id
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

        self.golden_list = []
        for g in gs.specialFood.golden:
            self.golden_list.append((g.root[0], g.root[1], g.root[2]))

        self.bad_list = []
        for g in gs.specialFood.suspicious:
           self.bad_list.append((g.root[0], g.root[1], g.root[2]))

        self.foods = []
        foods_coord_temp = []
        for food in gs.food:
            f = Food(food)
            if f.pos.get_tuple() in self.bad_list:
                continue
            if f.pos.get_tuple() in self.golden_list:
                f.points *= 2
            self.foods.append(Food(food))
            foods_coord_temp.append(f.pos.get_tuple())
        
        self.foods_coord = set(foods_coord_temp)

        self.snakes = []
        for snake in gs.snakes:
            self.snakes.append(Snake(snake))
        
        self.turn = gs.turn
        self.time_to_end = gs.reviveTimeoutSec
        self.tickRemainMS = gs.tickRemainMs
        self.points = gs.points

        self.obstacles = set(self.get_obstacles())

    def in_bounds(self, p):
        if 0 <= p.x < self.width and 0 <= p.y < self.high and 0 <= p.z < self.depth:
            return True
        else:
            return False

    def get_snake(self, x, y, z):
        for snake in self.snakes:
            if snake.status == 'dead':
                continue
            if snake.points[0].x == x and snake.points[0].y == y and snake.points[0].z == z:
                return snake

    def get_obstacles(self, bold = False):
        neighbor_offsets = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
        bold = True
        obstacles = []
        for fence in self.fences:
            origin = fence.pos.get_tuple()
            obstacles.append(origin)
            if bold:
                for dx, dy, dz in neighbor_offsets:
                    neighbor = (origin[0] + dx, origin[1] + dy, origin[2] + dz)
                    if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.high and 0 <= neighbor[2] < self.depth:
                        obstacles.append(neighbor)

        for enemy in self.enemies:
            for point in enemy.points:
                origin = point.get_tuple()
                obstacles.append(origin)
                if bold:
                    for dx, dy, dz in neighbor_offsets:
                        neighbor = (origin[0] + dx, origin[1] + dy, origin[2] + dz)
                        if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.high and 0 <= neighbor[2] < self.depth:
                            obstacles.append(neighbor)

        for snake in self.snakes:
            for point in snake.points:
                obstacles.append(point.get_tuple())

        obstacles += self.bad_list

        return obstacles


    @timing_decorator
    def make_grid2(self):
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

    @timing_decorator
    def make_grid(self):
        self.G = nx.Graph()
        
        # Создаем множество препятствий
        obstacles = set(self.get_obstacles())
        
        # Создаем список всех узлов, исключая препятствия
        all_nodes = [(x, y, z) for x in range(self.width) for y in range(self.high) for z in range(self.depth) if (x, y, z) not in obstacles]
        
        # Создаем KDTree для всех допустимых узлов
        tree = KDTree(all_nodes)
        
        # Определяем смещения для поиска соседей
        neighbor_offsets = np.array([(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)])
        
        # Добавляем узлы и рёбра на основе соседей
        for node in all_nodes:
            self.G.add_node(node)
            # Ищем всех соседей на расстоянии 1 по любой из осей
            neighbors = [tuple(np.array(node) + offset) for offset in neighbor_offsets]
            for neighbor in neighbors:
                if neighbor in obstacles:
                    continue
                # Проверяем, что сосед существует в KDTree
                if tree.query_ball_point(neighbor, 0):
                    self.G.add_edge(node, neighbor)
    

    @timing_decorator
    def make_grid3(self):
        self.G = nx.Graph()
    
        obstacles = set(self.get_obstacles())
        
        # Предварительно вычисляем возможные смещения для соседей
        neighbor_offsets = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
        
        # Обход всех узлов и добавление только необходимых
        for x in range(self.width):
            for y in range(self.high):
                for z in range(self.depth):
                    current_node = (x, y, z)
                    if current_node in obstacles:
                        continue

                    self.G.add_node(current_node)
                    for dx, dy, dz in neighbor_offsets:
                        neighbor = (x + dx, y + dy, z + dz)
                        if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.high and 0 <= neighbor[2] < self.depth:
                            if neighbor not in obstacles:
                                self.G.add_edge(current_node, neighbor)

    def find_way(self, point1, point2):
        res = []
        neighbor_offsets = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
        for dx, dy, dz in neighbor_offsets:
            neighbor = Point(point1.x + dx, point1.y + dy, point1.z + dz)
            if 0 <= neighbor.x < self.width and 0 <= neighbor.y < self.high and 0 <= neighbor.z < self.depth:
                if (neighbor.x, neighbor.y, neighbor.z) not in self.obstacles:
                    res.append(neighbor)

        best_dist = 100000000
        best_point = None
        for point in res:
            if (point.x, point.y, point.z) in self.foods_coord:
                best_point = Point(point.x-point1.x, point.y-point1.y, point.z-point1.z)
                print("ХОБА!!!")
                break
            dst = point.get_distance(point2)
            if point.get_distance(point2) < best_dist:
                best_point = Point(point.x-point1.x, point.y-point1.y, point.z-point1.z)
                best_dist = dst

        return best_point


    def get_directions(self):

        obstacles = set(self.get_obstacles())
        res = {}

        snakes_arr = []
        for snake in self.snakes:
            if snake.status == 'dead':
                continue
            snakes_arr.append(snake.points[0].get_tuple())

        if len(snakes_arr) == 0:
            return None

        food_arr = []
        food_arr_points = []
        for food in self.foods:
            if food.pos.get_tuple() in obstacles:
                #print("МАНДАРИН В ОБСТАКЛЕ")
                continue
            food_arr.append(food.pos.get_tuple())
            food_arr_points.append(food.points)

        #distance_matrix = cdist(snakes_arr, food_arr, metric='cityblock')
        distance_matrix = cdist(snakes_arr, food_arr)
        for row in range(len(food_arr)):
            distance_matrix[0, row] /= food_arr_points[row]**5
            if len(snakes_arr) > 1:
                distance_matrix[1, row] /= food_arr_points[row]

        row_ind, col_ind = linear_sum_assignment(distance_matrix)
        for hunter_index, target_index in zip(row_ind, col_ind):
            snake_pos = snakes_arr[hunter_index]
            snake = self.get_snake(snake_pos[0], snake_pos[1], snake_pos[2])
            food_pos = food_arr[target_index]
            direct = self.find_way(snake.points[0], Point(food_pos[0], food_pos[1], food_pos[2]))
            print(f"Охотник на позиции {snake_pos} назначен к цели на позиции {food_pos}, расстояние: {distance_matrix[hunter_index, target_index]:.2f}?, направление {direct.get_tuple()}, стоимость {food_arr_points[target_index]}")
            res[snake] = direct

        return res

    def get_directions_bycost(self):

        obstacles = set(self.get_obstacles())
        res = {}

        snakes_arr = []
        for snake in self.snakes:
            if snake.status == 'dead':
                continue
            snakes_arr.append(snake.points[0].get_tuple())

        food_arr = []
        food_arr_points = []
        for food in self.foods:
            if food.pos.get_tuple() in obstacles:
                #print("МАНДАРИН В ОБСТАКЛЕ")
                continue
            food_arr.append(food.pos.get_tuple())
            food_arr_points.append(food.points)

        #distance_matrix = cdist(snakes_arr, food_arr, metric='cityblock')
        distance_matrix = np.zeros((len(snakes_arr), len(food_arr)))
        for row in range(len(food_arr)):
            for col in range(len(snakes_arr)):
                distance_matrix[col, row] = food_arr_points[row]


        row_ind, col_ind = linear_sum_assignment(distance_matrix, maximize = True)
        for hunter_index, target_index in zip(row_ind, col_ind):
            snake_pos = snakes_arr[hunter_index]
            snake = self.get_snake(snake_pos[0], snake_pos[1], snake_pos[2])
            food_pos = food_arr[target_index]
            direct = self.find_way(snake.points[0], Point(food_pos[0], food_pos[1], food_pos[2]))
            print(f"Охотник на позиции {snake_pos} назначен к цели на позиции {food_pos}, расстояние: {distance_matrix[hunter_index, target_index]:.2f}?, направление {direct.get_tuple()}, стоимость {food_arr_points[target_index]}")
            res[snake] = direct

        return res
    
    def get_directions_bycenter(self):

        obstacles = set(self.get_obstacles())
        res = {}

        snakes_arr = []
        for snake in self.snakes:
            if snake.status == 'dead':
                continue
            snakes_arr.append(snake.points[0].get_tuple())

        if len(snakes_arr) == 0:
            return None


        selected_food = []
        for food in self.foods:
            if food.pos.get_tuple() in obstacles:
                #print("МАНДАРИН В ОБСТАКЛЕ")
                continue
            dst_to_center = Point(self.width//2, self.high//2, self.depth//2).get_distance(food.pos)
            selected_food.append([food, dst_to_center])
        
        selected_food.sort(key=lambda x: x[1])

        food_arr = []
        food_arr_points = []
        cnt = len(selected_food) // 1
        for food,dst in selected_food:           
            food_arr.append(food.pos.get_tuple())
            food_arr_points.append(food.points)
            cnt -=1
            if cnt == 0:
                break

        distance_matrix = cdist(snakes_arr, food_arr, metric='cityblock')
        #distance_matrix = np.zeros((len(snakes_arr), len(food_arr)))
        #for row in range(len(food_arr)):
        #    for col in range(len(snakes_arr)):
        #        distance_matrix[col, row] /= food_arr_points[row]


        row_ind, col_ind = linear_sum_assignment(distance_matrix)
        for hunter_index, target_index in zip(row_ind, col_ind):
            snake_pos = snakes_arr[hunter_index]
            snake = self.get_snake(snake_pos[0], snake_pos[1], snake_pos[2])
            food_pos = food_arr[target_index]
            #direct = self.find_way(snake.points[0], Point(food_pos[0], food_pos[1], food_pos[2]), obstacles)
            print(f"Охотник на позиции {snake_pos} назначен к цели на позиции {food_pos}, расстояние: {distance_matrix[hunter_index, target_index]:.2f}?, стоимость {food_arr_points[target_index]}")
            p = Point(food_pos[0], food_pos[1], food_pos[2])
            if self.in_bounds(p):
                res[snake] = p

        return res