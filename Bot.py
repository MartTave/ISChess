

from textwrap import wrap
from Board import Board
from Player import Player
from tools.readJson import readJson
from Bots.ChessBotList import register_chess_bot 

class Bot():


    def __init__(self, configPath: str) -> None:
            self.settings = readJson(configPath)

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
        while playerOrder[0].orientation != 0:
             for p in playerOrder:
                  p.orientation += 1
                  if p.orientation == 4:
                       p.orientation = 0
        currentBoard = Board(board, player, allies, enemies, playerOrder, self.settings)
        move = currentBoard.getBestMove(0.8, 3)
        return move


myBot = Bot("./settings/v1.json")

register_chess_bot("Bot_1", myBot.play)