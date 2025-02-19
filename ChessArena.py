import os.path
from typing import Optional, Dict

from PyQt6 import QtWidgets, QtGui
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QRectF
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QApplication, QFrame

from BoardManager import BoardManager
from BotWidget import BotWidget
from Bots.ChessBotList import *
from ChessRules import *
from Data.UI import Ui_MainWindow
from ParallelPlayer import *
from PieceManager import PieceManager

from Bots import *

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
        self.available_colors: list[str] = []
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

        self.chessboardView.resizeEvent = self.updateChessboard

    def updateChessboard(self, *args, **kwargs):
        view = self.chessboardView
        shape = self.board_manager.board.shape
        board_w = shape[1] * self.black_square.size().width()
        board_h = shape[0] * self.black_square.size().height()
        w_ratio = board_w / view.rect().width()
        h_ratio = board_h / view.rect().height()
        ratio = max(w_ratio, h_ratio)
        w = view.rect().width() * ratio
        h = view.rect().height() * ratio
        rect = QRectF(0, 0, w, h)
        view.setSceneRect(QRectF((board_w - w) / 2, (board_h - h) / 2, w, h))
        view.fitInView(rect)

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

    # Called to start the bot simulation
    def launch_game(self):
        self.add_system_message("# Starting new Game #")
        # Prepare AIs
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

        # Prepare board view
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
        PieceManager.load_assets()

    def setup_board(self):
        path: str = os.path.relpath(self.board_manager.path, self.BOARDS_DIR)
        if os.pardir in path:
            path = self.board_manager.path
        self.currentBoardValue.setText(path)

        self.chess_scene.clear()

        board = self.board_manager.board
        height, width = board.shape

        self.available_colors = []
        for y in range(height):
            for x in range(width):
                # Draw board square
                square_color = self.white_square if (x+y) % 2 == 0 else self.black_square
                square_item = self.chess_scene.addPixmap(square_color)
                square_item.setPos(QtCore.QPointF(square_color.size().width() * x, square_color.size().height() * y))

                # If tile is empty, continue
                if board[y, x] in ("", "XX"):
                    continue

                player_piece = board[y, x][0]
                player_color = board[y, x][1]
                if player_color not in self.available_colors:
                    self.available_colors.append(player_color)

                img = self.chess_scene.addPixmap(PieceManager.get_piece_img(player_color, player_piece))
                img.setPos(QtCore.QPointF(square_color.size().width() * x, square_color.size().height() * y))
        self.updateChessboard()

    def setup_players(self):
        layout = self.botsList.layout()
        for i in reversed(range(layout.count())):
            if layout.itemAt(i).widget() is not None:
                layout.itemAt(i).widget().setParent(None)

        self.players_AI_choice = {}
        for i, color in enumerate(self.available_colors):
            player = BotWidget(color)

            bot_selector = player.playerBot
            for name in CHESS_BOT_LIST:
                bot_selector.addItem(name, CHESS_BOT_LIST[name])
            bot_selector.setCurrentIndex(0)
            self.players_AI_choice[color] = bot_selector
            if i != 0:
                sep = QtWidgets.QFrame()

                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setFrameShadow(QFrame.Shadow.Sunken)
                layout.addWidget(sep)
            layout.addWidget(player)

        # TODO: Find a better solution
        def resize():
            self.botsScrollArea.setMaximumHeight(layout.maximumSize().height() + 2)
        QTimer.singleShot(1, resize)

    def start(self):
        self.setup_board()
        self.setup_players()
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
