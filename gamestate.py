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
        self.en_passant_file = [False for _ in range(8)]
