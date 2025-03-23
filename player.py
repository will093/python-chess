from __future__ import annotations

import abc
import os
import random
from typing import TYPE_CHECKING

import httpx

from enums import TeamColour
from pieces import King, Piece

if TYPE_CHECKING:
    from game import Game


class Player:
    team_colour: TeamColour
    is_turn: bool
    pieces: list[Piece]

    @property
    def king(self):
        return next(piece for piece in self.pieces if isinstance(piece, King))

    def __init__(self, team_colour: TeamColour, pieces: list[Piece]):
        self.team_colour = team_colour
        self.pieces = pieces
        self.is_turn = team_colour == TeamColour.WHITE

    @abc.abstractmethod
    def take_turn(self, *_: list[any], **__: dict[str, any]) -> tuple[str, str]:
        return


class CommandLinePlayer(Player):
    def take_turn(
        self, game: Game, message: str, *_: list[any], **__: dict[str, any]
    ) -> tuple[str, str]:
        print(message)
        print("\n")
        print(game.board)
        print("\n")
        move = input("Enter your move: ")
        os.system("cls" if os.name == "nt" else "clear")  # noqa: S605
        input_tiles = move.split(" ")

        if len(input_tiles) != 2:
            print("Invalid move, please provide a move in the correct format eg. 'A2 A4'")
            return self.take_turn(game, message)

        return (input_tiles[0].upper(), input_tiles[1].upper())


class RandomMovePlayer(Player):
    def take_turn(self, *_: list[any], **__: dict[str, any]) -> tuple[str, str]:
        piece = random.choice(  # noqa: S311
            [piece for piece in self.pieces if piece.is_alive and len(piece.get_view())]
        )
        to_tile = random.choice(piece.get_view())  # noqa: S311

        return (piece.tile.name, to_tile.name)


class ChessApiPlayer(Player):
    url = "https://chess-api.com/v1"

    def take_turn(self, game: Game, *_: list[any], **__: dict[str, any]) -> tuple[str, str]:
        fen = game.to_fen()
        response = httpx.post(self.url, data={"fen": fen})
        response_json = response.json()
        return (response_json["from"].upper(), response_json["to"].upper())
