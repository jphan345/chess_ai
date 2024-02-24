from constants import *
from move import Move
from bitboard import BitBoard
from gamestate import GameState


class Board:
    START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    def __init__(self, fen=START_FEN):
        self.can_white_queen_side_castle = True
        self.can_white_king_side_castle = True
        self.can_black_queen_side_castle = True
        self.can_black_king_side_castle = True
        self.in_check = False
        self.in_double_check = False
        self.white_to_move = True
        self.friendly_color = Color.WHITE
        self.opponent_color = Color.BLACK
        self.king_square = {Color.WHITE: 0, Color.BLACK: 0}
        self.en_passant_file = [False for _ in range(8)]

        # used for recording the game state
        self.prev_captured_piece = Piece.NONE

        self.board = []
        self.game_state_history = []
        self.bitboard = BitBoard()

        self.create_board(fen)

    def make_move(self, move):
        # add the previous state to the game history for undos
        self.game_state_history.append(self.create_game_state())

        move_color = Color.WHITE if self.white_to_move else Color.BLACK
        start_square = move.start_square
        target_square = move.target_square
        move_flag = move.flag
        is_promotion = move.is_promotion
        is_en_passant = move_flag == Move.EN_PASSANT_CAPTURE_FLAG

        moved_piece = self.board[start_square]
        moved_piece_type = Piece.get_piece_type(moved_piece)
        captured_piece = Piece.PAWN | self.opponent_color if is_en_passant else self.board[target_square]
        captured_piece_type = Piece.get_piece_type(captured_piece)

        # move piece
        self.board[target_square] = moved_piece
        self.board[start_square] = Piece.NONE

        # reset en passant files and checks
        self.prev_captured_piece = captured_piece
        self.en_passant_file = [False for _ in range(8)]
        self.in_check = False
        self.in_double_check = False

        # handle captures
        if captured_piece_type != Piece.NONE:
            if is_en_passant:
                captured_square = target_square + (-8 if self.white_to_move else 8)
                self.board[captured_square] = Piece.NONE

        # handle king
        if moved_piece_type == Piece.KING:
            self.king_square[move_color] = target_square

            if move_color == Color.WHITE:
                self.can_white_queen_side_castle = False
                self.can_white_king_side_castle = False
            else:
                self.can_black_queen_side_castle = False
                self.can_black_king_side_castle = False

            # the king can castle as a move
            if move_flag == Move.CASTLE_FLAG:
                rook_piece = move_color | Piece.ROOK
                is_kingside = True if target_square == BoardHelper.G1 or target_square == BoardHelper.G8 else False
                rook_start_square = target_square + 1 if is_kingside else target_square - 2
                rook_target_square = target_square - 1 if is_kingside else target_square + 1

                self.board[rook_target_square] = rook_piece
                self.board[rook_start_square] = Piece.NONE

        # handle promotion
        if is_promotion:
            promotion_piece = Piece.NONE
            if move_flag == Move.PROMOTE_TO_QUEEN_FLAG:
                promotion_piece = Piece.QUEEN
            elif move_flag == Move.PROMOTE_TO_ROOK_FLAG:
                promotion_piece = Piece.ROOK
            elif move_flag == Move.PROMOTE_TO_BISHOP_FLAG:
                promotion_piece = Piece.BISHOP
            elif move_flag == Move.PROMOTE_TO_KNIGHT_FLAG:
                promotion_piece = Piece.KNIGHT

            self.board[target_square] = move_color | promotion_piece

        # pawn has moved two forwards, mark file with en passant
        if move_flag == Move.PAWN_TWO_UP_FLAG:
            self.en_passant_file[BoardHelper.get_file(target_square)] = True

        # update castling rights
        if start_square == BoardHelper.A1 or target_square == BoardHelper.A1:
            self.can_white_queen_side_castle = False
        elif start_square == BoardHelper.H1 or target_square == BoardHelper.H1:
            self.can_white_king_side_castle = False
        elif start_square == BoardHelper.A8 or target_square == BoardHelper.A8:
            self.can_black_queen_side_castle = False
        elif start_square == BoardHelper.H8 or target_square == BoardHelper.H8:
            self.can_black_king_side_castle = False

        # change side to move
        self.white_to_move = not self.white_to_move
        self.friendly_color, self.opponent_color = self.opponent_color, self.friendly_color

    def unmake_move(self, move):
        # change side to move
        self.white_to_move = not self.white_to_move
        self.friendly_color, self.opponent_color = self.opponent_color, self.friendly_color

        move_color = Color.WHITE if self.white_to_move else Color.BLACK
        moved_from = move.start_square
        moved_to = move.target_square
        move_flag = move.flag

        undoing_promotion = move.is_promotion
        undoing_en_passant = move_flag == Move.EN_PASSANT_CAPTURE_FLAG
        undoing_castling = move_flag == Move.CASTLE_FLAG
        undoing_capture = Piece.get_piece_type(self.prev_captured_piece) != Piece.NONE

        moved_piece = move_color | Piece.PAWN if undoing_promotion else self.board[moved_to]
        moved_piece_type = Piece.get_piece_type(moved_piece)

        # if undoing promotion, remove piece from promotion square and replace with pawn
        if undoing_promotion:
            self.board[moved_to] = move_color | Piece.PAWN

        # move piece
        self.board[moved_to] = Piece.NONE
        self.board[moved_from] = moved_piece

        if undoing_capture:
            capture_square = moved_to
            if undoing_en_passant:
                capture_square += -8 if self.white_to_move else 8

            self.board[capture_square] = self.prev_captured_piece

        if moved_piece_type == Piece.KING:
            self.king_square[move_color] = moved_from

            if undoing_castling:
                rook_piece = move_color | Piece.ROOK
                is_kingside = moved_to == BoardHelper.G1 or moved_to == BoardHelper.G8
                rook_square_before = moved_to + 1 if is_kingside else moved_to - 2
                rook_square_after = moved_to - 1 if is_kingside else moved_to + 1

                self.board[rook_square_before] = rook_piece
                self.board[rook_square_after] = Piece.NONE

        game_state = self.game_state_history.pop()
        self.load_game_state(game_state)

    def create_game_state(self):
        game_state = GameState()

        game_state.can_white_queen_side_castle = self.can_white_queen_side_castle
        game_state.can_white_king_side_castle = self.can_white_king_side_castle
        game_state.can_black_queen_side_castle = self.can_black_queen_side_castle
        game_state.can_black_king_side_castle = self.can_black_king_side_castle
        game_state.in_check = self.in_check
        game_state.in_double_check = self.in_double_check
        game_state.white_to_move = self.white_to_move
        game_state.friendly_color = self.friendly_color
        game_state.opponent_color = self.opponent_color
        game_state.prev_captured_piece = self.prev_captured_piece
        game_state.king_square = self.king_square
        game_state.en_passant_file = self.en_passant_file

        return game_state

    def load_game_state(self, game_state):
        self.can_white_queen_side_castle = game_state.can_white_queen_side_castle
        self.can_white_king_side_castle = game_state.can_white_king_side_castle
        self.can_black_queen_side_castle = game_state.can_black_queen_side_castle
        self.can_black_king_side_castle = game_state.can_black_king_side_castle
        self.in_check = game_state.in_check
        self.in_double_check = game_state.in_double_check
        self.white_to_move = game_state.white_to_move
        self.friendly_color = game_state.friendly_color
        self.opponent_color = game_state.opponent_color
        self.prev_captured_piece = game_state.prev_captured_piece
        self.king_square = game_state.king_square
        self.en_passant_file = game_state.en_passant_file

    def create_board(self, fen=START_FEN):
        self.board = [Piece.NONE for _ in range(64)]
        self.load_position_from_fen(fen)

    def load_position_from_fen(self, fen):
        piece_from_symbol = {
            "p": Piece.PAWN,
            "n": Piece.KNIGHT,
            "b": Piece.BISHOP,
            "r": Piece.ROOK,
            "q": Piece.QUEEN,
            "k": Piece.KING
        }

        # create board from fen
        fen_info = fen.split(' ')
        fen_board = fen_info[0]
        file = 0
        rank = 7
        for symbol in fen_board:
            if symbol == '/':
                file = 0
                rank -= 1
            else:
                if symbol.isdigit():
                    file += int(symbol)
                else:
                    piece_color = Color.WHITE if (symbol.isupper()) else Color.BLACK
                    piece_type = piece_from_symbol[symbol.lower()]
                    square_index = rank * 8 + file
                    self.board[square_index] = piece_color | piece_type
                    if piece_type == Piece.KING:
                        self.king_square[piece_color] = square_index
                    file += 1

        # set player turn
        if len(fen_info) > 1 and fen_info[1] == 'b':
            self.white_to_move = False
            self.friendly_color = Color.BLACK
            self.opponent_color = Color.WHITE
        else:
            self.white_to_move = True
            self.friendly_color = Color.WHITE
            self.opponent_color = Color.BLACK

    def __str__(self):
        pieces = {
            Piece.NONE: "•",
            Piece.PAWN: "p",
            Piece.KNIGHT: "n",
            Piece.BISHOP: "b",
            Piece.ROOK: "r",
            Piece.QUEEN: "q",
            Piece.KING: "k"
        }

        rank = 1
        s = ""
        row = ""
        for i in range(len(self.board)):
            piece = self.board[i]

            is_white = (piece >> 3) == 0
            piece = piece & 0b0111
            piece = pieces[piece].upper() if is_white else pieces[piece]
            row += piece + " "
            # row += str(i) + " "

            if (i + 1) % 8 == 0:
                s = f"{str(rank)}  {row} \n{s}"
                rank += 1
                row = ""
        s += "   a b c d e f g h"
        s += f"\n{'White' if (self.white_to_move is True) else 'Black'} to move."

        return s

    def print_indexes(self):
        pieces = {
            Piece.NONE: "•",
            Piece.PAWN: "p",
            Piece.KNIGHT: "n",
            Piece.BISHOP: "b",
            Piece.ROOK: "r",
            Piece.QUEEN: "q",
            Piece.KING: "k"
        }

        rank = 1
        s = ""
        row = ""
        for i in range(len(self.board)):
            piece = self.board[i]

            is_white = (piece >> 3) == 0
            piece = piece & 0b0111
            piece = pieces[piece].upper() if is_white else pieces[piece]
            row += str(i) + (" " if i >= 10 else "  ")

            if (i + 1) % 8 == 0:
                s = f"{str(rank)}  {row} \n{s}"
                rank += 1
                row = ""
        s += "   a  b  c  d  e  f  g  h"
        s += f"\n{'White' if (self.white_to_move is True) else 'Black'} to move."

        print(s)


if __name__ == "__main__":
    board = Board()
    print(board)
