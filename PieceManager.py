from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap, QColor, QImage


class PieceManager:
    PIECES = ["k", "q", "n", "b", "r", "p"]
    COLORS = {
        "w": [
            QtGui.QColor(255,255,255),
            QtGui.QColor(0,0,0)
        ],
        "b": [
            QtGui.QColor(0,0,0),
            QtGui.QColor(255,255,255)
        ],
        "r": [
            QtGui.QColor(200,0,0),
            QtGui.QColor(50,255,255)
        ],
        "y": [
            QtGui.QColor(200,200,0),
            QtGui.QColor(50,50,255)
        ]
    }
    COLOR_NAMES = {
        "w": "White",
        "b": "Black",
        "r": "Red",
        "y": "Yellow"
    }
    PIECE_NAMES = {
        "k": "King",
        "q": "Queen",
        "n": "Knight",
        "b": "Bishop",
        "r": "Rook",
        "p": "Pawn"
    }

    PIECE_IMAGES = {}
    CACHE = {}

    @staticmethod
    def load_assets():
        for p in PieceManager.PIECES:
            image = QtGui.QImage("Data/assets/" + p + ".png")
            PieceManager.PIECE_IMAGES[p] = image

    @staticmethod
    def get_piece_img(color: str, piece: str) -> QPixmap:
        cache = PieceManager.CACHE

        if color not in cache:
            cache[color] = {}

        if piece not in cache[color]:
            piece_img: QImage = PieceManager.PIECE_IMAGES[piece]
            copy: QImage = piece_img.copy()

            def mix(c1: QColor, c2: QColor, f: float, a: int):
                return QtGui.QColor(
                    int(c1.red()   * f + c2.red()   * (1-f)),
                    int(c1.green() * f + c2.green() * (1-f)),
                    int(c1.blue()  * f + c2.blue()  * (1-f)),
                    a
                )

            col1, col2 = PieceManager.COLORS[color]
            for py in range(copy.size().height()):
                for px in range(copy.size().width()):
                    pixel: QColor = copy.pixelColor(px, py)
                    copy.setPixelColor(
                        px, py,
                        mix(col1, col2, pixel.value() / 255, pixel.alpha())
                    )
            cache[color][piece] = QtGui.QPixmap().fromImage(copy)
        return cache[color][piece]

    @staticmethod
    def get_piece_name(piece_and_col: str):
        piece, color = piece_and_col
        piece_name = PieceManager.PIECE_NAMES[piece]
        color_name = PieceManager.COLOR_NAMES[color]
        return f"{color_name} {piece_name}"
