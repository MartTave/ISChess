

from textwrap import wrap
from Board import Board
from Player import Player

class Party():

    teams = {}

    def boardParser(self, boardPath):
        data:list[list[str]] = []
        lines:list[str] = []
        with open(boardPath, 'r') as file:
            lines = file.readlines()
            file.close()
        firstL = lines[0]
        teams = wrap(firstL, 3)
        firstP:Player = None
        for t in teams:
            if firstP == None:
                firstP = t
            newP = Player(t)
            if not newP.team in self.teams:
                self.teams[newP.team] = []
            self.teams[newP.team].append(newP)
        lines = lines[1:]
        for l in lines:
            l = l.replace("\n", "")
            data.append(l.split(","))
        return Board(data, firstP, teams[firstP.team], )

    def __init__(self, boardPath:str):
        self.startBoard = self.boardParser(boardPath)