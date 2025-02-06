from __future__ import annotations
from enums import PieceType, PieceDirection, TeamColour
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Player, Tile


class Piece():

    @property
    @abc.abstractmethod
    def type(self) -> PieceType:
        return
    team_colour: TeamColour  # TODO: Readonly property
    tile: Tile | None

    @property
    def is_alive(self):
        return self.tile is not None

    def __init__(self, tile, team_colour):
        self.tile = tile
        self.tile.piece = self
        self.team_colour = team_colour

    def __str__(self):
        return 'K'

    @abc.abstractmethod
    def get_view(self) -> list[Tile]:
        return []

    '''
        Return a list of tiles in the line of sight of a piece in the given direction. 
        The view ends at edge of board or the first tile where there is a piece.
    '''
    def get_line_of_sight(self, directions: list[PieceDirection], distance: int | None = None, include_opponent_occupied: bool = True) -> list[Tile]:
        tiles = []
        for direction in directions:
            direction_tiles = []
            current_tile = self.tile
            while not distance or (len(direction_tiles) < distance):
                next_tile = current_tile.board.get_tile(current_tile.col + direction.value[1], current_tile.row + direction.value[0])

                if not next_tile:
                    break
                elif (not next_tile.piece):
                    direction_tiles += [next_tile]
                elif (next_tile.piece.team_colour != self.team_colour and include_opponent_occupied):
                    direction_tiles += [next_tile]
                    break
                else:
                    break
                current_tile = next_tile

            tiles += direction_tiles

        return tiles

    def move(self, new_tile: Tile) -> Piece | None:
        self.tile.vacate()

        self.tile = new_tile
        return self.tile.enter(self)

    def validate_move(self, player: Player, to_tile: Tile) -> (bool, str):
        if (not self.tile):
            return (False, f"No piece on {self.tile.name}")
        if (self.team_colour != player.team_colour):
            return (False, f"{self.tile.piece.type} on {self.tile.name} is not yours")

        available_moves = self.get_view()

        to_tile_in_view = next((x for x in available_moves if x.name == to_tile.name), None)
        if not to_tile_in_view:
            return (False, f"{self.type} cannot move to {to_tile.name}")

        return (True, "")


class Pawn(Piece):

    type = "Pawn"
    has_moved: bool

    def __init__(self, tile, team_colour):
        super().__init__(tile, team_colour)
        self.has_moved = False

    def get_view(self) -> list[Tile]:
        move_direction = PieceDirection.UP if self.team_colour == TeamColour.WHITE else PieceDirection.DOWN
        distance = 1 if self.has_moved else 2
        attack_directions = [PieceDirection.UPRIGHT, PieceDirection.UPLEFT] if self.team_colour == TeamColour.WHITE else [
            PieceDirection.DOWNRIGHT, PieceDirection.DOWNLEFT]
        tiles = self.get_line_of_sight(
            directions=[move_direction], distance=distance, include_opponent_occupied=False)
        attackable_tiles = self.get_line_of_sight(directions=attack_directions, distance=1)
        tiles += [t for t in attackable_tiles if t.piece and t.piece.team_colour != self.team_colour]

        return tiles

    def move(self, tile) -> Piece | None:
        self.has_moved = True
        return super().move(tile)

    def __str__(self):
        return 'P'


class Rook(Piece):

    type = "Rook"

    def get_view(self) -> list[Tile]:
        return self.get_line_of_sight(directions=[PieceDirection.UP, PieceDirection.RIGHT, PieceDirection.DOWN, PieceDirection.LEFT])

    def __str__(self):
        return 'R'


class Knight(Piece):

    type = "Knight"

    def get_view(self) -> list[Tile]:
        tiles = [t for t in [
            self.tile.board.get_tile(self.tile.col + 1, self.tile.row + 2),
            self.tile.board.get_tile(self.tile.col - 1, self.tile.row + 2),
            self.tile.board.get_tile(self.tile.col - 2, self.tile.row + 1),
            self.tile.board.get_tile(self.tile.col - 2, self.tile.row - 1),
            self.tile.board.get_tile(self.tile.col - 1, self.tile.row - 2),
            self.tile.board.get_tile(self.tile.col + 1, self.tile.row - 2),
            self.tile.board.get_tile(self.tile.col + 2, self.tile.row - 1),
            self.tile.board.get_tile(self.tile.col + 2, self.tile.row + 1),
        ] if t and (not t.piece or t.piece.team_colour != self.team_colour)]
        
        print([t.name for t in tiles])
        return tiles

    def __str__(self):
        return 'N'


class Bishop(Piece):

    type = "Bishop"

    def get_view(self) -> list[Tile]:
        return self.get_line_of_sight(directions=[PieceDirection.UPRIGHT, PieceDirection.DOWNRIGHT, PieceDirection.DOWNLEFT, PieceDirection.UPLEFT])

    def __str__(self):
        return 'B'


class Queen(Piece):

    type = "Queen"

    def get_view(self) -> list[Tile]:
        return self.get_line_of_sight(directions=[PieceDirection.UP, PieceDirection.RIGHT, PieceDirection.DOWN, PieceDirection.LEFT, PieceDirection.UPRIGHT, PieceDirection.DOWNRIGHT, PieceDirection.DOWNLEFT, PieceDirection.UPLEFT])

    def __str__(self):
        return 'Q'


class King(Piece):
    type = "King"

    def get_view(self) -> list[Tile]:
        return self.get_line_of_sight(directions=[PieceDirection.UP, PieceDirection.RIGHT, PieceDirection.DOWN, PieceDirection.LEFT, PieceDirection.UPRIGHT, PieceDirection.DOWNRIGHT, PieceDirection.DOWNLEFT, PieceDirection.UPLEFT], distance=1)
