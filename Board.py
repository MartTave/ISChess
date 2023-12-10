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

    def playerRotate(self, playerTab):
        #fonction rapide pour passer d'un joueur a l'autre => [1,2,3,4] devient [2,3,4,1]
        outTab = []
        for i in range(1,len(playerTab),step=1):
            outTab.append(playerTab[i])
        outTab.append(playerTab[0])
        return outTab
    
    def getBestMove(self,threshold,players):
        self.nextBoards = getNewBoard.getMoves(self,players[0])
        
        #on sait pas si on range, faut voir
        maxValue = 0
        if self.RANGEREOUPAS:
            #si la constante dit qu'on range
            sorted(self.nextBoards, key=lambda x: x.value)
            maxValue = self.nextBoards[0].value
        else:
            #si la contante dit qu'on s'en fout
            for i in self.nextBoards:
                #pour chaque Board enfant
                if i.value > maxValue:
                    #on cherche le board avec la plus grande valeur
                    maxValue = i.value

        for b in self.nextBoards:
            #pour chaque Board enfant
            if b.value > maxValue * threshold:
                #si c'est un move suffisament interessant
                b.getBestMove(-threshold,self.playerRotate(players)) #on inverse les valeurs pour par réécrire la ligne
            else:
                #si c'est un move de merde
                self.nextBoard.pop(b)
        

        
