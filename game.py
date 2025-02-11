from __future__ import annotations
from dataclasses import dataclass

from typing import List, Tuple
from numpy.typing import NDArray
import numpy as np
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from enums import TeamColour, bcolors
import os
import copy
from exceptions import InvalidMoveException


class Player():

    team_colour: TeamColour
    is_turn: bool
    pieces: List[Piece]
    
    @property
    def king(self):
        return [piece for piece in self.pieces if isinstance(piece, King)][0]

    def __init__(self, team_colour, pieces):
        self.team_colour = team_colour
        self.pieces = pieces
        self.is_turn = team_colour == TeamColour.WHITE
        
    


row_names = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'}
row_indices = {v: k for k, v in row_names.items()}

col_names = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8'}
col_indices = {v: k for k, v in col_names.items()}


class Tile():

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
        if (taken_piece := self.piece):
            taken_piece.tile = None

        self.piece = piece

    def is_threatened(self, pieces: list[Piece]) -> bool:
        for piece in pieces:
            if (piece.is_alive and self in piece.get_view()):
                return True
        return False

    def __init__(self, row, col, board):
        self.row = row
        self.col = col
        self.board = board
        self.piece = None

    def __str__(self):
        if not self.piece:
            return '-'
        color = bcolors.OKGREEN if self.piece.team_colour == TeamColour.WHITE else bcolors.FAIL
        return '-' if self.piece is None else f'{color}{self.piece}{bcolors.ENDC}'


class Board():

    tiles: NDArray[Tile, Tuple[8, 8]]
    
    @property
    def pieces(self):
        return [tile.piece for tile in self.tiles.flat if tile.piece]

    def __init__(self):
        self.tiles = np.array(
            [[Tile(i, j, self) for i in range(8)] for j in range(8)],
            dtype=Tile
        )

    def move_piece(self, piece: Piece, tileName: str):
        tile = self.get_tile_by_name(tileName)
        piece.move(tile)

    def get_tile_by_name(self, tileName: str):
        for row in self.tiles:
            for tile in row:
                if (tile.name == tileName):
                    return tile
        return None

    def get_tile(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.tiles[row, col]
        return None

    def __str__(self):
        return '\n'.join([' '.join([str(tile) for tile in tileRow]) for tileRow in self.tiles[::-1]])


class Game():

    current_turn: int
    players: list[Player]
    board: Board
    
    def get_opponent(self, player: Player) -> Player:
        return self.players[0] if player == self.players[1] else self.players[1]

    def __init__(self):
        self.board = Board()

        # TODO: pieces should reference the player ?
        self.players = [
            Player(team_colour=TeamColour.WHITE, pieces=[
                Pawn(self.board.get_tile_by_name('A2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('B2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('C2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('D2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('E2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('F2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('G2'), TeamColour.WHITE),
                Pawn(self.board.get_tile_by_name('H2'), TeamColour.WHITE),
                Rook(self.board.get_tile_by_name('A1'), TeamColour.WHITE),
                Knight(self.board.get_tile_by_name('B1'), TeamColour.WHITE),
                Bishop(self.board.get_tile_by_name('C1'), TeamColour.WHITE),
                Queen(self.board.get_tile_by_name('D1'), TeamColour.WHITE),
                King(self.board.get_tile_by_name('E1'), TeamColour.WHITE),
                Bishop(self.board.get_tile_by_name('F1'), TeamColour.WHITE),
                Knight(self.board.get_tile_by_name('G1'), TeamColour.WHITE),
                Rook(self.board.get_tile_by_name('H1'), TeamColour.WHITE),
            ]),
            Player(team_colour=TeamColour.BLACK, pieces=[
                Pawn(self.board.get_tile_by_name('A7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('B7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('C7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('D7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('E7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('F7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('G7'), TeamColour.BLACK),
                Pawn(self.board.get_tile_by_name('H7'), TeamColour.BLACK),
                Rook(self.board.get_tile_by_name('A8'), TeamColour.BLACK),
                Knight(self.board.get_tile_by_name('B8'), TeamColour.BLACK),
                Bishop(self.board.get_tile_by_name('C8'), TeamColour.BLACK),
                Queen(self.board.get_tile_by_name('D8'), TeamColour.BLACK),
                King(self.board.get_tile_by_name('E8'), TeamColour.BLACK),
                Bishop(self.board.get_tile_by_name('F8'), TeamColour.BLACK),
                Knight(self.board.get_tile_by_name('G8'), TeamColour.BLACK),
                Rook(self.board.get_tile_by_name('H8'), TeamColour.BLACK),
            ])
        ]
        self.current_turn = 0

    def play(self):
        checkmate = False
        while True:
            checkmate = self.start_turn(self.players[self.current_turn])
            if checkmate:
                break
            self.current_turn = (self.current_turn + 1) % 2
        print('Game Over')

    def start_turn(self, player: Player) -> bool:
        if (self.is_checkmate(player)):
            print("Checkmate")
            return True
        
        # os.system('cls' if os.name == 'nt' else 'clear')
        print(self.board)
        print("\n")
        print(f"{player.team_colour.value} turn")
        move = input()
        input_tiles = move.split(" ")

        if (len(input_tiles) != 2):
            print("Invalid move, please provide a move in the correct format eg. 'A2 A4'")
            return self.start_turn(player)

        from_tile_name, to_tile_name = input_tiles

        from_tile = self.board.get_tile_by_name(from_tile_name)
        to_tile = self.board.get_tile_by_name(to_tile_name)

        try:
            self.validate_move(from_tile, to_tile, player)
        except InvalidMoveException as e:
            print(e)
            return self.start_turn(player)

        self.board.move_piece(from_tile.piece, to_tile_name)

        return False

    def validate_move(self, from_tile: Tile, to_tile: Tile, player: Player) -> bool:
        if (not from_tile):
            raise InvalidMoveException("You must provide a tile to move from")

        if (not to_tile):
            raise InvalidMoveException("You must provide a tile to move to")

        if (not from_tile.piece):
            raise InvalidMoveException(f"There is no piece on {from_tile.name}")

        is_valid_piece_move, error = from_tile.piece.validate_move(player, to_tile)
        if (error):
            raise InvalidMoveException(error)

        if (is_valid_piece_move and self.is_moving_into_check(from_tile, to_tile)):
            raise InvalidMoveException("You must not move into check")

    def is_moving_into_check(self, from_tile: Tile, to_tile: Tile) -> bool:
        game_copy = copy.deepcopy(self)
        board_copy = game_copy.board
        player_copy = game_copy.players[game_copy.current_turn]

        next_board_from_tile = board_copy.get_tile_by_name(from_tile.name)
        board_copy.move_piece(next_board_from_tile.piece, to_tile.name)
        return game_copy.is_check(player_copy)

    def has_valid_move(self, player: Player) -> bool:
        for piece in player.pieces:
            if len([tile for tile in piece.get_view() if self.validate_move(piece.tile, tile, player)]) > 0:
                return True
        return False

    def is_check(self, player: Player) -> bool:
        enemy_pieces = [piece for piece in self.get_opponent(player).pieces]
        return player.king.tile.is_threatened(enemy_pieces)

    def is_checkmate(self, player: Player) -> bool:
        return self.is_check(player) and not self.has_valid_move(player)

    def is_stalemate(self, player: Player) -> bool:
        return not self.has_valid_move(player)
