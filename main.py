from __future__ import annotations

import sys

from game import Game, GameLog

if __name__ == "__main__":
    file_name = sys.argv[1] if len(sys.argv) > 1 else None

    if not file_name:
        game = Game()
    else:
        game_log = GameLog(file_name)
        game = Game.from_log(game_log)

    game.play()

# Implement board to FEN
# Implement castling
# Implement en passant
# Implement pawn promotion
# Implement draw by repitition
# Better user messages etc...
