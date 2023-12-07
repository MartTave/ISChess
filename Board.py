from textwrap import wrap
import getNewBoard

class Board:
    RANGEREOUPAS = True

    def __init__(self, setup, teams):
        self.boardTab = setup
        self.value = self.getValue()
        self.teams = wrap(teams, 3) #fait des groupes de 3 characteres avec le string d'equipes
        self.nextBoards:list[Board] = []

    def getValue(self):
        puntos = 0
        for x in self.boardTab:
            for y in x:
                #TODO : BLOCS HEURISTIQUES
                puntos += 0
        self.value = puntos
        
    
    def getBestMove(self,threshold,players):
        self.nextBoards = getNewBoard.getMoves(self)
        
        #on sait pas si on range, faut voir
        maxValue = 0
        if self.RANGEREOUPAS:
            sorted(self.nextBoards, key=lambda x: x.value)
            maxValue = self.nextBoards[0].value
        else:
            for i in self.nextBoards:
                if i.value > maxValue:
                    maxValue = i.value

        for b in self.nextBoards:
            if b.value > maxValue * threshold:
                b.getBestMove(threshold,players)
            else:
                self.nextBoard.pop(b)
        

        
