import os.path
import re
from typing import Optional, Dict

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QApplication

from BoardManager import BoardManager
from Bots.ChessBotList import *
from ChessRules import *
from Data.UI import Ui_MainWindow
from ParallelPlayer import *
from Bots import *

import numpy as np

#   Wrap up for QApplication
class ChessApp(QtWidgets.QApplication):
    def __init__(self):
        super().__init__([])


    def start(self):
        arena = ChessArena()
        arena.show()
        arena.start()

        self.exec()

#   Main window to handle the chess board
CHESS_PIECES = ["k", "q", "n", "b", "r", "p"]
CHESS_COLOR = {"w" : [QtGui.QColor(255,255,255), QtGui.QColor(0,0,0)], "b" : [QtGui.QColor(0,0,0), QtGui.QColor(255,255,255)],
               "r" : [QtGui.QColor(200,0,0), QtGui.QColor(50,255,255)], "y" : [QtGui.QColor(200,200,0), QtGui.QColor(50,50,255)]}
COLOR_NAMES = {"w" : "White", "b":"Black", "r":"Red", "y":"Yellow"}
CHESS_PIECES_NAMES = {"k":"King", "q":"Queen", "n":"Knight", "b":"Bishop", "r":"Rook", "p":"Pawn"}

class ChessArena(Ui_MainWindow, QWidget):
    PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
    BOARDS_DIR = os.path.join(PROJECT_DIR, "Data", "maps")
    START_ICON = QtGui.QIcon.fromTheme("media-playback-start")
    STOP_ICON = QtGui.QIcon.fromTheme("media-playback-stop")

    def __init__(self):
        super().__init__()

        uic.loadUi("Data/UI.ui", self)

        # Render for chess board
        self.chess_scene = QtWidgets.QGraphicsScene()
        self.chessboardView.setScene(self.chess_scene)

        # Assets
        self.white_square: Optional[QPixmap] = None
        self.black_square: Optional[QPixmap] = None
        self.pieces_imgs: Dict[str, QImage] = {}
        self.load_assets()

        # Variables
        self.board_manager: BoardManager = BoardManager()
        self.current_player = None
        self.players_AI = {}
        self.nbr_turn_to_play = 0
        self.auto_playing = False

        # Board actions
        self.loadBoard.clicked.connect(self.select_and_load_board)
        self.reloadBoard.clicked.connect(self.board_manager.reload)
        self.copyBoard.clicked.connect(self.copy_board)
        self.exportBoard.clicked.connect(self.export_board)

        # Game actions
        #self.prevMove.clicked.connect(self.prev_move)
        self.startStop.clicked.connect(self.start_stop)
        #self.nextMove.clicked.connect(self.next_move)

    def add_system_message(self, message):
        print("[SYS]", message)

    def start_stop(self):
        if self.auto_playing:
            self.startStop.setIcon(self.START_ICON)
            print("Stopping")
        else:
            self.startStop.setIcon(self.STOP_ICON)
            print("Starting")

        self.auto_playing = not self.auto_playing

    #   Called to start the bot simulation
    def launch_game(self):
        self.add_system_message("# Starting new Game #")
        #   Prepare AIs
        self.players_AI = {}
        for cid, color in enumerate(self.players_AI_choice):
            self.players_AI[color] = CHESS_BOT_LIST[self.players_AI_choice[color].currentText()]
            self.add_system_message("AI #" + str(cid) + " = " + str(self.players_AI[color].__name__))

        self.nbr_turn_to_play = self.autoMovesCount.value()

        self.play_next_turn()

    def play_next_turn(self):
        if self.current_player is not None:
            print("Cannot launch new turn while already processing")
            return

        if self.nbr_turn_to_play == 0:
            print("No more play to do")
            self.end_game(None)
            return

        next_player_color = self.player_order[0:3]

        #   Prepare board view
        rotated_view_board = np.rot90(self.board, int(next_player_color[2]))
        self.current_player = ParallelTurn(self.players_AI[next_player_color[1]], self.player_order, rotated_view_board, self.max_time_budget)
        self.current_player.setTerminationEnabled(True)
        self.current_player.start()

        #   Timer to call
        QtCore.QTimer.singleShot(int(self.max_time_budget * 1000 * 1.05), self.end_turn)


    def end_turn(self):
        all_other_defeated = False

        if self.current_player.isRunning():
            self.current_player.terminate()
            self.add_system_message(COLOR_NAMES[self.current_player.color] + " did not end his turn")
        else:

            player_color = self.current_player.color

            next_play = self.current_player.next_move

            if not move_is_valid(self.player_order, next_play, self.current_player.board):
                self.add_system_message(COLOR_NAMES[player_color] + " invalid move from " + str(next_play[0]) + " to " + str(next_play[1]))
                return

            self.add_system_message(COLOR_NAMES[player_color] + " moved " + CHESS_PIECES_NAMES[self.current_player.board[next_play[0][0], next_play[0][1]][0]] +
                                    " from " + str(next_play[0]) + " to " + str(next_play[1]))

            if self.current_player.board[next_play[1][0], next_play[1][1]] != '':
                self.add_system_message(COLOR_NAMES[player_color] + " captured " + COLOR_NAMES[self.current_player.board[next_play[1][0], next_play[1][1]][1]] + " " + CHESS_PIECES_NAMES[self.current_player.board[next_play[1][0], next_play[1][1]][0]])

            #   apply move
            self.current_player.board[next_play[1][0], next_play[1][1]] = self.current_player.board[next_play[0][0], next_play[0][1]]
            self.current_player.board[next_play[0][0], next_play[0][1]] = ''

            #   check for promotion
            if self.current_player.board[next_play[1][0], next_play[1][1]][0] == 'p' and next_play[1][0] == self.current_player.board.shape[0]-1:
                self.current_player.board[next_play[1][0], next_play[1][1]] = "q" + self.current_player.board[next_play[1][0], next_play[1][1]][1]

            all_other_defeated = True
            for row in self.board:
                for elem in row:
                    if len(elem) > 0 and elem[0] == 'k':
                        if int(self.player_order[self.player_order.find(elem[1])-1]) != int(self.current_player.team):
                            all_other_defeated = False

        #   Update board state
        self.current_player = None

        self.setup_board()

        #   Current player goes at the end of the play queue
        self.player_order = self.player_order[3:] + self.player_order[0:3]
        self.nbr_turn_to_play -= 1

        if all_other_defeated:
            self.end_game(player_color)
        else:
            self.play_next_turn()


    def end_game(self, winner):
        if winner is None:
            self.add_system_message("# Match ended in a draw")
        else:
            self.add_system_message("# " + str(COLOR_NAMES[winner]) + " won the match")

    def select_and_load_board(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select board",
            self.BOARDS_DIR,
            "Board File (*.brd *.fen)"
        )

        if path is None:
            return
        path = path[0]

        if self.board_manager.load_file(path):
            self.setup_board()
            self.setup_players()

    def load_assets(self):
        self.white_square = QtGui.QPixmap("Data/assets/light_square.png")
        self.black_square = QtGui.QPixmap("Data/assets/dark_square.png")

        self.pieces_imgs = {}

        for p in CHESS_PIECES:
            image = QtGui.QImage("Data/assets/" + p + ".png")
            self.pieces_imgs[p] = image

    def setup_players(self):
        for i in reversed(range(self.playersList.count())):
            if self.playersList.itemAt(i).widget() is not None:
                self.playersList.itemAt(i).widget().setParent(None)

        self.players_AI_choice = {}
        for color in self.colored_piece_pixmaps:
            l = QtWidgets.QLabel("Color:"  + COLOR_NAMES[color])
            self.playersList.addWidget(l)

            choice = QtWidgets.QComboBox()

            for name in CHESS_BOT_LIST:
                choice.addItem(name, CHESS_BOT_LIST[name])
            choice.setCurrentIndex(0)

            self.players_AI_choice[color] = choice
            self.playersList.addWidget(choice)

        self.playersList.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding))

    def setup_board(self):
        path: str = os.path.relpath(self.board_manager.path, self.BOARDS_DIR)
        if os.pardir in path:
            path = self.board_manager.path
        self.currentBoardValue.setText(path)
        return
        for i in reversed(self.chess_scene.items()):
            self.chess_scene.removeItem((i))

        #   Maintain the pointer towards the items on the board
        self.piece_items = np.array([[None] * self.board.shape[1]]*self.board.shape[0], dtype=object)
        #   Maintain list of colored pixmap
        self.colored_piece_pixmaps = {}

        for y in range(self.board.shape[1]):
            for x in range(self.board.shape[0]):

                square_color = self.white_square if (x+y) % 2 == 0 else self.black_square
                square_item = self.chess_scene.addPixmap(square_color)
                square_item.setPos(QtCore.QPointF(square_color.size().width()*y,square_color.size().height()*x))

                if self.board[x,y] != '' and self.board[x,y] != 'XX':
                    player_piece = self.board[x,y][0]
                    player_color = self.board[x,y][1]

                    if player_color not in self.colored_piece_pixmaps:
                        self.colored_piece_pixmaps[player_color] = {}

                    if player_piece not in self.colored_piece_pixmaps[player_color]:
                        piece_img = self.pieces_imgs[player_piece]
                        copy = piece_img.copy()

                        def mix(Q1, Q2, f, a):
                            return QtGui.QColor(int(Q1.red()   * f + Q2.red()   * (1-f)),
                                                int(Q1.green() * f + Q2.green() * (1-f)),
                                                int(Q1.blue()  * f + Q2.blue()  * (1-f)), a)

                        for px in range(copy.size().width()):
                            for py in range(copy.size().height()):
                                copy.setPixelColor(px, py, mix(CHESS_COLOR[player_color][0], CHESS_COLOR[player_color][1], copy.pixelColor(px, py).red() / 255., copy.pixelColor(px, py).alpha()))

                        self.colored_piece_pixmaps[player_color][player_piece] = QtGui.QPixmap().fromImage(copy)

                    self.piece_items[x,y] = self.chess_scene.addPixmap(self.colored_piece_pixmaps[player_color][player_piece])
                    self.piece_items[x,y].setPos(QtCore.QPointF(square_color.size().width()*y,square_color.size().height()*x))

        self.chessboardView.fitInView(self.chess_scene.sceneRect())

    def start(self):
        self.setup_board()
        #self.setup_players()
        self.chess_scene.update()

    def copy_board(self):
        fen: str = self.board_manager.get_fen()
        QApplication.clipboard().setText(fen)

    def export_board(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save board as ...",
            self.BOARDS_DIR,
            "Board File (*.brd *.fen)"
        )
        if path == "":
            return
        self.board_manager.save(path)
