import random
from constants import *


# use a seed for consistency and debugging
ZOBRIST_SEED = 42739105
random.seed(ZOBRIST_SEED)


class Zobrist:
    def __init__(self):
        self.zobrist_array = {}
        self.castling_rights = [random.getrandbits(64) for _ in range(16)]
        self.en_passant_file = [random.getrandbits(64) for _ in range(8)]
        self.side_to_move = random.getrandbits(64)

        for color in [Color.BLACK, Color.WHITE]:
            for piece in [Piece.PAWN, Piece.KNIGHT, Piece.BISHOP, Piece.ROOK, Piece.QUEEN, Piece.KING]:
                piece = color | piece
                self.zobrist_array[piece] = [random.getrandbits(64) for _ in range(64)]

    def get_zobrist_num(self, piece, square):
        """Takes in a piece (color and type) and square index and returns the zobrist number associated with it."""
        if Piece.get_piece_type(piece) == Piece.NONE:
            return 0
        return self.zobrist_array[piece][square]

    def get_zobrist_en_passant(self, file):
        if not (0 <= file <= 7):
            return 0
        return self.en_passant_file[file]

    def get_zobrist_side_to_move(self, color):
        if color == Color.BLACK:
            return self.side_to_move
        return 0

    def get_zobrist_castling_rights(self, castling_state):
        return self.castling_rights[castling_state]


if __name__ == "__main__":
    z = Zobrist()
