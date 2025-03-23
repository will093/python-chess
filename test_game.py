from collections.abc import Callable
from unittest.mock import Mock

import pytest

from exceptions import InvalidMoveError
from game import Game
from player import Player

initial_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"

"""
G6 White Queen
A7 White Queen
H8 Black King
"""
endgame_position = "7k/Q7/6K1/8/8/8/8/8 w - - 0 1"


@pytest.fixture
def game_factory():
    def factory(fen: str) -> Game:
        mocked_log = Mock()
        mocked_log.append.return_value = None
        mocked_log.get_latest_fen.return_value = fen

        return Game.from_log(mocked_log, player_types=(Player, Player))

    return factory


def test_pawn_movement(game_factory: Callable[[str], Game]):
    game = game_factory(initial_position)
    game_generator = game.play()

    white_a_pawn = game.board.get_tile_by_name("A2").piece
    black_a_pawn = game.board.get_tile_by_name("A7").piece
    black_h_pawn = game.board.get_tile_by_name("H7").piece

    game.players[0].take_turn = Mock(return_value=("A2", "A4"))
    next(game_generator)
    assert white_a_pawn.tile.name == "A4"

    game.players[1].take_turn = Mock(return_value=("A7", "A6"))

    next(game_generator)
    assert black_a_pawn.tile.name == "A6"

    game.players[0].take_turn = Mock(return_value=("A4", "A5"))
    next(game_generator)
    assert white_a_pawn.tile.name == "A5"

    game.players[1].take_turn = Mock(side_effect=[("A6", "A5"), ("H7", "H5")])
    next(game_generator)
    assert black_a_pawn.tile.name == "A6"
    assert white_a_pawn.tile.name == "A5"
    assert black_h_pawn.tile.name == "H5"

    assert game.players[1].take_turn.call_count == 2
    assert isinstance(game.players[1].take_turn.call_args_list[1][0][1], InvalidMoveError)


def test_pawn_capture(game_factory: Callable[[str], Game]):
    game = game_factory(initial_position)
    game_generator = game.play()

    white_e_pawn = game.board.get_tile_by_name("E2").piece
    black_d_pawn = game.board.get_tile_by_name("D7").piece

    game.players[0].take_turn = Mock(return_value=("E2", "E4"))
    next(game_generator)

    game.players[1].take_turn = Mock(return_value=("D7", "D5"))
    next(game_generator)

    game.players[0].take_turn = Mock(return_value=("E4", "D5"))
    next(game_generator)

    assert white_e_pawn.tile.name == "D5"
    assert white_e_pawn.is_alive is True
    assert black_d_pawn.tile is None
    assert black_d_pawn.is_alive is False


def test_checkmate(game_factory: Callable[[str], Game]):
    game = game_factory(endgame_position)
    game_generator = game.play()

    white_player = game.players[0]
    black_player = game.players[1]

    white_queen = game.board.get_tile_by_name("A7").piece

    white_player.take_turn = Mock(return_value=("A7", "G7"))
    next(game_generator)

    assert white_queen.tile.name == "G7"
    assert white_queen.is_alive is True

    assert game.is_check(black_player) is True
    assert game.is_checkmate(black_player) is True

    assert game.is_check(white_player) is False
    assert game.is_checkmate(white_player) is False


def test_check(game_factory: Callable[[str], Game]):
    game = game_factory(endgame_position)
    game_generator = game.play()

    white_player = game.players[0]
    black_player = game.players[1]

    white_queen = game.board.get_tile_by_name("A7").piece

    white_player.take_turn = Mock(return_value=("A7", "A1"))
    next(game_generator)

    assert white_queen.tile.name == "A1"
    assert white_queen.is_alive is True

    assert game.is_check(black_player) is True
    assert game.is_checkmate(black_player) is False

    assert game.is_check(white_player) is False
    assert game.is_checkmate(white_player) is False
