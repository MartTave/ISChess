

from textwrap import wrap
from Bots.BT_Bot import Bot
import os
import time
import numpy

# Method to clear console cross os
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# This is only for 1v1 tests
# It has full trust in bots and does not check validity of moves -> very non practical
class Party():

    def parseBoard(self, boardPath):
        self.currentData = []
        self.currentPlayerOrder = []
        lines:list[str] = []
        self.playerOrder = []
        with open(boardPath, 'r') as file:
            lines = file.readlines()
            file.close()
        self.currentPlayerOrder = wrap(lines[0], 3)
        lines = lines[1:]
        for l in lines:
            l = l.replace("\n", "")
            l = l.replace("--", "")
            self.currentData.append(l.split(","))

    def printCurrentBoard(self):
        toPrint = "\n\n"
        for l in self.currentData:
            for c in l:
                if c == "":
                    toPrint += "--,"
                else:
                    toPrint += c + ","
            toPrint += "\n"
        print(toPrint)

    def __init__(self, boardPath:str, depthAllowed=5):
        self.parseBoard(boardPath)
        self.bots = {}
        self.bots["w"] = Bot("./settings/v1.json", depthAllowed)
        self.bots["b"] = Bot("./settings/v2.json", depthAllowed)
        self.printCurrentBoard()

    def playGame(self, numberOfPlays=-1):
        if numberOfPlays == 0:
            return False
        currentP: Bot = self.bots[self.currentPlayerOrder[0][1]]
        start = time.time()
        move = currentP.play(''.join(self.currentPlayerOrder), self.currentData, 0.75)
        end = time.time()
        elapsed = end - start
        print("Time elapsed is ", "{:10.4f}".format(elapsed), "s")
        if move == None:
            print("Party seems to be done...")
            print(self.currentPlayerOrder[1][1], " won the game !")
            return False
        self.currentData[move[1][0]][move[1][1]] = self.currentData[move[0][0]][move[0][1]]
        self.currentData[move[0][0]][move[0][1]] = ""
        bcup = self.currentPlayerOrder[0]
        self.currentPlayerOrder[0] = self.currentPlayerOrder[1]
        self.currentPlayerOrder[1] = bcup
        self.printCurrentBoard()
        self.currentData = numpy.rot90(self.currentData).tolist()
        self.currentData = numpy.rot90(self.currentData).tolist()
        kingWhiteFound = False
        kingBlackFound = False
        for i in self.currentData:
            for j in i:
                if j == "kw":
                    kingWhiteFound = True
                    if kingBlackFound:
                        break
                elif j == "kb":
                    kingBlackFound = True
                    if kingWhiteFound:
                        break
        if not kingWhiteFound:
            print("Black has won")
            return (False,0)
        elif not kingBlackFound:
            print("White has won")
            return (False,1)



        
        return True,2

blackWins = 0
whiteWins = 0
nGames = 5
for i in range(0,nGames):
    current = Party("./Data/maps/default.brd", 100000)
    numberOfPlays = -1

    res = True
    winner = 3
    while (res):
        res,winner = current.playGame(numberOfPlays)
        numberOfPlays -= 1
    if winner == 0:
        blackWins += 1
    elif winner == 1:
        whiteWins += 1

print("RESULTATS FINAUX DE LA BASTON: ")
print("NOMBRE DE VICTOIRES DES BLANCS: ", whiteWins)
print("NOMBRE DE VICTOIRES DES NOIRS: ", blackWins)
