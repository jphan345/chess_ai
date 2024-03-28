from constants import *
from board import Board
from move import Move


# PeSTO's Evaluation Function
# https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
mg_pawn_table = [
      0,   0,   0,   0,   0,   0,  0,   0,
     98, 134,  61,  95,  68, 126, 34, -11,
     -6,   7,  26,  31,  65,  56, 25, -20,
    -14,  13,   6,  21,  23,  12, 17, -23,
    -27,  -2,  -5,  12,  17,   6, 10, -25,
    -26,  -4,  -4, -10,   3,   3, 33, -12,
    -35,  -1, -20, -23, -15,  24, 38, -22,
      0,   0,   0,   0,   0,   0,  0,   0,
]

eg_pawn_table = [
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0,
]

mg_knight_table = [
    -167, -89, -34, -49,  61, -97, -15, -107,
     -73, -41,  72,  36,  23,  62,   7,  -17,
     -47,  60,  37,  65,  84, 129,  73,   44,
      -9,  17,  19,  53,  37,  69,  18,   22,
     -13,   4,  16,  13,  28,  19,  21,   -8,
     -23,  -9,  12,  10,  19,  17,  25,  -16,
     -29, -53, -12,  -3,  -1,  18, -14,  -19,
    -105, -21, -58, -33, -17, -28, -19,  -23,
]

eg_knight_table = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64,
]

mg_bishop_table = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
]

eg_bishop_table = [
    -14, -21, -11,  -8, -7,  -9, -17, -24,
     -8,  -4,   7, -12, -3, -13,  -4, -14,
      2,  -8,   0,  -1, -2,   6,   0,   4,
     -3,   9,  12,   9, 14,  10,   3,   2,
     -6,   3,  13,  19,  7,  10,  -3,  -9,
    -12,  -3,   8,  10, 13,   3,  -7, -15,
    -14, -18,  -7,  -1,  4,  -9, -15, -27,
    -23,  -9, -23,  -5, -9, -16,  -5, -17,
]

mg_rook_table = [
     32,  42,  32,  51, 63,  9,  31,  43,
     27,  32,  58,  62, 80, 67,  26,  44,
     -5,  19,  26,  36, 17, 45,  61,  16,
    -24, -11,   7,  26, 24, 35,  -8, -20,
    -36, -26, -12,  -1,  9, -7,   6, -23,
    -45, -25, -16, -17,  3,  0,  -5, -33,
    -44, -16, -20,  -9, -1, 11,  -6, -71,
    -19, -13,   1,  17, 16,  7, -37, -26,
]

eg_rook_table = [
    13, 10, 18, 15, 12,  12,   8,   5,
    11, 13, 13, 11, -3,   3,   8,   3,
     7,  7,  7,  5,  4,  -3,  -5,  -3,
     4,  3, 13,  1,  2,   1,  -1,   2,
     3,  5,  8,  4, -5,  -6,  -8, -11,
    -4,  0, -5, -1, -7, -12,  -8, -16,
    -6, -6,  0,  2, -9,  -9, -11,  -3,
    -9,  2,  3, -1, -5, -13,   4, -20,
]

mg_queen_table = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
]

eg_queen_table = [
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  57,  40,  57,  36,
    -18,  28,  19,  47,  31,  34,  39,  23,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41,
]

mg_king_table = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
]

eg_king_table = [
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43
]

mg_piece_table = {
    Piece.PAWN: mg_pawn_table,
    Piece.KNIGHT: mg_knight_table,
    Piece.BISHOP: mg_bishop_table,
    Piece.ROOK: mg_rook_table,
    Piece.QUEEN: mg_queen_table,
    Piece.KING: mg_king_table
}

eg_piece_table = {
    Piece.PAWN: eg_pawn_table,
    Piece.KNIGHT: eg_knight_table,
    Piece.BISHOP: eg_bishop_table,
    Piece.ROOK: eg_rook_table,
    Piece.QUEEN: eg_queen_table,
    Piece.KING: eg_king_table
}

mg_piece_value = {
    Piece.PAWN: 82,
    Piece.KNIGHT: 337,
    Piece.BISHOP: 365,
    Piece.ROOK: 477,
    Piece.QUEEN: 1025,
    Piece.KING: 0
}

eg_piece_value = {
    Piece.PAWN: 94,
    Piece.KNIGHT: 281,
    Piece.BISHOP: 297,
    Piece.ROOK: 512,
    Piece.QUEEN: 936,
    Piece.KING: 0
}


def flip_index(i):
    """Flips the square index of the board to the other side to represent the other color."""
    return i ^ 56


class Evaluation:
    def __init__(self, board):
        self.board = board

        self.mg_table = {}
        self.eg_table = {}

        for piece in [Piece.PAWN, Piece.KNIGHT, Piece.BISHOP, Piece.ROOK, Piece.QUEEN, Piece.KING]:
            self.mg_table[piece | Color.WHITE] = [0 for _ in range(64)]
            self.eg_table[piece | Color.WHITE] = [0 for _ in range(64)]
            self.mg_table[piece | Color.BLACK] = [0 for _ in range(64)]
            self.eg_table[piece | Color.BLACK] = [0 for _ in range(64)]

            for square in range(64):
                self.mg_table[piece | Color.WHITE][square] = mg_piece_value[piece] + mg_piece_table[piece][square]
                self.eg_table[piece | Color.WHITE][square] = eg_piece_value[piece] + eg_piece_table[piece][square]
                self.mg_table[piece | Color.BLACK][square] = mg_piece_value[piece] + mg_piece_table[piece][flip_index(square)]
                self.eg_table[piece | Color.BLACK][square] = eg_piece_value[piece] + eg_piece_table[piece][flip_index(square)]

    def evaluate(self):
        # evaluate endgame mop up
        white_material = self.count_material(Color.WHITE)
        black_material = self.count_material(Color.BLACK)

        white_mop_up = self.mop_up_eval(Color.WHITE, white_material, black_material)
        black_mop_up = self.mop_up_eval(Color.BLACK, black_material, white_material)
        mop_up_eval = white_mop_up - black_mop_up

        # evaluate pieces value
        game_phase_inc = {
            Piece.PAWN: 0,
            Piece.KNIGHT: 1,
            Piece.BISHOP: 1,
            Piece.ROOK: 2,
            Piece.QUEEN: 4,
            Piece.KING: 0
        }

        mg = {Color.WHITE: 0, Color.BLACK: 0}
        eg = {Color.WHITE: 0, Color.BLACK: 0}
        game_phase = 0
        for square in range(64):
            piece = self.board.board[square]
            piece_type = Piece.get_piece_type(piece)
            piece_color = Color.get_piece_color(piece)

            if piece_type != Piece.NONE:
                mg[piece_color] += self.mg_table[piece][square]
                eg[piece_color] += self.eg_table[piece][square]
                game_phase += game_phase_inc[piece_type]

        # tapered eval
        mg_eval = mg[Color.WHITE] - mg[Color.BLACK]
        eg_eval = eg[Color.WHITE] - eg[Color.BLACK]
        mg_phase = game_phase
        mg_phase = 24 if mg_phase > 24 else 24  # in case of early promotion
        eg_phase = 24 - mg_phase

        pieces_eval = (mg_eval * mg_phase + eg_eval * eg_phase) / 24

        evaluation = pieces_eval + mop_up_eval
        evaluation = evaluation if self.board.game_state.white_to_move else -evaluation

        return evaluation

    def count_material(self, color):
        material = 0
        piece_types = [Piece.PAWN, Piece.KNIGHT, Piece.BISHOP, Piece.ROOK, Piece.QUEEN]
        for piece_type in piece_types:
            material += Piece.get_piece_value(piece_type) * self.board.piece_count[color | piece_type]

        return material

    def mop_up_eval(self, color, friendly_material, enemy_material):
        queen_endgame_weight = 45
        rook_endgame_weight = 20
        bishop_endgame_weight = 10
        knight_endgame_weight = 10

        enemy_color = Color.WHITE if color == Color.BLACK else Color.BLACK

        # calculate if we have more pieces and calculate how far we are into the endgame
        endgame_start_weight = queen_endgame_weight \
                               + 2 * rook_endgame_weight \
                               + 2 * bishop_endgame_weight \
                               + 2 * knight_endgame_weight
        endgame_weight_sum = self.board.piece_count[enemy_color | Piece.QUEEN] * queen_endgame_weight \
                             + self.board.piece_count[enemy_color | Piece.ROOK] * rook_endgame_weight \
                             + self.board.piece_count[enemy_color | Piece.BISHOP] * bishop_endgame_weight \
                             + self.board.piece_count[enemy_color | Piece.KNIGHT] * knight_endgame_weight
        endgame_transition = 1 - min(1, endgame_weight_sum / endgame_start_weight)

        if friendly_material > enemy_material + Piece.PAWN_VALUE * 2 and endgame_transition > 0:
            score = 0
            friendly_king_square = self.board.game_state.king_square[color]
            enemy_king_square = self.board.game_state.king_square[enemy_color]

            # encourage pushing enemy king to edge
            enemy_king_rank = BoardHelper.get_rank(enemy_king_square)
            enemy_king_file = BoardHelper.get_file(enemy_king_square)

            enemy_king_rank_dst_from_center = max(3 - enemy_king_rank, enemy_king_rank - 4)
            enemy_king_file_dst_from_center = max(3 - enemy_king_file, enemy_king_file - 4)
            enemy_king_dst_from_center = enemy_king_rank_dst_from_center + enemy_king_file_dst_from_center
            score += enemy_king_dst_from_center * 2

            # encourage moving king closer to enemy king
            friendly_king_rank = BoardHelper.get_rank(friendly_king_square)
            friendly_king_file = BoardHelper.get_file(friendly_king_square)

            rank_dst_between_kings = abs(friendly_king_rank - enemy_king_rank)
            file_dst_between_kings = abs(friendly_king_file - enemy_king_file)
            manhattan_dst_between_kings = rank_dst_between_kings + file_dst_between_kings
            score += (14 - manhattan_dst_between_kings) * 2

            # # discourage putting king on edge
            # score -= 10 if friendly_king_rank == 0 or friendly_king_rank == 7 else 0
            # score -= 10 if friendly_king_file == 0 or friendly_king_file == 7 else 0

            return score * 10 * endgame_transition

        return 0


if __name__ == "__main__":
    board = Board("3r4/8/3k4/8/8/3K4/8/8 w - - 0 1")
    evaluation = Evaluation(board)
    print(board)
    print(evaluation.mop_up_eval(Color.BLACK, 500, 0))

    board = Board("8/3r4/8/2k5/8/2K5/8/8 w - - 0 1")
    evaluation = Evaluation(board)
    print(board)
    print(evaluation.mop_up_eval(Color.BLACK, 500, 0))

    board = Board("8/3r4/8/2k5/8/1K6/8/8 w - - 0 1")
    evaluation = Evaluation(board)
    print(board)
    print(evaluation.mop_up_eval(Color.BLACK, 500, 0))

    board = Board("8/8/8/8/8/1k1r4/8/2K5 w - - 0 1")
    evaluation = Evaluation(board)
    print(board)
    print(evaluation.mop_up_eval(Color.BLACK, 500, 0))

