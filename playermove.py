import time
from datetime import datetime

def move(API_KEY, SERVER, data = None):

    header={"X-Auth-Token" : API_KEY, 'Content-Type': 'application/json'}

    if data is None:
        data = {'snakes': []}

    import requests

    response = requests.post(SERVER+"play/snake3d/player/move", headers = header, data=data)
    gamestate = response.json()

    from datetime import datetime
    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    with open(f"responses\\{filename}.json", 'w') as file:
        file.write(response.text)
    
    return gamestate