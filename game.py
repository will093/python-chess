from __future__ import annotations

import copy
import os
import re
from pathlib import Path

from enums import ConsoleColors, TeamColour
from exceptions import InvalidMoveError
from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook
from player import Player
from utility import throws_exception

row_names = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H"}
row_indices = {v: k for k, v in row_names.items()}

col_names = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7", 7: "8"}
col_indices = {v: k for k, v in col_names.items()}


class Tile:
    board: Board
    piece: Piece | None
    row: int
    col: int

    @property
    def name(self):
        return f"{row_names[self.row]}{col_names[self.col]}"

    def vacate(self):
        self.piece = None

    def enter(self, piece: Piece) -> Piece | None:
        if taken_piece := self.piece:
            taken_piece.tile = None

        self.piece = piece

    def is_threatened(self, pieces: list[Piece]) -> bool:
        return any(piece.is_alive and self in piece.get_view() for piece in pieces)

    def __init__(self, row: int, col: int, board: Board):
        self.row = row
        self.col = col
        self.board = board
        self.piece = None

    def __str__(self):
        if not self.piece:
            return "-"
        color = (
            ConsoleColors.OKGREEN
            if self.piece.team_colour == TeamColour.WHITE
            else ConsoleColors.FAIL
        )
        return f"{color}{str(self.piece).upper()}{ConsoleColors.ENDC}"

    def to_fen(self):
        return str(self.piece) if self.piece else "-"


class Board:
    tiles: list[list[Tile]]

    @property
    def pieces(self):
        return [tile.piece for tile in self.tiles.flat if tile.piece]

    def __init__(self):
        self.tiles = [[Tile(i, j, self) for i in range(8)] for j in range(8)]

    def move_piece(self, piece: Piece, tile_name: str):
        tile = self.get_tile_by_name(tile_name)
        piece.move(tile)

    def get_tile_by_name(self, tile_name: str):
        for row in self.tiles:
            for tile in row:
                if tile.name == tile_name:
                    return tile
        return None

    def get_tile(self, row: int, col: int):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.tiles[row][col]
        return None

    def __str__(self):
        return "\n".join(
            [" ".join([str(tile) for tile in tile_row]) for tile_row in self.tiles[::-1]]
        )

    def to_fen_row(self, row: list[Tile]) -> str:
        def replace_dashes(s: str):
            return re.sub(r"-+", lambda m: str(len(m.group())), s)

        return replace_dashes("".join([tile.to_fen() for tile in row]))

    def to_fen(self) -> str:
        return "/".join([self.to_fen_row(row) for row in reversed(self.tiles)])


class Game:
    current_turn: int
    players: list[Player]
    board: Board
    full_turn_count: int
    game_log: GameLog | None

    def get_opponent(self, player: Player) -> Player:
        return self.players[0] if player == self.players[1] else self.players[1]

    def __init__(
        self,
        board: Board = None,
        players: list[Player] | None = None,
        current_turn: int | None = None,
        full_turn_count: int | None = None,
        game_log: GameLog = None,
        player_types: tuple[type[Player], type[Player]] | None = None,
    ):
        self.board = board or Board()

        self.players = players or [
            player_types[0](
                team_colour=TeamColour.WHITE,
                pieces=[
                    Pawn(self.board.get_tile_by_name("A2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("B2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("C2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("D2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("E2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("F2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("G2"), TeamColour.WHITE),
                    Pawn(self.board.get_tile_by_name("H2"), TeamColour.WHITE),
                    Rook(self.board.get_tile_by_name("A1"), TeamColour.WHITE),
                    Knight(self.board.get_tile_by_name("B1"), TeamColour.WHITE),
                    Bishop(self.board.get_tile_by_name("C1"), TeamColour.WHITE),
                    Queen(self.board.get_tile_by_name("D1"), TeamColour.WHITE),
                    King(self.board.get_tile_by_name("E1"), TeamColour.WHITE),
                    Bishop(self.board.get_tile_by_name("F1"), TeamColour.WHITE),
                    Knight(self.board.get_tile_by_name("G1"), TeamColour.WHITE),
                    Rook(self.board.get_tile_by_name("H1"), TeamColour.WHITE),
                ],
            ),
            player_types[1](
                team_colour=TeamColour.BLACK,
                pieces=[
                    Pawn(self.board.get_tile_by_name("A7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("B7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("C7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("D7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("E7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("F7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("G7"), TeamColour.BLACK),
                    Pawn(self.board.get_tile_by_name("H7"), TeamColour.BLACK),
                    Rook(self.board.get_tile_by_name("A8"), TeamColour.BLACK),
                    Knight(self.board.get_tile_by_name("B8"), TeamColour.BLACK),
                    Bishop(self.board.get_tile_by_name("C8"), TeamColour.BLACK),
                    Queen(self.board.get_tile_by_name("D8"), TeamColour.BLACK),
                    King(self.board.get_tile_by_name("E8"), TeamColour.BLACK),
                    Bishop(self.board.get_tile_by_name("F8"), TeamColour.BLACK),
                    Knight(self.board.get_tile_by_name("G8"), TeamColour.BLACK),
                    Rook(self.board.get_tile_by_name("H8"), TeamColour.BLACK),
                ],
            ),
        ]
        self.current_turn = current_turn or 0
        self.full_turn_count = full_turn_count or 1
        self.game_log = game_log

    def play(self):
        checkmate = False
        previous_move = ""
        while True:
            checkmate, move = self.start_turn(self.players[self.current_turn], previous_move)
            previous_move = move

            if checkmate:
                break
            self.current_turn = (self.current_turn + 1) % 2

            if self.game_log:
                self.game_log.append(self)
            yield
        print("Game Over")

    def start_turn(self, player: Player, previous_move: str) -> bool:
        os.system("cls" if os.name == "nt" else "clear")  # noqa: S605
        if self.is_checkmate(player):
            print("Checkmate")
            return (True, "")

        from_tile_name, to_tile_name = None, None

        previous_move_message = "" if not previous_move else f" ({previous_move})"
        message = f"{player.team_colour.value} turn{previous_move_message}"
        while True:
            from_tile_name, to_tile_name = player.take_turn(self, message)

            from_tile = self.board.get_tile_by_name(from_tile_name)
            to_tile = self.board.get_tile_by_name(to_tile_name)

            try:
                self.validate_move(from_tile, to_tile, player)
                break
            except InvalidMoveError as e:
                message = e

        self.board.move_piece(from_tile.piece, to_tile_name)

        if player.team_colour == TeamColour.BLACK:
            self.full_turn_count += 1
        return (False, f"{from_tile_name} {to_tile_name}")

    def validate_move(self, from_tile: Tile, to_tile: Tile, player: Player) -> bool:
        if not from_tile:
            raise InvalidMoveError("You must provide a tile to move from")

        if not to_tile:
            raise InvalidMoveError("You must provide a tile to move to")

        if not from_tile.piece:
            raise InvalidMoveError(f"There is no piece on {from_tile.name}")

        is_valid_piece_move, error = from_tile.piece.validate_move(player, to_tile)
        if error:
            raise InvalidMoveError(error)

        if is_valid_piece_move and self.is_moving_into_check(from_tile, to_tile):
            raise InvalidMoveError("You must not move into check")

    def is_moving_into_check(self, from_tile: Tile, to_tile: Tile) -> bool:
        game_copy = copy.deepcopy(self)
        board_copy = game_copy.board
        player_copy = game_copy.players[game_copy.current_turn]

        next_board_from_tile = board_copy.get_tile_by_name(from_tile.name)
        board_copy.move_piece(next_board_from_tile.piece, to_tile.name)
        return game_copy.is_check(player_copy)

    def has_valid_move(self, player: Player) -> bool:
        for piece in player.pieces:
            piece_valid_moves = [
                tile
                for tile in piece.get_view()
                if not throws_exception(self.validate_move, InvalidMoveError)(
                    piece.tile, tile, player
                )
            ]
            if len(piece_valid_moves) > 0:
                return True
        return False

    def is_check(self, player: Player) -> bool:
        enemy_pieces = list(self.get_opponent(player).pieces)
        return player.king.tile.is_threatened(enemy_pieces)

    def is_checkmate(self, player: Player) -> bool:
        return self.is_check(player) and not self.has_valid_move(player)

    def is_stalemate(self, player: Player) -> bool:
        return not self.has_valid_move(player)

    def to_fen(self) -> str:
        fen_board = self.board.to_fen()
        fen_turn = self.players[self.current_turn].team_colour.value[0].lower()
        fen_castle = "-"  # TODO
        fen_en_passant = "-"  # TODO
        fen_half_move_clock = "0"  # TODO
        fen_full_turn_count = self.full_turn_count
        return (
            f"{fen_board} {fen_turn} {fen_castle} "
            f"{fen_en_passant} {fen_half_move_clock} {fen_full_turn_count}"
        )

    @classmethod
    def to_pieces(cls, row: str, row_index: int, board: Board) -> list[Piece]:
        def replace_numbers(string: str):
            return re.sub(r"\d", lambda m: "-" * int(m.group()), string)

        row_with_dashes = replace_numbers(row)

        piece_types: dict[str, Piece] = {
            "p": Pawn,
            "n": Knight,
            "b": Bishop,
            "r": Rook,
            "q": Queen,
            "k": King,
        }
        return [
            piece_types[char.lower()](
                board.get_tile(row_index, col_index),
                TeamColour.BLACK if char.islower() else TeamColour.WHITE,
            )
            for col_index, char in enumerate(row_with_dashes)
            if char != "-"
        ]

    @classmethod
    def from_log(cls, game_log: GameLog, player_types: tuple[type[Player], type[Player]]) -> Game:
        fen = game_log.get_latest_fen()
        fen_item_count = 6
        if not fen or len(fen.split(" ")) != fen_item_count:
            game = Game(game_log=game_log)
            game_log.append(game)
            return game
        [
            fen_board,
            fen_turn,
            fen_castle,
            fen_en_passant,
            fen_half_move_clock,
            fen_full_turn_count,
        ] = fen.split(" ")
        fen_rows = reversed(fen_board.split("/"))
        board = Board()
        pieces = [
            piece
            for row_index, row in enumerate(fen_rows)
            for piece in cls.to_pieces(row, row_index, board)
        ]
        players = [
            player_types[0](
                team_colour=TeamColour.WHITE,
                pieces=[p for p in pieces if p.team_colour == TeamColour.WHITE],
            ),
            player_types[1](
                team_colour=TeamColour.BLACK,
                pieces=[p for p in pieces if p.team_colour == TeamColour.BLACK],
            ),
        ]
        current_turn = 0 if fen_turn == "w" else 1
        return Game(board, players, int(current_turn), int(fen_full_turn_count), game_log)


class GameLog:
    file_name: str

    def __init__(self, file_name: str):
        self.file_name = file_name

    def append(self, game: Game):
        fen = game.to_fen()
        with Path.open(self.file_name, "a+") as f:
            f.write(f"{fen}\n")

    def get_latest_fen(self):
        with Path.open(self.file_name, "a+") as f:
            f.seek(0)
            lines = f.readlines()
            return None if len(lines) == 0 else lines[-1]
