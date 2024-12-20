import DataDef as gamedata
import json


data = json.loads(open('responses/20241220_211019_647.json').read())
gs = gamedata.GameState.parse_obj(data)
test = 1