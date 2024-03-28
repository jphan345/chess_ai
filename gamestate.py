from constants import *


class GameState:
    def __init__(self):
        self.can_white_queen_side_castle = True
        self.can_white_king_side_castle = True
        self.can_black_queen_side_castle = True
        self.can_black_king_side_castle = True
        self.in_check = False
        self.in_double_check = False
        self.white_to_move = True
        self.friendly_color = Color.WHITE
        self.opponent_color = Color.BLACK
        self.prev_captured_piece = Piece.NONE
        self.king_square = {Color.WHITE: 0, Color.BLACK: 0}
        self.en_passant_file = -1
        self.num_pieces = 32
        self.num_half_moves = 0
        self.num_full_moves = 0

        self.zobrist_key = 0

    def copy(self):
        new_game_state = GameState()

        new_game_state.can_white_queen_side_castle = self.can_white_queen_side_castle
        new_game_state.can_white_king_side_castle = self.can_white_king_side_castle
        new_game_state.can_black_queen_side_castle = self.can_black_queen_side_castle
        new_game_state.can_black_king_side_castle = self.can_black_king_side_castle
        new_game_state.in_check = self.in_check
        new_game_state.in_double_check = self.in_double_check
        new_game_state.white_to_move = self.white_to_move
        new_game_state.friendly_color = self.friendly_color
        new_game_state.opponent_color = self.opponent_color
        new_game_state.prev_captured_piece = self.prev_captured_piece
        new_game_state.king_square = {
            Color.WHITE: self.king_square[Color.WHITE],
            Color.BLACK: self.king_square[Color.BLACK]
        }
        new_game_state.en_passant_file = self.en_passant_file
        new_game_state.num_pieces = self.num_pieces
        new_game_state.num_half_moves = self.num_half_moves
        new_game_state.num_full_moves = self.num_full_moves
        new_game_state.zobrist_key = self.zobrist_key

        return new_game_state

