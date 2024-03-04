from constants import *


class Move:
    # flags
    NO_FLAG = 0b0000
    EN_PASSANT_CAPTURE_FLAG = 0b0001
    CASTLE_FLAG = 0b0010
    PAWN_TWO_UP_FLAG = 0b0011

    PROMOTE_TO_QUEEN_FLAG = 0b0100
    PROMOTE_TO_KNIGHT_FLAG = 0b0101
    PROMOTE_TO_ROOK_FLAG = 0b0110
    PROMOTE_TO_BISHOP_FLAG = 0b0111

    # masks
    START_SQUARE_MASK = 0b0000000000111111
    TARGET_SQUARE_MASK = 0b0000111111000000
    FLAG_MASK = 0b1111000000000000

    def __init__(self, start_square, target_square, flag=NO_FLAG):
        promotion_pieces = {
            Move.PROMOTE_TO_QUEEN_FLAG: Piece.QUEEN,
            Move.PROMOTE_TO_BISHOP_FLAG: Piece.BISHOP,
            Move.PROMOTE_TO_ROOK_FLAG: Piece.ROOK,
            Move.PROMOTE_TO_KNIGHT_FLAG: Piece.KNIGHT,
            Move.NO_FLAG: Piece.NONE
        }

        # 16bit move val, format is:
        # Bits 0 - 5: start square index
        # Bits 6 - 11: target square index
        # Bits 12 - 15: flags (promotion type, etc)
        self.value = start_square | target_square << 6 | flag << 12

        # attributes
        self.isNull = self.value == 0
        self.start_square = self.value & Move.START_SQUARE_MASK
        self.target_square = (self.value & Move.TARGET_SQUARE_MASK) >> 6
        self.flag = (self.value & Move.FLAG_MASK) >> 12

        # Move.PROMOTE_TO_QUEEN_FLAG is the smallest bit value, so checking if any flag is >= it means it's a promotion
        self.is_promotion = self.flag >= Move.PROMOTE_TO_QUEEN_FLAG
        self.promotion_piece_type = promotion_pieces[self.flag] if self.is_promotion else Piece.NONE

    def __str__(self):
        flags = {
            Move.EN_PASSANT_CAPTURE_FLAG: "EN_PASSANT_CAPTURE_FLAG",
            Move.CASTLE_FLAG: "CASTLE_FLAG",
            Move.PAWN_TWO_UP_FLAG: "PAWN_TWO_UP_FLAG",
            Move.PROMOTE_TO_QUEEN_FLAG: "PROMOTE_TO_QUEEN_FLAG",
            Move.PROMOTE_TO_KNIGHT_FLAG: "PROMOTE_TO_KNIGHT_FLAG",
            Move.PROMOTE_TO_ROOK_FLAG: "PROMOTE_TO_ROOK_FLAG",
            Move.PROMOTE_TO_BISHOP_FLAG: "PROMOTE_TO_BISHOP_FLAG",
            Move.NO_FLAG: "NO_FLAG"
        }
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        start_square = files[BoardHelper.get_file(self.start_square)] + str(BoardHelper.get_rank(self.start_square) + 1)
        target_square = files[BoardHelper.get_file(self.target_square)] + str(BoardHelper.get_rank(self.target_square) + 1)

        return f"Move(start={start_square}, target={target_square}, flag={flags[self.flag]})"

    def __eq__(self, other):
        return other.value == self.value
