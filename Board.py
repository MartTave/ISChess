class Board:
    def __init__(self, setup:list[list[str]]):
        self.boardTab = setup
        self.value = 0

    def getValue(self):
        puntos = 0
        for x in self.boardTab:
            for y in x:
                #TODO : BLOCS HEURISTIQUES
                puntos += 0
            