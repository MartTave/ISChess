from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import numpy as np
from PyQt6.QtCore import QTimer

from BoardManager import BoardManager
from BotWidget import BotWidget
from ChessRules import move_is_valid
from ParallelPlayer import ParallelTurn
from PieceManager import PieceManager
from Player import Player

if TYPE_CHECKING:
    from ChessArena import ChessArena


class GameManager:
    MIN_WAIT = 500
    GRACE_RATIO = 0.05

    def __init__(self, arena: ChessArena):
        self.arena: ChessArena = arena
        self.board_manager: BoardManager = BoardManager()
        self.players: list[Player] = []
        self.turn: int = 0
        self.nbr_turn_to_play: int = 0
        self.current_player: Optional[ParallelTurn] = None
        self.player_finished: bool = False
        self.auto_playing: bool = False
        self.timeout = QTimer()
        self.timeout.timeout.connect(lambda: self.end_turn(forced=True))
        self.min_wait = QTimer()
        self.min_wait.timeout.connect(self.end_if_finished)

    def reset(self):
        """Reset the game"""
        self.players = []
        self.turn = 0

    def add_player(self, color: str, widget: BotWidget):
        """
        Add a player to the game
        :param color: The player's color
        :param widget: The bot widget
        """
        player = Player(color, widget)
        self.players.append(player)

    def get_sequence(self, full: bool = False) -> str:
        """
        Get the player sequence
        :param full: If ``True``, the full sequence is returned.
                     If ``False``, only the part related to the current player is returned
        :return: The player sequence
        """
        if full:
            start = self.board_manager.player_order[:3*self.turn]
            end = self.board_manager.player_order[3*self.turn:]
            return end + start
        return self.board_manager.player_order[self.turn * 3:self.turn * 3 + 3]

    def next(self) -> bool:
        """
        Start a new turn

        This function calls the next player's bot function with the appropriate arguments and starts a timeout timer.
        :return: ``True`` if successful, ``False`` if a turn is already in progress
        """
        if self.current_player is not None:
            print("Cannot launch new turn while already processing")
            return False

        board = self.board_manager.board
        player: Player = self.players[self.turn]
        budget: float = player.get_budget()
        sequence: str = self.get_sequence()
        func_name, func = player.get_func()
        print(f"Player {self.turn}'s turn: {func_name} (budget: {budget:.2f}s)")

        self.player_finished = False
        self.current_player = ParallelTurn(
            func,
            sequence,
            np.rot90(board, int(sequence[2])),
            budget
        )
        self.current_player.setTerminationEnabled(True)
        self.current_player.finished.connect(self.on_player_finished)
        self.current_player.start()

        # Timer to call
        #self.timeout.singleShot(int(budget * 1000 * 1.05), lambda: self.end_turn(forced=True))
        budget_ms: int = int(budget * 1000 * (1 + self.GRACE_RATIO))
        self.timeout.start(budget_ms)
        if self.MIN_WAIT < budget_ms:
            self.min_wait.start(self.MIN_WAIT)

        return True

    def on_player_finished(self):
        """Callback called by the player when it has finished playing"""
        self.player_finished = True

    def end_if_finished(self):
        """Callback called after a minimum waiting time to end the turn if the player has already finished playing"""
        if self.player_finished:
            self.end_turn()

    def end_turn(self, forced: bool = False) -> bool:
        """
        End the current turn

        If this function is called to prematurely end a player's turn
        because of a timeout, ``forced`` should be set to ``True``
        :param forced: If ``True``, prints a message telling the user the current player
                       took too long and was terminated early
        :return: ``True`` if successful, ``False`` if no turn was in progress
        """
        if self.current_player is None:
            return False

        self.timeout.stop()
        if forced:
            print("Player took too long, terminating thread")

        self.current_player.terminate()
        self.current_player.quit()

        self.apply_move()

        if self.check_game_end():
            return True

        self.current_player = None
        self.turn += 1
        self.turn %= len(self.players)
        self.arena.setup_board()

        if self.auto_playing:
            self.nbr_turn_to_play -= 1
            if self.nbr_turn_to_play <= 0:
                self.stop()
            else:
                self.next()
        return True

    def start(self) -> bool:
        """
        Start a series of turns

        :return: ``True`` if successful, ``False`` if the number of turns to play is <= 0 or if already autoplaying
        """
        self.nbr_turn_to_play = self.arena.autoMovesCount.value()
        if self.nbr_turn_to_play <= 0:
            self.arena.show_message(f"Cannot start auto-playing, number of moves is {self.nbr_turn_to_play}, must be >0")
            return False

        self.arena.startStop.setIcon(self.arena.STOP_ICON)
        if self.auto_playing:
            print("Already auto-playing")
            return False
        self.auto_playing = True
        print(f"Starting auto-play for {self.nbr_turn_to_play} moves")
        self.next()
        return True

    def stop(self):
        """
        Stop the game if currently autoplaying

        This does not immediately end the running turn but lets it complete gracefully
        """
        self.arena.startStop.setIcon(self.arena.START_ICON)
        if not self.auto_playing:
            print("Already stopped")
            return
        self.auto_playing = False

    def start_stop(self):
        """
        Toggle autoplaying

        This function calls either `start` or `stop` depending on the current state
        """
        if self.auto_playing:
            print("Stopping")
            self.stop()
        else:
            print("Starting")
            self.start()

    def undo_move(self):
        """Undo the last move, if any"""
        print("Undoing")

    def redo_move(self):
        """Redo the next move, if any"""
        print("Redoing")

    def apply_move(self) -> bool:
        """
        Try to apply the move chosen by the current player
        :return: ``True`` if successful, ``False`` if the move is invalid
        """
        move: tuple[tuple[int, int], tuple[int, int]] = self.current_player.next_move
        start, end = move
        color: str = self.current_player.color
        color_name: str = PieceManager.COLOR_NAMES[color]
        board = self.current_player.board

        if not move_is_valid(self.get_sequence(True), move, board):
            print(f"Invalid move from {start} to {end}")
            return False

        start_piece = board[start[0], start[1]]
        end_piece = board[end[0], end[1]]

        print(f"{color_name} moved {PieceManager.get_piece_name(start_piece)} from {start} to {end}")

        # Capture
        if end_piece != "":
            print(f"{color_name} captured {PieceManager.get_piece_name(end_piece)}")

        # Apply move
        board[end[0], end[1]] = start_piece
        board[start[0], start[1]] = ""

        # Promotion
        if start_piece[0] == "p" and end[0] == board.shape[0] - 1:
            board[end[0], end[1]] = "q" + self.current_player.color

        col1 = "ABCDEFGH"[7 - start[1]]
        col2 = "ABCDEFGH"[7 - end[1]]
        row1 = start[0] + 1
        row2 = end[0] + 1
        self.arena.push_move_to_history(f"{col1}{row1} -> {col2}{row2}", color_name)

        return True

    def check_game_end(self):
        board = self.current_player.board
        current_color = self.current_player.color
        for y in range(board.shape[0]):
            for x in range(board.shape[1]):
                piece = board[y, x]
                if piece and piece[0] == "k" and piece[1] != current_color:
                    return

        color_name: str = PieceManager.COLOR_NAMES[current_color]
        self.arena.show_message(f"{color_name} player won the match", "End of game")
        self.stop()
