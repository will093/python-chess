from __future__ import annotations
from game import Game
import pickle
import signal
import sys

if __name__ == '__main__':
    file_name = sys.argv[1] if len(sys.argv) > 1 else None

    if (not file_name):
        game = Game()
    else:
        with open(file_name, "rb") as f:
            game = pickle.load(f)

    def sigint_handler(signal, frame):
        if (file_name):
            print('Serializing game')
            # pickle.dump(game, open(file_name, "wb"))
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)
    
    game.play()

# Implement board to FEN
# Implement castling
# Implement en passant
# Implement pawn promotion
# Implement draw by repitition
# Better user messages etc...
