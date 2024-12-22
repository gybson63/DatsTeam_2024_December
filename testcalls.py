import DataDef as gamedata
import json
import gamestate
import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Время выполнения {func.__name__}: {end_time - start_time:.4f} секунд")
        return result
    return wrapper


data = json.loads(open('responses/20241220_211019_647.json').read())
#game_response = gamedata.GameState.parse_obj(data)
game_response = gamedata.GameState.model_validate(data)
gs = gamestate.GameState(data)

dirs = gs.get_directions()

snakes = []
for key, value in dirs.items():
    snakes.append({"id":key.id, "direction" : [value.x, value.y, value.z]})
    print(key.id, value.get_tuple())

body = {"snakes":snakes}
for snake in gs.snakes:
        posstr = "X"
        if snake.status != "dead":
            posstr = str(snake.points[0].get_tuple())
        print(snake.id, snake.status, posstr)