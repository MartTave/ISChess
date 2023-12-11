from Board import Board
from Player import Player
from tools.readJson import readJson

def boardParser(path: str):
    with open(path, 'r') as file:
        lines = file.readlines()
        file.close()
    fl = lines[0]
    lines = lines[1:]
    data = []
    for l in lines:
            l = l.replace("\n", "")
            data.append(l.split(","))
    player = Player("0w0")
    enemy = Player("1b2")
    return Board(data, player, [player], [enemy], [player, enemy], readJson("./settings/v1.json"))


brd = boardParser("./Data/maps/default2.brd")

move = brd.getBestMove(0.9, 2)
print(move)