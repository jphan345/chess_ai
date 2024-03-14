from constants import *
from board import Board
from move import Move


class Evaluation:
    def __init__(self, board):
        self.board = board

    def evaluate(self):
        white_material = self.count_material(Color.WHITE)
        black_material = self.count_material(Color.BLACK)

        white_mop_up = self.mop_up_eval(Color.WHITE, white_material, black_material)
        black_mop_up = self.mop_up_eval(Color.BLACK, black_material, white_material)

        white_eval = white_material + white_mop_up
        black_eval = black_material + black_mop_up
        evaluation = white_eval - black_eval

        return evaluation if self.board.white_to_move else -evaluation

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
            friendly_king_square = self.board.king_square[color]
            enemy_king_square = self.board.king_square[enemy_color]

            # encourage pushing enemy king to edge
            enemy_king_rank = BoardHelper.get_rank(enemy_king_square)
            enemy_king_file = BoardHelper.get_file(enemy_king_square)

            enemy_king_rank_dst_from_center = max(3 - enemy_king_rank, enemy_king_rank - 4)
            enemy_king_file_dst_from_center = max(3 - enemy_king_file, enemy_king_file - 4)
            enemy_king_dst_from_center = enemy_king_rank_dst_from_center + enemy_king_file_dst_from_center
            score += enemy_king_dst_from_center * 4

            # encourage moving king closer to enemy king
            friendly_king_rank = BoardHelper.get_rank(friendly_king_square)
            friendly_king_file = BoardHelper.get_file(friendly_king_square)

            rank_dst_between_kings = abs(friendly_king_rank - enemy_king_rank)
            file_dst_between_kings = abs(friendly_king_file - enemy_king_file)
            manhattan_dst_between_kings = rank_dst_between_kings + file_dst_between_kings
            score += (14 - manhattan_dst_between_kings) * 2

            # discourage putting king on edge
            score -= 10 if friendly_king_rank == 0 or friendly_king_rank == 7 else 0
            score -= 10 if friendly_king_file == 0 or friendly_king_file == 7 else 0

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


