from constants import *
from move import Move
from bitboard import BitBoard
from gamestate import GameState
from zobrist import Zobrist


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
        self.en_passant_file = -1
        self.num_pieces = 0
        self.piece_count = {
            Color.WHITE | Piece.PAWN: 0,
            Color.WHITE | Piece.ROOK: 0,
            Color.WHITE | Piece.BISHOP: 0,
            Color.WHITE | Piece.KNIGHT: 0,
            Color.WHITE | Piece.QUEEN: 0,
            Color.WHITE | Piece.KING: 0,
            Color.BLACK | Piece.PAWN: 0,
            Color.BLACK | Piece.ROOK: 0,
            Color.BLACK | Piece.BISHOP: 0,
            Color.BLACK | Piece.KNIGHT: 0,
            Color.BLACK | Piece.QUEEN: 0,
            Color.BLACK | Piece.KING: 0
        }

        self.zobrist = Zobrist()
        self.zobrist_key = 0

        # TODO: add 50 move draw rule
        self.num_half_moves = 0
        self.num_full_moves = 0

        # TODO: add 3 fold repetition

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
        prev_castling_state = self.get_castling_state()

        moved_piece = self.board[start_square]
        moved_piece_type = Piece.get_piece_type(moved_piece)
        captured_piece = Piece.PAWN | self.opponent_color if is_en_passant else self.board[target_square]
        captured_piece_type = Piece.get_piece_type(captured_piece)

        # move piece
        self.board[target_square] = moved_piece
        self.board[start_square] = Piece.NONE

        self.zobrist_key ^= self.zobrist.get_zobrist_num(moved_piece, start_square)
        self.zobrist_key ^= self.zobrist.get_zobrist_num(moved_piece, target_square)

        # reset en passant files and checks
        self.zobrist_key ^= self.zobrist.get_zobrist_en_passant(self.en_passant_file)

        self.prev_captured_piece = captured_piece
        self.en_passant_file = -1
        self.in_check = False
        self.in_double_check = False

        # handle captures
        if captured_piece_type != Piece.NONE:
            captured_square = target_square
            if is_en_passant:
                captured_square = target_square + (-8 if self.white_to_move else 8)
                self.board[captured_square] = Piece.NONE

            self.piece_count[self.opponent_color | captured_piece_type] -= 1
            self.num_pieces -= 1

            self.zobrist_key ^= self.zobrist.get_zobrist_num(captured_piece, captured_square)

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

                self.zobrist_key ^= self.zobrist.get_zobrist_num(rook_piece, rook_start_square)
                self.zobrist_key ^= self.zobrist.get_zobrist_num(rook_piece, rook_target_square)

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

            promotion_piece = move_color | promotion_piece
            self.board[target_square] = promotion_piece
            self.piece_count[promotion_piece] += 1
            self.piece_count[move_color | Piece.PAWN] -= 1

            self.zobrist_key ^= self.zobrist.get_zobrist_num(moved_piece, target_square)
            self.zobrist_key ^= self.zobrist.get_zobrist_num(promotion_piece, target_square)

        # pawn has moved two forwards, mark file with en passant
        if move_flag == Move.PAWN_TWO_UP_FLAG:
            self.en_passant_file = BoardHelper.get_file(target_square)

            self.zobrist_key ^= self.zobrist.get_zobrist_en_passant(self.en_passant_file)

        # update castling rights
        if start_square == BoardHelper.A1 or target_square == BoardHelper.A1:
            self.can_white_queen_side_castle = False
        elif start_square == BoardHelper.H1 or target_square == BoardHelper.H1:
            self.can_white_king_side_castle = False
        elif start_square == BoardHelper.A8 or target_square == BoardHelper.A8:
            self.can_black_queen_side_castle = False
        elif start_square == BoardHelper.H8 or target_square == BoardHelper.H8:
            self.can_black_king_side_castle = False

        new_castling_state = self.get_castling_state()
        if prev_castling_state != new_castling_state:
            self.zobrist_key ^= self.zobrist.get_zobrist_castling_rights(prev_castling_state)
            self.zobrist_key ^= self.zobrist.get_zobrist_castling_rights(new_castling_state)

        # change side to move
        self.white_to_move = not self.white_to_move
        self.friendly_color, self.opponent_color = self.opponent_color, self.friendly_color

        self.zobrist_key ^= self.zobrist.get_zobrist_side_to_move(Color.BLACK)

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
            self.piece_count[self.board[moved_to]] -= 1
            self.piece_count[move_color | Piece.PAWN] += 1

            self.board[moved_to] = move_color | Piece.PAWN

        # move piece
        self.board[moved_to] = Piece.NONE
        self.board[moved_from] = moved_piece

        if undoing_capture:
            capture_square = moved_to
            if undoing_en_passant:
                capture_square += -8 if self.white_to_move else 8

            self.board[capture_square] = self.prev_captured_piece
            self.piece_count[self.prev_captured_piece] += 1

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

    def get_castling_state(self):
        """Calculates a 4-bit number representing the current castling state."""
        castling_state = 0b0000
        castling_state |= 0b0001 if self.can_white_queen_side_castle else 0b0000
        castling_state |= 0b0010 if self.can_white_king_side_castle else 0b0000
        castling_state |= 0b0100 if self.can_black_queen_side_castle else 0b0000
        castling_state |= 0b1000 if self.can_black_king_side_castle else 0b0000

        return castling_state

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
        game_state.num_pieces = self.num_pieces
        game_state.num_half_moves = self.num_half_moves
        game_state.num_full_moves = self.num_full_moves
        game_state.zobrist_key = self.zobrist_key

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
        self.num_pieces = game_state.num_pieces
        self.num_half_moves = game_state.num_half_moves
        self.num_full_moves = game_state.num_full_moves
        self.zobrist_key = game_state.zobrist_key

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
                    self.piece_count[piece_color | piece_type] += 1
                    self.num_pieces += 1
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

        # set castling rights
        if len(fen_info) > 2:
            fen_castling_str = fen_info[2]

            self.can_white_queen_side_castle = True if 'Q' in fen_castling_str else False
            self.can_white_king_side_castle = True if 'K' in fen_castling_str else False
            self.can_black_queen_side_castle = True if 'q' in fen_castling_str else False
            self.can_black_king_side_castle = True if 'k' in fen_castling_str else False

        # set en passant file
        if len(fen_info) > 3 and fen_info[3] != '-':
            fen_en_passant_str = fen_info[3]
            rank_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
            self.en_passant_file = rank_to_index[fen_en_passant_str[0]]

        # set halfmove clock
        if len(fen_info) > 4:
            self.num_half_moves = int(fen_info[4])

        # set fullmove clock
        if len(fen_info) > 5:
            self.num_full_moves = int(fen_info[5])

        # set up initial zobrist key
        for square_index in range(len(self.board)):
            piece = self.board[square_index]
            self.zobrist_key ^= self.zobrist.get_zobrist_num(piece, square_index)

        side_to_move = Color.WHITE if self.white_to_move else Color.BLACK

        self.zobrist_key ^= self.zobrist.get_zobrist_en_passant(self.en_passant_file)
        self.zobrist_key ^= self.zobrist.get_zobrist_side_to_move(side_to_move)
        self.zobrist_key ^= self.zobrist.get_zobrist_castling_rights(self.get_castling_state())

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
    print(board.zobrist_key)
