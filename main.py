from board import Board
from move_generator import MoveGenerator
from move import Move
from evaluation import Evaluation
from search import Search
from constants import *
import random


def print_move(move):
    start_square = move.start_square
    target_square = move.target_square

    start_file = BoardHelper.get_file(start_square)
    start_rank = BoardHelper.get_rank(start_square)
    target_file = BoardHelper.get_file(target_square)
    target_rank = BoardHelper.get_rank(target_square)

    ranks = "abcdefgh"

    print(f"{ranks[start_rank]}{start_file} {ranks[target_rank]}{target_file}")


def print_status(board, mg):
    print(f"BOARD:")
    print(f"board.game_state.can_white_queen_side_castle: {board.game_state.can_white_queen_side_castle}")
    print(f"board.game_state.can_white_king_side_castle: {board.game_state.can_white_king_side_castle}")
    print(f"board.game_state.can_black_queen_side_castle: {board.game_state.can_black_queen_side_castle}")
    print(f"board.game_state.can_black_king_side_castle: {board.game_state.can_black_king_side_castle}")
    print(f"board.game_state.in_check: {board.game_state.in_check}")
    print(f"board.game_state.in_double_check: {board.game_state.in_double_check}")
    print(f"board.game_state.white_to_move: {board.game_state.white_to_move}")
    print(f"board.game_state.friendly_color: {board.game_state.friendly_color}")
    print(f"board.game_state.opponent_color: {board.game_state.opponent_color}")
    print(f"board.game_state.king_square: {board.game_state.king_square}")
    print(f"board.game_state.en_passant_file: {board.game_state.en_passant_file}")
    print(f"board.game_state.prev_captured_piece: {board.game_state.prev_captured_piece}")
    print(f"board.game_state.num_half_moves: {board.game_state.num_half_moves}")
    print(f"board.game_state.num_full_moves: {board.game_state.num_full_moves}")

    print()
    print(f"MOVE GENERATOR:")
    print(f"mg.white_to_move: {mg.white_to_move}")
    print(f"mg.friendly_color: {mg.friendly_color}")
    print(f"mg.opponent_color: {mg.opponent_color}")
    print(f"mg.in_check: {mg.in_check}")
    print(f"mg.in_double_check: {mg.in_double_check}")
    print(f"mg.pin_rays: {mg.pin_rays}")
    print(f"mg.check_squares: {mg.check_squares}")
    print(f"mg.opponent_attack_squares: {mg.opponent_attack_squares}")


def print_pieces(board):
    print(f"board.game_state.num_pieces: {board.game_state.num_pieces}")
    print("board.piece_count: {")
    for piece in board.piece_count:
        print(f"\t{Piece.piece_str(piece)}: {board.piece_count[piece]}")
    print("}")


def print_eval(eval):
    total = eval.evaluate()
    white_material = eval.count_material(Color.WHITE)
    black_material = eval.count_material(Color.BLACK)
    white_mop_up = eval.mop_up_eval(Color.WHITE, white_material, black_material)
    black_mop_up = eval.mop_up_eval(Color.BLACK, black_material, white_material)
    print(f"white_material: {white_material}, white_mop_up: {white_mop_up}")
    print(f"black_material: {black_material}, black_mop_up: {black_mop_up}")
    print(f"total: {eval.evaluate()}")


def get_computer_move(search):
    search.iterative_deepening_search(6)

    return search.get_search_result()[0]


def is_checkmate(board, moves):
    if board.game_state.in_check and len(moves) == 0:
        return True
    return False


def is_stalemate(board, moves):
    if not board.game_state.in_check and len(moves) == 0:
        return True
    return False

def instructions():
    print("Type: start_square target_square flag")
    print("flags: EN_PASSANT, CASTLE, PAWN_TWO_UP, QUEEN, KNIGHT, ROOK, BISHOP (put in no flag if just a normal move)")

    print("Example moves:")
    print("Normal move: e2 e4")
    print("Initial pawn move: d2 d4 PAWN_TWO_UP")
    print("Promotion move: a7 a8 QUEEN")
    print("\nType 'undo' to undo a move")

if __name__ == "__main__":
    board = Board()
    # board = Board("3r4/8/3k4/8/8/3K4/8/8 w - - 0 1")
    # board = Board("7K/4rk2/8/8/8/8/8/8 w - - 2 2")
    # board = Board("8/8/3KP3/8/8/8/6k1/7q w - - 0 1")

    # board = Board("7k/8/8/2p1p2p/2P1p2P/4P3/8/7K w - - 0 1")
    # board = Board("8/8/8/2p1p2p/2P1p2k/4P3/6K1/8 w - - 0 9")
    # board = Board("r2qkb1r/ppp1pppp/2np1n2/8/3PP1b1/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 0 1")

    mg = MoveGenerator(board)
    eval = Evaluation(board)
    search = Search(board)
    move_stack = []

    BOT = True
    while True:
        instructions()
        print(board)
        valid_moves = mg.generate_moves()
        print(f"moves: {[str(m) for m in valid_moves]}")
        capture_moves = mg.generate_moves(captures_only=True)
        print(f"capture moves: {[str(m) for m in capture_moves]}")

        if is_stalemate(board, valid_moves):
            print("STALEMATE")
            break
        elif is_checkmate(board, valid_moves):
            print("CHECKMATE")
            break

        while True:
            move_str = input("Make your move: ").lower()

            if move_str == "status":
                print_status(board, mg)
                continue
            if move_str == "eval":
                print_eval(eval)
                continue
            if move_str == "pieces":
                print_pieces(board)
                continue
            if move_str == "zobrist":
                print(f"{board.game_state.zobrist_key:b}")
                print(f"{board.game_state.zobrist_key}")
                continue
            if move_str == "instructions":
                instructions()
                continue
            if move_str == "undo" or move_str == "unmake":
                if len(move_stack) != 0:
                    board.unmake_move(move_stack.pop())

            # parse move
            ranks = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
            flags = {
                "EN_PASSANT": Move.EN_PASSANT_CAPTURE_FLAG,
                "CASTLE": Move.CASTLE_FLAG,
                "PAWN_TWO_UP": Move.PAWN_TWO_UP_FLAG,
                "QUEEN": Move.PROMOTE_TO_QUEEN_FLAG,
                "KNIGHT": Move.PROMOTE_TO_KNIGHT_FLAG,
                "ROOK": Move.PROMOTE_TO_ROOK_FLAG,
                "BISHOP": Move.PROMOTE_TO_BISHOP_FLAG,
                "NONE": Move.NO_FLAG
            }

            s = move_str.split()
            start_str, target_str = s[0], s[1]
            start_square = ranks[start_str[0]] + ((int(start_str[1]) - 1) * 8)
            target_square = ranks[target_str[0]] + ((int(target_str[1]) - 1) * 8)
            flag = Move.NO_FLAG if len(s) == 2 else flags[s[2].upper()]

            move = Move(start_square, target_square, flag=flag)
            print(move.value)
            if move in valid_moves:
                board.make_move(move)
                move_stack.append(move)
                break

        print(board)

        if BOT:
            valid_moves = mg.generate_moves()
            search.order_moves(valid_moves)
            print("\nCOMPUTER VALID MOVES")
            print([repr(move) for move in valid_moves])
            print(sorted(str(move) for move in valid_moves))
            computer_move = get_computer_move(search)

            if is_stalemate(board, valid_moves):
                print("STALEMATE")
                break
            elif is_checkmate(board, valid_moves):
                print("CHECKMATE")
                break

            board.make_move(computer_move)
