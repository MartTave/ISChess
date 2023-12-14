

from textwrap import wrap
from Bot import Bot
import os
import time

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
        self.bots["b"] = Bot("./settings/v1.json", depthAllowed)
        self.printCurrentBoard()

    def playGame(self, numberOfPlays=-1):
        if numberOfPlays == 0:
            return
        currentP: Bot = self.bots[self.currentPlayerOrder[0][1]]
        start = time.time()
        move = currentP.play(''.join(self.currentPlayerOrder), self.currentData, 10)
        end = time.time()
        elapsed = end - start
        print("Time elapsed is ", "{:10.4f}".format(elapsed), "s")
        if move == None:
            print("Party seems to be done...")
            print(self.currentPlayerOrder[1][1], " won the game !")
            return
        self.currentData[move[1][0]][move[1][1]] = self.currentData[move[0][0]][move[0][1]]
        self.currentData[move[0][0]][move[0][1]] = ""
        bcup = self.currentPlayerOrder[0]
        self.currentPlayerOrder[0] = self.currentPlayerOrder[1]
        self.currentPlayerOrder[1] = bcup
        self.printCurrentBoard()
        self.playGame(numberOfPlays - 1)


current = Party("./Data/maps/defaultTest1.brd", 5)
current.playGame()