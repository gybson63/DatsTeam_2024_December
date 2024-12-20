def get_rounds(API_KEY, SERVER):

    header={"X-Auth-Token" : API_KEY}

    import requests

    response = requests.get(SERVER+"rounds/snake3d", headers = header)
    rounds = response.json()
    test = 1
    for round in rounds['rounds']:
        if round['status'] !='ended':
            print(round['startAt'], round['status'])