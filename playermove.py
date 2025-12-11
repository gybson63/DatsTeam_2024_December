import time
from datetime import datetime
import requests

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Время выполнения {func.__name__}: {end_time - start_time:.4f} секунд")
        return result
    return wrapper

def move(API_KEY, SERVER, data = None):

    header={"X-Auth-Token" : API_KEY, 'Content-Type': 'application/json'}

    if data is None:
        data = {'snakes': []}

    start_time = time.time()
    response = requests.post(SERVER+"api/move", headers = header, data=data)
    end_time = time.time()
    print(f"Время выполнения request: {end_time - start_time:.4f} секунд")
    gamestate = response.json()

    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    with open(f"C:\\DatsTeam\\responses_new\\{filename}.json", 'w') as file:
        file.write(response.text)

    return gamestate