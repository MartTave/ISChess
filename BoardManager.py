import os
import re
from typing import Optional

import numpy as np


class BoardManager:
    BOARD_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "Data", "maps")
    DEFAULT_BOARD = os.path.join(BOARD_DIRECTORY, "default.brd")

    def __init__(self):
        self.board: np.array = np.array([], dtype='O')
        self.path: Optional[str] = None
        self.player_order: str = "0w01b2"
        self.load_file(self.DEFAULT_BOARD)

    def load_file(self, path: str) -> bool:
        if path.strip() == "":
            return False

        if not os.path.exists(path):
            print(f"File '{path}' not found")
            return False

        if not os.path.isfile(path):
            print(f"'{path}' is not a file")
            return False

        ext = os.path.splitext(path)[1]

        if ext not in (".brd", ".fen"):
            print(f"Unsupported extension '{ext}'")
            return False

        with open(path, "r") as f:
            data = f.read()

        if ext == ".brd":
            lines = data.split("\n")
            rows = [
                line.replace('--', '').strip().split(",")
                for line in lines[1:]
            ]
            rows = list(filter(lambda r: len(r) != 0, rows))
            if len(rows) == 0:
                print("Board must have at least one row")
                return False

            width = len(rows[0])

            #   check lines length equals
            for row in rows:
                if len(row) != width:
                    print("All rows must have the same width")
                    return False

            self.player_order = lines[0]
            self.board = np.array(rows, dtype='O')
            self.path = path
            return True

        elif ext == ".fen":
            parts = data.strip().split(" ")
            if len(parts) == 0:
                print("FEN must at least contain the board state")
                return False

            board_desc = parts[0]
            rows_desc = board_desc.split("/")
            if len(rows_desc) == 0:
                print("Board must have at least one row")
                return False

            rows = []

            # Match before a letter or between a letter and a digit, or at the start/end of the string
            # (allows for bigger board with spaces >= 10)
            regexp = r"^|(?=\D)|(?<=\D)(?=\d)|$"
            for row_desc in rows_desc:
                matches = list(re.finditer(regexp, row_desc))
                row = []
                for i in range(len(matches) - 1):
                    m1 = matches[i]
                    m2 = matches[i + 1]
                    part = row_desc[m1.start():m2.start()]
                    if part.isnumeric():
                        row += [""] * int(part)
                    else:
                        color = "w" if part.isupper() else "b"
                        piece = part.lower()
                        if piece not in ("p", "r", "n", "b", "k", "q"):
                            print(f"Invalid piece '{part}'")
                            return False
                        row.append(piece + color)
                rows.append(row)

            width = len(rows[0])
            # Check lines length equals
            for row in rows:
                if len(row) != width:
                    print("All rows must have the same width")
                    return False

            next_player = parts[1] if len(parts) > 1 else "w"
            if next_player not in ("w", "b"):
                print(f"Invalid player '{next_player}'")
                return False

            self.player_order = "0w01b2" if next_player == "w" else "0b01w2"
            board = np.array(rows, dtype='O')
            if next_player == "w":
                board = np.rot90(board, 2)
            self.board = board
            self.path = path
            return True
        return False

    def reload(self):
        if self.path is not None:
            self.load_file(self.path)

    def get_fen(self):
        fen = ""
        rows = []
        for y in range(self.board.shape[0]):
            row = ""
            count = 0
            for x in range(self.board.shape[1]):
                piece = self.board[y, x]
                if piece == "":
                    count += 1
                else:
                    if count != 0:
                        row += str(count)
                        count = 0
                    type_, col = piece
                    if col == "w":
                        type_ = type_.upper()
                    row += type_
            if count != 0:
                row += str(count)
            rows.append(row)

        fen += "/".join(rows)
        fen += " " + self.player_order[1]
        fen += " - - 0 1"
        return fen

    def save(self, path: str):
        with open(path, "w") as file:
            file.write(self.player_order)
            for y in range(self.board.shape[0]):
                line = []
                for x in range(self.board.shape[1]):
                    piece = self.board[y, x]
                    if piece == "":
                        piece = "--"
                    line.append(piece)
                file.write("\n" + ",".join(line))
