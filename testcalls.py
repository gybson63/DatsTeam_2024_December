import DataDef as gamedata
import json
import gamestate


data = json.loads(open('responses/20241220_211019_647.json').read())
game_response = gamedata.GameState.parse_obj(data)
gs = gamestate.GameState(data)
test = 1