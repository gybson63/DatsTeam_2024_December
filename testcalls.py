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

print(gs.get_directions())