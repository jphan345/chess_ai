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
    print(f"board.can_white_queen_side_castle: {board.can_white_queen_side_castle}")
    print(f"board.can_white_king_side_castle: {board.can_white_king_side_castle}")
    print(f"board.can_black_queen_side_castle: {board.can_black_queen_side_castle}")
    print(f"board.can_black_king_side_castle: {board.can_black_king_side_castle}")
    print(f"board.in_check: {board.in_check}")
    print(f"board.in_double_check: {board.in_double_check}")
    print(f"board.white_to_move: {board.white_to_move}")
    print(f"board.friendly_color: {board.friendly_color}")
    print(f"board.opponent_color: {board.opponent_color}")
    print(f"board.king_square: {board.king_square}")
    print(f"board.en_passant_file: {board.en_passant_file}")
    print(f"board.prev_captured_piece: {board.prev_captured_piece}")
    print(f"board.num_half_moves: {board.num_half_moves}")
    print(f"board.num_full_moves: {board.num_full_moves}")

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
    print(f"board.num_pieces: {board.num_pieces}")
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
    if board.in_check and len(moves) == 0:
        return True
    return False


def is_stalemate(board, moves):
    if not board.in_check and len(moves) == 0:
        return True
    return False


if __name__ == "__main__":
    # board = Board()
    board = Board("3r4/8/3k4/8/8/3K4/8/8 w - - 0 1")
    # board = Board("7K/4rk2/8/8/8/8/8/8 w - - 2 2")
    # board = Board("8/8/3KP3/8/8/8/6k1/7q w - - 0 1")

    # board = Board("7k/8/8/2p1p2p/2P1p2P/4P3/8/7K w - - 0 1")
    # board = Board("8/8/8/2p1p2p/2P1p2k/4P3/6K1/8 w - - 0 9")

    mg = MoveGenerator(board)
    eval = Evaluation(board)
    search = Search(board)
    move_stack = []

    while True:

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
            move_str = input("Make your move: ")

            if move_str == "STATUS" or move_str == "status":
                print_status(board, mg)
                continue

            if move_str == "EVAL" or move_str == "eval":
                print_eval(eval)
                continue

            if move_str == "PIECES" or move_str == "pieces":
                print_pieces(board)
                continue

            if move_str == "ZOBRIST" or move_str == "zobrist":
                print(f"{board.zobrist_key:b}")
                print(f"{board.zobrist_key}")
                continue

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
            flag = Move.NO_FLAG if len(s) == 2 else flags[s[2]]

            move = Move(start_square, target_square, flag=flag)
            if move in valid_moves:
                board.make_move(move)
                move_stack.append(move)
                break

        valid_moves = mg.generate_moves()
        search.order_moves(valid_moves)
        print("\nCOMPUTER VALID MOVES")
        print([str(move) for move in valid_moves])
        computer_move = get_computer_move(search)

        if is_stalemate(board, valid_moves):
            print("STALEMATE")
            break
        elif is_checkmate(board, valid_moves):
            print("CHECKMATE")
            break

        board.make_move(computer_move)
