from board import Board
from move_generator import MoveGenerator
from evaluation import Evaluation
from move import Move
from constants import *


class Search:
    NEGATIVE_INFINITY = float('-inf')
    POSITIVE_INFINITY = float('inf')

    def __init__(self, board):
        self.board = board

        self.evaluation = Evaluation(board)
        self.move_generator = MoveGenerator(board)

        self.best_move = None
        self.best_eval = Search.NEGATIVE_INFINITY

    def start_search(self):
        self.best_move = None
        self.best_eval = Search.NEGATIVE_INFINITY

        depth = 3
        moves = self.move_generator.generate_moves()
        self.order_moves(moves)

        for move in moves:
            self.board.make_move(move)
            evaluation = -1 * self.search(depth - 1, Search.NEGATIVE_INFINITY, Search.POSITIVE_INFINITY)
            self.board.unmake_move(move)

            if evaluation > self.best_eval:
                self.best_eval = evaluation
                self.best_move = move

        # if there is no best move found, pick any move
        if self.best_move is None:
            return moves[0]

        return self.best_move

    def get_search_result(self):
        return self.best_move, self.best_eval

    def search(self, depth, alpha, beta):
        if depth == 0:
            return self.evaluation.evaluate()

        valid_moves = self.move_generator.generate_moves()
        self.order_moves(valid_moves)

        if self.is_checkmate(valid_moves):
            return Search.NEGATIVE_INFINITY
        if self.is_stalemate(valid_moves):
            return 0

        for move in valid_moves:
            self.board.make_move(move)
            evaluation = -1 * self.search(depth - 1, -beta, -alpha)
            self.board.unmake_move(move)

            if evaluation >= beta:
                # if move is too good, opponent won't play the move so disregard it
                return beta
            if evaluation > alpha:
                alpha = evaluation

        return alpha

    def order_moves(self, moves):
        moves.sort(key=self.get_move_score)

    def get_move_score(self, move):
        move_score = 0
        move_piece = self.board.board[move.start_square]
        capture_piece = self.board.board[move.target_square]
        capture_piece_type = Piece.get_piece_type(capture_piece)

        if capture_piece_type != Piece.NONE:
            move_score = 10 * Piece.get_piece_value(capture_piece) - Piece.get_piece_value(move_piece)

        if move.flag == Move.PROMOTE_TO_QUEEN_FLAG:
            move_score += Piece.QUEEN_VALUE
        # elif move.flag == Move.PROMOTE_TO_ROOK_FLAG:
        #     move_score += Piece.ROOK_VALUE
        # elif move.flag == Move.PROMOTE_TO_BISHOP_FLAG:
        #     move_score += Piece.BISHOP_VALUE
        # elif move.flag == Move.PROMOTE_TO_KNIGHT_FLAG:
        #     move_score += Piece.KNIGHT_VALUE

        if move.target_square in self.move_generator.opponent_pawn_attack_squares:
            move_score -= Piece.get_piece_value(move_piece)

        return move_score
    def is_checkmate(self, moves):
        if self.board.in_check and len(moves) == 0:
            return True
        return False

    def is_stalemate(self, moves):
        if not self.board.in_check and len(moves) == 0:
            return True
        return False
