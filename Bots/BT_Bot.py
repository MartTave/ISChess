

from textwrap import wrap
from tools.readJson import readJson
from Bots.ChessBotList import register_chess_bot 
import sys
import datetime
import json
from random import randrange, choices
import copy
import time
sys.setrecursionlimit(100000)


class Player:
    def __init__(self, playerTab: str):
        self.team = int(playerTab[0])
        self.color = str(playerTab[1])
        self.orientation = int(playerTab[2])


    def playerToString(self):
        return "{},{},{}".format(self.team,self.color,self.orientation)

CLACLUL_PARAM = 50
counter = 0
start = 0

popped = 0

class Board:
    RANGEREOUPAS = True

    def __init__(self, setup, player: Player, allies: list[Player], enemies:list[Player], playerOrder:list[Player], settings:object):
        self.settings = settings
        self.boardTab = setup
        self.playerOrder = playerOrder
        self.player = player
        self.allies = allies
        self.enemies = enemies
        self.value = self.getValue()
        self.nextMoves:list[Move] = []

    def boardToArray(self):
        res = []
        for i in self.boardTab:
            toAppend = ""
            for j in i:
                if j == "":
                    toAppend += "--,"
                else:
                    toAppend += j + ","
            res.append(toAppend)
        return res

    def boardToString(self):
        res = ""
        for i in self.boardTab:
            line = ""
            for j in i:
                if j == "":
                    line += "--,"
                    continue
                line += j
                if j != i[-1]:
                    line += ','
            res += line + "\n"
        return res

    def getValue(self)-> float:
        global counter
        counter += 1
        # Valuing the board with the player that played to get to this board
        return Heuristic.getValue(self, self.player, self.settings)

    def getTeams(self, player: Player) -> tuple[list[Player], list[Player]]:
        allies = [player]
        enemies = []
        for p in self.playerOrder:
            if p.team == player.team:
                allies.append(p)
            else:
                enemies.append(p)
        return (allies, enemies)

    def playerRotate(self, playerTab):
        #fonction rapide pour passer d'un joueur a l'autre => [1,2,3,4] devient [2,3,4,1]
        outTab = []
        for i in range(1,len(playerTab)):
            outTab.append(playerTab[i])
        outTab.append(playerTab[0])
        return outTab
    
    def getBestMove(self, treshold, timeAllowed, depth=5)-> tuple[tuple[int, int], tuple[int, int]]:
        global start
        start = time.time()
        timeAllowedExploration = timeAllowed / 100.0 * 97.5
        self.fillPossibleBoards(treshold, timeAllowedExploration, depth)
        res = analyseBoardTree(self)
        return res

    def fillPossibleBoards(self, threshold, timeTarget, depth=5):
        if depth <= 0:
            return False
        current = time.time()
        global start
        elapsed = current - start
        if elapsed >= timeTarget:
            return False
        self.nextMoves = getAllMoves(self, self.player, self.allies, self.enemies)
        # Activate only if treshold pruning is deactivated
        # for m in self.nextMoves:
        #     m.board.fillPossibleBoards(threshold, depth - 1)
        if len(self.nextMoves) == 0:
            return True
        #on sait pas si on range, faut voir
        minValue = 10000
        if self.RANGEREOUPAS:
            #si la constante dit qu'on range
            sorted(self.nextMoves, key=lambda x: x.board.value)
            minValue = self.nextMoves[-1].board.value
        else:
            #si la contante dit qu'on s'en fout
            for i in self.nextMoves:
                #pour chaque Board enfant
                if i.value < minValue:
                   #on cherche le board avec la plus grande valeur
                   minValue = i.board.value

        currentTresh = minValue + (threshold)
        global popped
        for b in self.nextMoves:
            #pour chaque Board enfant
            if b.board.value < currentTresh:
                # si c'est un move suffisament interessant
                if not b.board.fillPossibleBoards(threshold, timeTarget, depth - 1): #on inverse les valeurs pour pas réécrire la ligne
                    break
            else:
                # si c'est un move de merde
                self.nextMoves.pop(self.nextMoves.index(b))
                popped += 1
        return True

class Move:
    def __init__(self, board:Board, move: tuple[tuple[int, int], tuple[int, int]]):
        self.board = board
        self.move = move

class Heuristic:

    @staticmethod
    def getValue(board:Board, player: Player, settings:object) -> float:
        points = 0.0
        if settings["cases"]["active"]:
            points += Heuristic.getPointsForPiecesAndCases(board, player, settings)
        else:
            points += Heuristic.getPointsForPieces(board, player, settings)
        return points
    
    @staticmethod
    def getPointsForPieces(board:Board, player:Player, settings:object) -> float:
        points = 0.0
        data:list[list[str]] = board.boardTab
        for lines in data:
            for value in lines:
                # Checking for empty cells and if piece has the player as owner
                if value != "" and value != "--" and value[1] == player.color:
                    points += settings["pieces"]["values"][value[0]]
        return points * settings["pieces"]["factor"]

    @staticmethod
    def getPointsForPiecesAndCases(board:Board, player:Player, settings:object) -> float:
        pointsPieces = 0.0
        pointsCases = 0.0
        data:list[list[str]] = board.boardTab
        for lines in range(0,len(data)):
            for value in range(0,len(data[lines])):
                # Checking for empty cells and if piece has the player as owner
                if data[lines][value] != "" and data[lines][value] != "--" and data[lines][value][1] == player.color:
                    pointsPieces += settings["pieces"]["values"][data[lines][value][0]]
                    pointsCases += settings["cases"]["values"]["lignes"][str(lines)] * settings["cases"]["values"]["colonnes"][str(value)]
        return pointsPieces * settings["pieces"]["factor"] + pointsCases * settings["cases"]["factor"]


def isInBoard(board:Board, x:int, y:int):
    return x >= 0 and x < len(board.boardTab[0]) and y >= 0 and y < len(board.boardTab)



# This method return -1 if out of board
# 1 if cell contain ally
# 2 if cell contain enemy
def checkCellsContent(board: Board, x: int, y:int, allies: list[Player], enemies:list[Player])->int:
    if not isInBoard(board, x, y):
        return -1
    data = board.boardTab[y][x]
    if data == "":
        return 0
    if data[1] in [ally.color for ally in allies]:
        return 1
    if data[1] in [enemy.color for enemy in enemies]:
        return 2
    return 0
    

def movePiece(board: Board, startX: int, startY: int, endX:int, endY: int)->Move:
    if not isInBoard(board, startX, startY) or not isInBoard(board, endX, endY):
        print("[ERROR] Move piece with invalid position")
    data = copy.deepcopy(board.boardTab)
    data[endY][endX] = data[startY][startX]
    data[startY][startX] = ""
    nextPlayerOrder = board.playerRotate(board.playerOrder)
    nextPlayerTeams = board.getTeams(nextPlayerOrder[0])
    return Move(Board(data, nextPlayerOrder[0], nextPlayerTeams[0], nextPlayerTeams[1], nextPlayerOrder, board.settings), ((startY, startX), (endY, endX)))

def checkCell(board: Board, startX:int, startY:int, endX:int, endY:int, allies:list[Player], enemies:list[Player], resList:list[Move])->bool:
    status = checkCellsContent(board, endX, endY, allies, enemies)
    if status == 0 or status == 2:
        resList.append(movePiece(board, startX, startY, endX, endY))
        # Here, the return serve only to break the loop when we encounter something
        # So if it's an enemy, we need to return false in order to break the loop
        # but still add it as an possibility
        # So status == 0 return true only when cells is empty
        return status == 0
    return False

def getNextPiongMoves(player:Player, x: int, y: int) -> tuple[int, int]:
    match player.orientation:
        case 0:
            # Bottom
            return (x, y + 1)
        case 1:
            # Left
            return (x - 1, y)
        case 2:
            # Top
            return (x, y - 1)
        case 3:
            # Right
            return (x + 1, y)
    print("There was an non recognized orientation : ", player.orientation)

def getPromotingLine(player: Player, board: Board) -> tuple[str, int]:
    match player.orientation:
        case 0:
            # Bottom -> last y row is promoting
            return ('y', len(board.boardTab) - 1)
        case 1:
            # Left -> first x column is promoting
            return ('x', 0)
        case 2:
            # Top -> first y row is promoting
            return ('y', 0)
        case 3:
            # Right -> last x column is promoting
            return ('x', len(board.boardTab[0]) - 1)

def getNextPiongAttack(player: Player, x: int, y: int) -> tuple[tuple[int, int], tuple[int, int]]:
    topLeft = (x - 1, y - 1)
    topRight = (x + 1, y - 1)
    bottomLeft = (x - 1, y + 1)
    bottomRight = (x + 1, y + 1)
    match player.orientation:
        case 0:
            # Bottom -> bottom left/ bottom right
            return (bottomLeft, bottomRight)
        case 1:
            # Left -> top left/bottom left
            return (topLeft, bottomLeft)
        case 2:
            # Top -> top right/top left
            return (topRight, topLeft)
        case 3:
            # Right -> top right/ bottom right
            return (topRight, bottomRight)

def getMovesPiong(board: Board, x: int, y: int, player:Player,  allies:list[Player], enemies:list[Player]) -> list[Move]:
    nextIndexes = getNextPiongMoves(player, x, y)
    nextAttacks = getNextPiongAttack(player, x, y)
    res = []
    promotingCondition = getPromotingLine(player, board)
    # Here we check if the cell in the direction of the pawn is empty or not
    cellStatus = checkCellsContent(board, nextIndexes[0], nextIndexes[1], allies, enemies)
    if cellStatus == 0:
        # If it's empty -> we can add it to the solutions
        newMove = movePiece(board, x, y, nextIndexes[0], nextIndexes[1])
        if (promotingCondition[0] == 'x' and nextIndexes[0] == promotingCondition[1]) or (promotingCondition[0] == 'y' and nextIndexes[1] == promotingCondition[1]):
            # If pawn is on promoting row/column
            newMove.board.boardTab[nextIndexes[1]][nextIndexes[0]] = "q" + player.color
        res.append(newMove)
            
    # Now we can check if pawn can attack !!
    for a in nextAttacks:
        if checkCellsContent(board, a[0], a[1], allies, enemies) == 2:
            # There is an enemy in the cell -> we can attack it !!!
            newMove = movePiece(board, x, y, a[0], a[1])
            if (promotingCondition[0] == 'x' and a[0] == promotingCondition[1]) or (promotingCondition[0] == 'y' and a[1] == promotingCondition[1]):
                # If pawn is on promoting row/column
                # We replace it by a queen
                newMove.board.boardTab[a[1]][a[0]] = "q" + player.color
            res.append(newMove)    
    return res

def getChevalMoves(board: Board, x: int, y: int, player:Player, allies:list[Player], enemies: list[Player]) -> list[Move]:

    res = []
    checkCell(board, x, y, x + 1, y + 2, allies, enemies, res)
    checkCell(board, x, y, x - 1, y + 2, allies, enemies, res)
    checkCell(board, x, y, x + 1, y - 2, allies, enemies, res)
    checkCell(board, x, y, x - 1, y - 2, allies, enemies, res)
    checkCell(board, x, y, x + 2, y + 1, allies, enemies, res)
    checkCell(board, x, y, x - 2, y + 1, allies, enemies, res)
    checkCell(board, x, y, x + 2, y - 1, allies, enemies, res)
    checkCell(board, x, y, x - 2, y - 1, allies, enemies, res)
    return res

def getRoahMoves(board: Board, x: int, y: int, player:Player, allies: list[Player], enemies: list[Player]) -> list[Move]:
    res = []
    checkCell(board, x, y, x - 1, y - 1, allies, enemies, res)
    checkCell(board, x, y, x, y - 1, allies, enemies, res)
    checkCell(board, x, y, x + 1, y - 1, allies, enemies, res)
    checkCell(board, x, y, x + 1, y, allies, enemies, res)
    checkCell(board, x, y, x + 1, y + 1, allies, enemies, res)
    checkCell(board, x, y, x, y + 1, allies, enemies, res)
    checkCell(board, x, y, x - 1, y + 1, allies, enemies, res)
    checkCell(board, x, y, x - 1, y, allies, enemies, res)
    return res

def getMovesRook(board:Board, x:int, y:int, player:Player, allies: list[Player], enemies: list[Player]):
    data = board.boardTab
    # If we're here -> position passed in parameter is in board
    if len(data[y][x]) > 1 and data[y][x][1] != player.color:
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
    for i in range(x - 1, -1, -1):
        if not checkCell(board, x, y, i, y, allAllies, enemies, res):
            break
    for i in range(y + 1, len(data)):
        if not checkCell(board, x, y, x, i, allAllies, enemies, res):
            break
    for i in range(y - 1, -1, -1):
        if not checkCell(board, x, y, x, i, allAllies, enemies, res):
            break
    return res

def getMaladeMoves(board: Board, x:int, y:int, player:Player, allies: list[Player], enemies: list[Player]) -> list[Move]:
    data = board.boardTab
    # If we're here -> position passed in parameter is in board
    if len(data[y][x]) > 1 and data[y][x][1] != player.color:
        print("[ERROR] Get moves from rook : cell is not from player : ", data[y][x], " and ", player) 
        return []   
    allAllies = allies.copy()
    allAllies.append(player)


    res = []
    # Direction bottom right
    currentX = x + 1
    currentY = y + 1
    while checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
        currentX += 1
        currentY += 1

    # Direction bottom left
    currentX = x - 1
    currentY = y + 1
    while checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
        currentX -= 1
        currentY += 1
    
    # Direction top left
    currentX = x - 1
    currentY = y - 1
    while checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
        currentX -= 1
        currentY -= 1

    # Direction top right
    currentX = x + 1
    currentY = y - 1
    while checkCell(board, x, y, currentX, currentY, allAllies, enemies, res):
        currentX += 1
        currentY -= 1
    return res

def getQueenMoves(board: Board, x: int, y: int, player:Player, allies:list[Player], enemies: list[Player]) -> list[Move]:
    part1 = getMovesRook(board, x, y, player, allies, enemies)
    part2 = getMaladeMoves(board, x, y, player, allies, enemies)
    return part1 + part2

def getAllMoves(board: Board, player: Player, allies: list[Player], enemies: list[Player])->list[Move]:
    res: list[Move] = []
    for y in range(0, len(board.boardTab)):
        for x in range(0, len(board.boardTab[y])):
            current = board.boardTab[y][x]
            if len(current) > 1 and current[1] == player.color:
                # Cells has a piece and it's ours !
                piece = current[0]
                match piece:
                    case 'q':
                        res += getQueenMoves(board, x, y, player, allies, enemies)
                    case 'r':
                        res += getMovesRook(board, x, y, player, allies, enemies)
                    case 'b':
                        res += getMaladeMoves(board, x, y, player, allies, enemies)
                    case 'n':
                        res += getChevalMoves(board, x, y, player, allies, enemies)
                    case 'p':
                        moves = getMovesPiong(board, x, y, player, allies, enemies)
                        res += moves
                    case 'k':
                        res += getRoahMoves(board, x, y, player, allies, enemies)
    return res

def getProba(score: float):
    return CLACLUL_PARAM / (score + 0.1)

def getMoveFromBoards(source: Board, dest:Board):
    player = source.player
    for i in range(0, len(source.boardTab)):
        for j in range(0, len(source.boardTab[i])):
            current = dest.boardTab[i][j]
            if current != "" and current[1] == player.color:
                # This is one of our piece -> we need to find if it has moved
                if current != source.boardTab[i][j]:
                    # This mean we have found the pieces that moved
                    pass


numberOfPrint = 0
def logToJson(boardTree: Board):
    def getChildObject(board: Board):
        toReturn = []
        sorted(board.nextMoves, key=lambda x: x.board.value)
        for m in board.nextMoves:
            childs = getChildObject(m.board)
            toReturn.append({
                "move": m.move,
                "score": m.board.value,
                "board": m.board.boardToArray(),
                "childs": childs
            })
        return toReturn
    childs = getChildObject(boardTree)
    currentBoard = {
        "board": boardTree.boardToArray(),
        "childs": childs
    }
    global numberOfPrint
    fileName = "./logs/" + str(datetime.datetime.now()) + "-" + str(numberOfPrint) + ".json"
    with open(fileName, 'w') as currentFile:
        json.dump(currentBoard, currentFile)
        currentFile.close()
    numberOfPrint += 1



movesFound = -1

def analyseBoardTree(rootBoard: Board) -> tuple[tuple[int, int], tuple[int, int]]:
    global movesFound
    movesFound = -1
    def getChildsScore(board:Board) -> float:
        global movesFound
        movesFound += 1
        totalBrut = 0
        totalRaf = 0
        childScores = []
        for c in board.nextMoves:
            getChildsScore(c.board)
            newVal = getProba(c.board.value)
            childScores.append(newVal)
            totalBrut += newVal
        index = 0
        for c in board.nextMoves:
            totalRaf += childScores[index] * (childScores[index] / totalBrut)
            index += 1
        board.value += totalRaf
    getChildsScore(rootBoard)
    # Here the values of the child must be updated -> we can choose the greater one
    if len(rootBoard.nextMoves) == 0:
        return
    choosenMove = rootBoard.nextMoves[randrange(0, len(rootBoard.nextMoves))]
    if rootBoard.settings["stochastic"]:
        print("Choosing with stochastic !")
        # We need to get percentage
        moves = rootBoard.nextMoves
        values = []
        for c in moves:
            values.append(c.board.value)
        choosenMove = choices(moves, values)[0]
    else:
        print("Move choosen is deterministic")
        minMove = choosenMove
        min = minMove.board.value
        for c in rootBoard.nextMoves:
            if c.board.value < min:
                print("[SYS] Found a better move")
                minMove = c
                min = c.board.value
    print("Found a move in ", movesFound, " total moves")
    global popped
    print("Popped ", popped, " moves with treshold")
    popped = 0

    # TODO: Activate this to log all decisions to json files
    # logToJson(rootBoard)
    return choosenMove.move


class Bot():


    def __init__(self, configPath: str, depthAllowed=5, needRotating=True) -> None:
            
            self.settings = readJson(configPath)
            self.needRotating = needRotating
            self.depthAllowed = depthAllowed

    def play(self, player_sequence: str, board: list[list[str]], time_budget):
        teams = wrap(player_sequence, 3)
        player = Player(teams[0])
        playerOrder = [player]
        teams = teams[1:]
        allies = [player]
        enemies = []
        for t in teams:
            c = Player(t)
            playerOrder.append(c)
            if c.team == player.team:
                allies.append(c)
            else:
                enemies.append(c)
        if self.needRotating:
            while playerOrder[0].orientation != 0:
                for p in playerOrder:
                    p.orientation += 1
                    if p.orientation == 4:
                        p.orientation = 0
        currentBoard = Board(board, player, allies, enemies, playerOrder, self.settings)
        time_budget -= 0.05
        move = currentBoard.getBestMove(1000, time_budget, self.depthAllowed)
        return move



myBot = Bot("./Bots/BT_Settings.json", 100000)

register_chess_bot("BT_Bot", myBot.play)

