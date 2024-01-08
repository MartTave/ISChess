class Player:
    def __init__(self, playerTab: str):
        self.team = int(playerTab[0])
        self.color = str(playerTab[1])
        self.orientation = int(playerTab[2])


    def playerToString(self):
        return "{},{},{}".format(self.team,self.color,self.orientation)