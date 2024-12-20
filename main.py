#https://github.com/harisankar95/pathfinding3D/blob/main/pathfinding3d/core/diagonal_movement.py

import rounds
import playermove
import requests
import time
from datetime import datetime

API_KEY = ""

with open('api.key', 'r') as file:
    input_lines = [line.strip() for line in file]
    API_KEY = input_lines[0]

if API_KEY == "":
    raise "API KEY не задан"

SERVER = "https://games.datsteam.dev/"
SERVER = "https://games-test.datsteam.dev/"

#rounds.get_rounds(API_KEY, SERVER)
gamestate_json = playermove.move(API_KEY, SERVER)

