from tools.readJson import readJson
from Board import Board

heurists_settings_path = "./settings/heuristic.json"

def parseBoard(path:str)-> Board:
    data:list[list[str]] = []
    lines:list[str] = []
    with open(path, 'r') as file:
        lines = file.readlines()
        file.close()
    lines = lines[1:]
    for l in lines:
        l = l.replace("\n", "")
        data.append(l.split(","))
    return Board(data, "")

class Heuristic:
    settings = readJson(heurists_settings_path)

    @staticmethod
    def getValue(board:Board, player: str) -> float:
        points = 0.0
        if Heuristic.settings["pieces"]["active"]:
            points += Heuristic.getPointsForPieces(board, player)
        return points
    
    @staticmethod
    def getPointsForPieces(board:Board, player:str) -> float:
        points = 0.0
        data:list[list[str]] = board.boardTab
        for lines in data:
            for value in lines:
                # Checking for empty cells and if piece has the player has owner
                if value != "" and value != "--" and value[1] == player:
                    points += Heuristic.settings["pieces"]["values"][value[0]]
        return points * Heuristic.settings["pieces"]["factor"]


baseBoard = parseBoard("./Data/maps/default.brd")
val = Heuristic.getValue(baseBoard, "w")
print(val)