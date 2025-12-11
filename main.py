#https://github.com/harisankar95/pathfinding3D/blob/main/pathfinding3d/core/diagonal_movement.py

import rounds
import playermove
import requests
import time
from datetime import datetime
import DataDef as gamedata
import json
import networkx as nx
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import time
import DataDef as gamedata
import json
import gamestate
import time

API_KEY = ""

with open('api.key', 'r') as file:
    input_lines = [line.strip() for line in file]
    API_KEY = input_lines[0]

if API_KEY == "":
    raise "API KEY не задан"

SERVER = "https://games.datsteam.dev/"
#SERVER = "https://games-test.datsteam.dev/"

rounds.get_rounds(API_KEY, SERVER)

targets = {}

data = playermove.move(API_KEY, SERVER)
points = 0
while True:
    print(datetime.now().strftime("%H:%M:%S"))
    start_time = time.time()
    game_response = gamedata.GameState.model_validate(data)
    gs = gamestate.GameState(data)
    print("Набрали вон сколько очков!", gs.points)
    
    #dirs = gs.get_directions()
    #dirs = gs.get_directions_bycost()
    dirs = gs.get_directions_bycenter()
    if dirs is None:
        data = playermove.move(API_KEY, SERVER)
    else:
        snakes = []
        for key, value in dirs.items():
            if targets.get(key.id) is None:
                targets[key.id] = value
                target = value
            elif targets[key.id].get_tuple() in gs.foods_coord:
                target = targets[key.id]
            else:
                del targets[key.id]
                target = value

            dir = gs.find_way(key.points[0], target)
            if not dir is None:
                snakes.append({"id":key.id, "direction" : [dir.x, dir.y, dir.z]})
                print(key.points[0].get_tuple(), " --> ",dir.get_tuple(), " --> ",target.get_tuple())

        body = {"snakes":snakes}
        data = playermove.move(API_KEY, SERVER, json.dumps(body))
    #
    #
    #
    end_time = time.time()
    pause = (100 - (end_time - start_time))/100
    pause = pause / 3
    print("Wait", pause)
    #time.sleep(pause)

