import json

def readJson(filePath: str) -> object:
    with open(filePath) as json_data:
        d = json.load(json_data)
        json_data.close()
    return d