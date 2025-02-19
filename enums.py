from enum import Enum


class PieceDirection(Enum):
    UP = (0, 1)
    UPRIGHT = (1, 1)
    RIGHT = (1, 0)
    DOWNRIGHT = (1, -1)
    DOWN = (0, -1)
    DOWNLEFT = (-1, -1)
    LEFT = (-1, 0)
    UPLEFT = (-1, 1)


class PieceType(Enum):
    PAWN = "Pawn"
    ROOK = "Rook"
    KNIGHT = "Knight"
    BISHOP = "Bishop"
    QUEEN = "Queen"
    KING = "King"


class TeamColour(Enum):
    WHITE = "White"
    BLACK = "Black"


class ConsoleColors:
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
