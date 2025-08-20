import os.path
from typing import Optional, Dict

from PyQt6 import QtWidgets, QtGui
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QRectF
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QApplication, QFrame, QMessageBox, QTableWidgetItem, QAbstractItemView

from BoardManager import BoardManager
from BotWidget import BotWidget
from Bots.ChessBotList import *
from ChessRules import *
from Data.UI import Ui_MainWindow
from GameManager import GameManager
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
        self.game_manager: GameManager = GameManager(self)
        self.board_manager: BoardManager = self.game_manager.board_manager

        # Board actions
        self.loadBoard.clicked.connect(self.select_and_load_board)
        self.reloadBoard.clicked.connect(self.reload_board)
        self.copyBoard.clicked.connect(self.copy_board)
        self.exportBoard.clicked.connect(self.export_board)

        # Game actions
        self.prevMove.clicked.connect(self.game_manager.undo_move)
        self.startStop.clicked.connect(self.game_manager.start_stop)
        self.nextMove.clicked.connect(self.game_manager.redo_move)

        self.movesList.resizeColumnsToContents()

        self.chessboardView.resizeEvent = self.update_chessboard

    def update_chessboard(self, *args, **kwargs):
        """ Update chessboard to fit in view """

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

        for y in range(height):
            for x in range(width):
                # Draw board square
                square_color = self.white_square if (x+y) % 2 == 0 else self.black_square
                square_item = self.chess_scene.addPixmap(square_color)
                square_item.setPos(QtCore.QPointF(square_color.size().width() * x, square_color.size().height() * y))

                # If tile is empty, continue
                if board[y, x] in ("", "XX"):
                    continue

                player_piece, player_color = board[y, x]

                img = self.chess_scene.addPixmap(PieceManager.get_piece_img(player_color, player_piece))
                img.setPos(QtCore.QPointF(square_color.size().width() * x, square_color.size().height() * y))
        self.update_chessboard()

    def setup_players(self):
        self.game_manager.reset()
        layout = self.botsList.layout()
        for i in reversed(range(layout.count())):
            if layout.itemAt(i).widget() is not None:
                layout.itemAt(i).widget().setParent(None)

        for i, color in enumerate(self.board_manager.available_colors):
            player = BotWidget(color)

            bot_selector = player.playerBot
            for name in CHESS_BOT_LIST:
                bot_selector.addItem(name, CHESS_BOT_LIST[name])
            bot_selector.setCurrentIndex(0)
            if i != 0:
                sep = QtWidgets.QFrame()

                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setFrameShadow(QFrame.Shadow.Sunken)
                layout.addWidget(sep)
            layout.addWidget(player)
            self.game_manager.add_player(color, player)

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

    def reload_board(self):
        self.board_manager.reload()
        self.setup_board()

    def show_message(self, message: str, title: str = "Message"):
        msgbox = QMessageBox(self)
        msgbox.setWindowTitle(title)
        msgbox.setText(message)
        msgbox.open()

    def push_move_to_history(self, move: str, player: str):
        tab = self.movesList
        tab.insertRow(tab.rowCount())
        tab.setItem(tab.rowCount() - 1, 0, QTableWidgetItem(str(tab.rowCount())))
        tab.setItem(tab.rowCount() - 1, 1, QTableWidgetItem(move))
        tab.setItem(tab.rowCount() - 1, 2, QTableWidgetItem(player))
        tab.resizeColumnsToContents()
