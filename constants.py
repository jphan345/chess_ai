# constants.py

from enum import IntEnum


class Color(IntEnum):
    # pieces and colors and be bitwise-or together
    # first 2 bits are the color
    # e.g. 0b01101 -> 1 | 101 -> BLACK | KING
    BLACK = 8
    WHITE = 0

    MASK = 0b1000

    @staticmethod
    def get_piece_color(piece):
        return piece & Color.MASK


class Piece(IntEnum):
    # pieces and colors and be bitwise-or together
    # last 3 bits are the piece
    # e.g. 0b1101 -> 1 | 110 -> BLACK | KING
    NONE = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

    MASK = 0b0111

    PAWN_VALUE = 100
    KNIGHT_VALUE = 300
    BISHOP_VALUE = 310
    ROOK_VALUE = 500
    QUEEN_VALUE = 900

    @staticmethod
    def get_piece_type(piece):
        return piece & Piece.MASK

    @staticmethod
    def get_piece_value(piece):
        piece_type = Piece.get_piece_type(piece)

        if piece_type == Piece.PAWN:
            return Piece.PAWN_VALUE
        elif piece_type == Piece.KNIGHT:
            return Piece.KNIGHT_VALUE
        elif piece_type == Piece.BISHOP:
            return Piece.BISHOP_VALUE
        elif piece_type == Piece.ROOK:
            return Piece.ROOK_VALUE
        elif piece_type == Piece.QUEEN:
            return Piece.QUEEN_VALUE

        return 0


class BoardHelper(IntEnum):
    A1 = 0
    B1 = 1
    C1 = 2
    D1 = 3
    E1 = 4
    F1 = 5
    G1 = 6
    H1 = 7
    A2 = 8
    B2 = 9
    C2 = 10
    D2 = 11
    E2 = 12
    F2 = 13
    G2 = 14
    H2 = 15
    A3 = 16
    B3 = 17
    C3 = 18
    D3 = 19
    E3 = 20
    F3 = 21
    G3 = 22
    H3 = 23
    A4 = 24
    B4 = 25
    C4 = 26
    D4 = 27
    E4 = 28
    F4 = 29
    G4 = 30
    H4 = 31
    A5 = 32
    B5 = 33
    C5 = 34
    D5 = 35
    E5 = 36
    F5 = 37
    G5 = 38
    H5 = 39
    A6 = 40
    B6 = 41
    C6 = 42
    D6 = 43
    E6 = 44
    F6 = 45
    G6 = 46
    H6 = 47
    A7 = 48
    B7 = 49
    C7 = 50
    D7 = 51
    E7 = 52
    F7 = 53
    G7 = 54
    H7 = 55
    A8 = 56
    B8 = 57
    C8 = 58
    D8 = 59
    E8 = 60
    F8 = 61
    G8 = 62
    H8 = 63

    @staticmethod
    def get_file(square_index):
        return square_index % 8

    @staticmethod
    def get_rank(square_index):
        return square_index // 8


class Offset(IntEnum):
    LEFT = -1
    RIGHT = 1
    DOWN = -8
    UP = 8
    BOTTOM_RIGHT = -7
    TOP_LEFT = 7
    BOTTOM_LEFT = -9
    TOP_RIGHT = 9

    @staticmethod
    def to_name(offset):
        offset_to_name = {
            -1: "LEFT",
            1: "RIGHT",
            -8: "DOWN",
            8: "UP",
            -7: "BOTTOM_RIGHT",
            7: "TOP_LEFT",
            -9: "BOTTOM_LEFT",
            9: "TOP_RIGHT"
        }

        return offset_to_name[offset]
