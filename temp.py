import copy
from Board import Board

# TODO Remove
from heuristic import parseBoard

def isInBoard(board:Board, x:int, y:int):
    return x >= 0 and x < len(board.boardTab[0]) and y >= 0 and y < len(board.boardTab)


# This method return -1 is out of board
# 1 if cell contain ally
# 2 if cell contain enemy
def checkCellsContent(board: Board, x: int, y:int, allies: list[str], enemies:list[str])->int:
    if not isInBoard(board, x, y):
        return -1
    data = board.boardTab[y][x]
    if allies.count(data[1]) > 0:
        return 1
    if enemies.count(data[1]) > 0:
        return 2
    return 0
    

def movePiece(board: Board, startX: int, startY: int, endX:int, endY: int)->Board:
    if not isInBoard(board, startX, startY) or not isInBoard(board, endX, endY):
        print("[ERROR] Move piece with invalid position")
    data = copy.deepcopy(board.boardTab)
    data[endY][endX] = data[startY][startX]
    data[startY][startX] = ""
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
    if len(data[y][x]) > 1 and data[y][x][1] != player[0]:
        print("[ERROR] Get moves from rook : cell is not from player : ", data[y][x], " and ", player)
        return
    allAllies = allies.copy()
    allAllies.append(player)
    # Now we can check for moves
    res = []
    # We need to check for four directions
    for i in range(x + 1, len(data[0])):
        if not checkCell(board, x, y, i, y, allAllies, enemies, res):
            break
    for i in range(x - 1, 0, -1):
        if not checkCell(board, x, y, i, y, allAllies, enemies, res):
            break
    for i in range(y + 1, len(data)):
        if not checkCell(board, x, y, x, i, allAllies, enemies, res):
            break
    for i in range(y - 1, 0, -1):
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
    if len(data[y][x]) > 1 and data[y][x][1] != player[0]:
        print("[ERROR] Get moves from rook : cell is not from player : ", data[y][x], " and ", player) 
        return []   
    allAllies = allies.copy()
    allAllies.append(player)


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

def getQueenMoves(board: Board, x: int, y: int, player:str, allies:list[str], enemies: list[str]) -> list[Board]:
    part1 = getMovesRook(board, x, y, player, allies, enemies)
    part2 = getMaladeMoves(board, x, y, player, allies, enemies)
    return part1 + part2

def getAllMoves(board: Board, player: str, allies: list[str], enemies: list[str])->list[Board]:
    res = []
    for y in range(0, len(board.boardTab)):
        for x in range(0, len(board.boardTab[y])):
            current = board.boardTab[y][x]
            if len(current) > 1 and current[1] == player:
                # Cells has a piece and it's ours !
                piece = current[0]
                match piece:
                    case 'q':
                        res += getQueenMoves(board, x, y, player, allies, enemies)
                    case 'r':
                        res += getMovesRook(board, x, y, player, allies, enemies)
                    case 'b':
                        res += getMaladeMoves(board, x, y, player, allies, enemies)


baseBoard = parseBoard("./Data/maps/default.brd")

res = getQueenMoves(baseBoard, 3, 0, "w", [], ["b"])
print(len(res))