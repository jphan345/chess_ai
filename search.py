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

        # for move ordering
        self.move_scores = {}
        self.ordered_moves = []

        self.best_move = None
        self.best_eval = Search.NEGATIVE_INFINITY
        self.best_move_this_iteration = None
        self.best_eval_this_iteration = Search.NEGATIVE_INFINITY

        # for debugging/testing purposes
        self.positions_evaluated = 0

    def get_search_result(self):
        return self.best_move, self.best_eval

    def iterative_deepening_search(self, max_depth, max_time=2):
        self.ordered_moves = []
        self.move_scores = {}

        start_time = time.time()
        moves = self.move_generator.generate_moves()
        for depth in range(1, max_depth + 1):
            self.best_move = None
            self.best_eval = Search.NEGATIVE_INFINITY

            if DEBUG:
                print(f"\ndepth: {depth}")

            self.order_moves(moves, iterative=True)

            for move in moves:
                self.board.make_move(move)
                evaluation = -self.negamax_search(depth, Search.NEGATIVE_INFINITY, Search.POSITIVE_INFINITY)
                self.board.unmake_move(move)

                if DEBUG:
                    print(move, evaluation)

                self.move_scores[move] = evaluation

                if evaluation > self.best_eval_this_iteration:
                    self.best_eval_this_iteration = evaluation
                    self.best_move_this_iteration = move

            self.best_move = self.best_move_this_iteration
            self.best_eval = self.best_eval_this_iteration

            if self.best_eval == Search.POSITIVE_INFINITY:
                return self.best_move

            self.best_move_this_iteration = None
            self.best_eval_this_iteration = Search.NEGATIVE_INFINITY

            time_passed = time.time() - start_time
            if time_passed > max_time:
                break

        if self.best_move is None:
            if self.best_move_this_iteration is None:
                self.best_move = self.move_generator.generate_moves()[0]
            else:
                self.best_move = self.best_move_this_iteration

        return self.best_move

    def old_search(self, depth, alpha, beta):
        zobrist_key = self.board.zobrist_key
        tt_entry = self.transposition_table.lookup(zobrist_key)

        # TODO: add repetition table to avoid repeated moves
        if zobrist_key in self.repetition_table:
            return 0

        alpha_orig = alpha
        if tt_entry and tt_entry.depth >= depth:
            if tt_entry.flag == TableEntry.EXACT:
                return tt_entry.value
            elif tt_entry.flag == TableEntry.UPPER_BOUND:
                alpha = max(alpha, tt_entry.value)
            elif tt_entry.flag == TableEntry.LOWER_BOUND:
                beta = min(beta, tt_entry.value)

        valid_moves = self.move_generator.generate_moves()

        if self.is_checkmate(valid_moves):
            return Search.NEGATIVE_INFINITY
        if self.is_stalemate(valid_moves):
            return 0

        if depth == 0:
            return self.quiescence_search(alpha, beta)

        self.order_moves(valid_moves)

        for move in valid_moves:
            self.board.make_move(move)
            evaluation = -1 * self.old_search(depth - 1, -beta, -alpha)
            self.board.unmake_move(move)

            if evaluation >= beta:
                # if move is too good, opponent won't play the move so disregard it
                self.transposition_table.store(zobrist_key, depth, beta, TableEntry.LOWER_BOUND)
                return beta

            alpha = max(alpha, evaluation)

        self.transposition_table.store(zobrist_key, depth, alpha, TableEntry.EXACT)
        return alpha

    def negamax_search(self, depth, alpha, beta):
        alpha_orig = alpha

        # TODO: add repetition table to avoid repeated moves
        if self.board.zobrist_key in self.repetition_table:
            return 0

        # transposition table lookup
        tt_entry = self.transposition_table.lookup(self.board.zobrist_key)
        if tt_entry and tt_entry.depth >= depth:
            if tt_entry.flag == TableEntry.EXACT:
                return tt_entry.value
            elif tt_entry.flag == TableEntry.LOWER_BOUND:
                alpha = max(alpha, tt_entry.value)
            elif tt_entry.flag == TableEntry.UPPER_BOUND:
                beta = min(beta, tt_entry.value)

            if alpha >= beta:
                return tt_entry.value

        moves = self.move_generator.generate_moves()

        if self.is_checkmate(moves):
            return Search.NEGATIVE_INFINITY
        if self.is_stalemate(moves):
            return 0

        if depth == 0:
            return self.quiescence_search(alpha, beta)

        self.order_moves(moves)
        evaluation = Search.NEGATIVE_INFINITY
        for move in moves:
            self.board.make_move(move)
            evaluation = -self.negamax_search(depth - 1, -beta, -alpha)
            self.board.unmake_move(move)

            alpha = max(alpha, evaluation)
            if alpha >= beta:
                break

        # transposition table store
        if evaluation <= alpha_orig:
            self.transposition_table.store(self.board.zobrist_key, depth, evaluation, TableEntry.UPPER_BOUND)
        elif evaluation >= beta:
            self.transposition_table.store(self.board.zobrist_key, depth, evaluation, TableEntry.LOWER_BOUND)
        else:
            self.transposition_table.store(self.board.zobrist_key, depth, evaluation, TableEntry.EXACT)

        return evaluation

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

    def order_moves(self, moves, iterative=False):
        # order moves from high move score to low
        if not iterative or len(self.move_scores) == 0:
            moves.sort(key=self.get_move_score, reverse=True)
        else:
            moves.sort(key=lambda x: (self.move_scores[x], -self.ordered_moves.index(x)), reverse=True)

        if iterative:
            self.ordered_moves = moves[:]

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
