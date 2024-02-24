from constants import *
from board import Board


class Evaluation:
    def __init__(self, board):
        self.board = board

    def evaluate(self):
        white_evaluation = self.count_pieces(Color.WHITE)
        black_evaluation = self.count_pieces(Color.BLACK)

        evaluation = white_evaluation - black_evaluation

        return evaluation if self.board.white_to_move else -evaluation

    def count_pieces(self, color):
        material = 0
        for square in range(64):
            piece = self.board.board[square]
            piece_type = Piece.get_piece_type(piece)
            piece_color = Color.get_piece_color(piece)

            if piece_type != Piece.NONE and piece_color == color:
                material += Piece.get_piece_value(piece)

        return material
