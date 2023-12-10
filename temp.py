

from Board import Board

# TODO Remove
from heuristic import parseBoard

def isInBoard(board:Board, x:int, y:int):
    return x >= 0 and x < len(board.boardTab) and y >= 0 and y < len(board.boardTab)


# This method return -1 is out of board
# 1 if cell contain ally
# 2 if cell contain enemy
def checkCellsContent(board: Board, x: int, y:int, allies: list[str], enemies:list[str])->int:
    if not isInBoard(board, x, y):
        return -1
    data = board.boardTab[x][y]
    if allies.count(data[1]) > 0:
        return 1
    if enemies.count(data[1]) > 0:
        return 2
    return 0
    

def movePiece(board: Board, startX: int, startY: int, endX:int, endY: int)->Board:
    if not isInBoard(board, startX, startY) or not isInBoard(board, endX, endY):
        print("[ERROR] Move piece with invalid position")
    data = board.boardTab.copy()
    data[endX][endY] = data[startX][startY]
    data[startX][startY] = ""
    return Board(data, "")

def checkCell(board: Board, startX:int, startY:int, endX:int, endY:int, allies:list[str], enemies:list[str], resList:list[Board])->bool:
    status = checkCellsContent(board, endX, endY, allies, enemies)
    if status == 0 or status == 2:
        resList.append(movePiece(board, startX, startY, endX, endY))
        # Here, the return serve only to break the loop when we encounter something
        # So if it's an enemy, we need to return false in order to break the loop
        # but still add it as an possibility
        # So status == 0 return true only when cells is empty
        return status == 0
    return False


def getMovesRook(board:Board, x:int, y:int, player:str, allies: list[str], enemies: list[str]):
    data = board.boardTab
    # TODO:This part is for debug -> when final, thoses checks needs to be done upward
    if not isInBoard(board, x, y):
        print("[ERROR] Get moves from rook : index non valid (",x , ", ", y, ")")
        return []
    # If we're here -> position passed in parameter is in board
    if data[x][y][1] != player[0]:
        print("[ERROR] Get moves from rook : cell is not from player : ", data[x][y], " and ", player)
    allAllies = allies.copy()
    allAllies.append(player)
    print("All allies is ", allAllies)
    # Now we can check for moves
    res = []
    # We need to check for four directions
    for i in range(x + 1, len(data)):
        if not checkCell(board, x, y, i, y, allAllies, enemies, res):
            break
    for i in range(x - 1, 0):
        if not checkCell(board, x, y, i, y, allAllies, enemies, res):
            break
    for i in range(y + 1, len(data[0])):
        if not checkCell(board, x, y, x, i, allAllies, enemies, res):
            break
    for i in range(y - 1, 0):
        if not checkCell(board, x, y, x, i, allAllies, enemies, res):
            break
    return res

def getMaladeMoves(board: Board, x:int, y:int, player:str, allies: list[str], enemies: list[str]):
    data = board.boardTab
    # TODO:This part is for debug -> when final, thoses checks needs to be done upward
    if not isInBoard(board, x, y):
        print("[ERROR] Get moves from rook : index non valid (",x , ", ", y, ")")
        return []
    # If we're here -> position passed in parameter is in board
    if data[x][y][1] != player[0]:
        print("[ERROR] Get moves from rook : cell is not from player : ", data[x][y], " and ", player) 
        return []   
    allAllies = allies.copy()
    allAllies.append(player)
    print("All allies is ", allAllies)


    res = []
    # Direction bottom right
    currentX = x + 1
    currentY = y + 1
    while True:
        if not checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
            break
        currentX += 1
        currentY += 1

    # Direction bottom left
    currentX = x - 1
    currentY = y + 1
    while True:
        if not checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
            break
        currentX -= 1
        currentY += 1
    
    # Direction top left
    currentX = x - 1
    currentY = y - 1
    while True:
        if not checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
            break
        currentX -= 1
        currentY -= 1

    # Direction top right
    currentX = x + 1
    currentY = y - 1
    while True:
        if not checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
            break
        currentX += 1
        currentY -= 1
    return res

baseBoard = parseBoard("./Data/maps/default.brd")

res = getMaladeMoves(baseBoard, 0, 2, "w", [], ["b"])
print(len(res))