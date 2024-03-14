import time

from board import Board
from move_generator import MoveGenerator
from evaluation import Evaluation
from move import Move
from transposition_table import TableEntry, TranspositionTable
from constants import *


class Search:
    NEGATIVE_INFINITY = float('-inf')
    POSITIVE_INFINITY = float('inf')

    def __init__(self, board):
        self.board = board

        self.evaluation = Evaluation(board)
        self.move_generator = MoveGenerator(board)
        self.transposition_table = TranspositionTable()
        self.repetition_table = set()

        self.best_move = None
        self.best_eval = Search.NEGATIVE_INFINITY

        # for debugging/testing purposes
        self.positions_evaluated = 0

    def start_search(self, depth=3):
        self.best_move = None
        self.best_eval = Search.NEGATIVE_INFINITY

        self.positions_evaluated = 0

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

    def iterative_deepening_search(self, max_depth, max_time=2):
        for depth in range(1, max_depth + 1):
            start_time = time.time()
            self.start_search(depth)

            if self.best_eval == Search.POSITIVE_INFINITY:
                return self.best_move

            elapsed_time = time.time() - start_time
            if elapsed_time >= max_time:
                break

        if self.best_move is None:
            self.best_move = self.move_generator.generate_moves()[0]

        return self.best_move

    def search(self, depth, alpha, beta):
        zobrist_key = self.board.zobrist_key
        tt_entry = self.transposition_table.lookup(zobrist_key)

        # TODO: add repetition table to avoid repeated moves
        if zobrist_key in self.repetition_table:
            return 0

        alpha_orig = alpha
        if tt_entry and tt_entry.depth >= depth:
            # print(tt_entry)
            if tt_entry.flag == TableEntry.EXACT:
                return tt_entry.value
            elif tt_entry.flag == TableEntry.LOWER_BOUND:
                alpha = max(alpha, tt_entry.value)
            elif tt_entry.flag == TableEntry.UPPER_BOUND:
                beta = min(beta, tt_entry.value)

            if alpha >= beta:
                return tt_entry.value

        if depth == 0:
            return self.quiescence_search(alpha, beta)

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
                self.transposition_table.store(zobrist_key, depth, beta, TableEntry.LOWER_BOUND)
                return beta
            alpha = max(alpha, evaluation)

        self.transposition_table.store(zobrist_key, depth, alpha, TableEntry.EXACT)
        return alpha

    # TODO: add checks to quiescence search
    def quiescence_search(self, alpha, beta):
        """Keep searching if there are captures. The purpose is to only evaluate 'quiet' positions where
        there are no captures possible."""
        evaluation = self.evaluation.evaluate()

        if evaluation >= beta:
            return beta
        alpha = max(alpha, evaluation)

        valid_moves = self.move_generator.generate_moves(captures_only=True)
        self.order_moves(valid_moves)

        for move in valid_moves:
            self.board.make_move(move)
            evaluation = -1 * self.quiescence_search(-beta, -alpha)
            self.board.unmake_move(move)

            if evaluation >= beta:
                return beta
            alpha = max(alpha, evaluation)

        return alpha

    def order_moves(self, moves):
        # order moves from high move score to low
        moves.sort(key=self.get_move_score, reverse=True)

    def get_move_score(self, move):
        move_score = 0
        move_piece = self.board.board[move.start_square]
        capture_piece = self.board.board[move.target_square]
        capture_piece_type = Piece.get_piece_type(capture_piece)

        # likely to be a good move if we are capturing a high value piece with a low value piece
        if capture_piece_type != Piece.NONE:
            move_score = 10 * Piece.get_piece_value(capture_piece) - Piece.get_piece_value(move_piece)

        # likely to be a good move if we are promoting/close to promoting
        if move.flag == Move.PROMOTE_TO_QUEEN_FLAG:
            move_score += Piece.QUEEN_VALUE
        elif move.flag == Move.PROMOTE_TO_ROOK_FLAG:
            move_score += Piece.ROOK_VALUE
        elif move.flag == Move.PROMOTE_TO_BISHOP_FLAG:
            move_score += Piece.BISHOP_VALUE
        elif move.flag == Move.PROMOTE_TO_KNIGHT_FLAG:
            move_score += Piece.KNIGHT_VALUE

        # TODO: checks are likely to be good moves sometimes
        # if move.flag ==

        # king moves are less likely to be good
        if Piece.get_piece_type(move_piece) == Piece.KING:
            move_score -= 50

        # probably not a good move if we are moving our piece into a square that our opponent's pawn can capture
        if move.target_square in self.move_generator.opponent_pawn_attack_squares:
            move_score -= Piece.get_piece_value(move_piece)

        return move_score

    def is_checkmate(self, moves):
        if len(moves) == 0 and self.board.in_check:
            return True
        return False

    def is_stalemate(self, moves):
        if len(moves) == 0 and not self.board.in_check:
            return True
        return False
