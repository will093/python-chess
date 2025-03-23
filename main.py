from __future__ import annotations

import sys

from game import Game, GameLog
from player import ChessApiPlayer, CommandLinePlayer

white_player_type = CommandLinePlayer
black_player_type = ChessApiPlayer

if __name__ == "__main__":
    file_name = sys.argv[1] if len(sys.argv) > 1 else None

    if not file_name:
        game = Game(player_types=(white_player_type, black_player_type))
    else:
        game_log = GameLog(file_name)
        game = Game.from_log(game_log, player_types=(white_player_type, black_player_type))

    for _ in game.play():
        pass
