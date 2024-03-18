from constants import *
from board import Board
from move import Move


class MoveGenerator:
    ORTHOGONAL_DIRECTIONS = [Offset.LEFT, Offset.RIGHT, Offset.DOWN, Offset.UP]
    DIAGONAL_DIRECTIONS = [Offset.BOTTOM_RIGHT, Offset.TOP_LEFT, Offset.BOTTOM_LEFT, Offset.TOP_RIGHT]

    def __init__(self, board):
        self.board = board

        self.white_to_move = board.white_to_move
        self.friendly_color = board.friendly_color
        self.opponent_color = board.opponent_color

        self.in_check = self.board.in_check
        self.in_double_check = self.board.in_double_check

        self.pin_rays = []
        self.check_squares = set()
        self.opponent_attack_squares = set()
        self.opponent_pawn_attack_squares = set()

        self.calculate_attack_data()

    def generate_moves(self, captures_only=False):
        """Generates a list of legal moves in the current position.
        Non capture moves can be excluded for quiescence search."""
        self.white_to_move = self.board.white_to_move
        self.friendly_color = self.board.friendly_color
        self.opponent_color = self.board.opponent_color

        # set these values to false because self.calculate_attack_data calculates it
        self.in_check = False
        self.in_double_check = False

        self.pin_rays = []
        self.check_squares = set()
        self.opponent_attack_squares = set()

        self.calculate_attack_data()

        moves = []

        king_square = self.board.king_square[self.friendly_color]
        king_piece = self.board.board[king_square]
        moves += self.generate_king_moves(king_square, king_piece, captures_only=captures_only)

        # if there is a double check only the king can move
        if not self.in_double_check:
            for square in range(64):
                piece = self.board.board[square]
                piece_type = Piece.get_piece_type(piece)
                piece_color = Color.get_piece_color(piece)
                if piece_color == self.friendly_color:
                    if piece_type in [Piece.ROOK, Piece.BISHOP, Piece.QUEEN]:
                        moves += self.generate_sliding_moves(square, piece, captures_only=captures_only)
                    elif piece_type == Piece.PAWN:
                        moves += self.generate_pawn_moves(square, piece, captures_only=captures_only)
                    elif piece_type == Piece.KNIGHT:
                        moves += self.generate_knight_moves(square, piece, captures_only=captures_only)

        return moves

    def generate_king_moves(self, start_square, piece, captures_only=False):
        file = BoardHelper.get_file(start_square)
        king_offsets = [Offset.LEFT, Offset.TOP_LEFT, Offset.BOTTOM_LEFT, Offset.DOWN, Offset.UP, Offset.RIGHT,
                        Offset.BOTTOM_RIGHT, Offset.TOP_RIGHT]
        if file == 0:
            king_offsets = king_offsets[3:]
        elif file == 7:
            king_offsets = king_offsets[:-3]

        moves = []
        for offset in king_offsets:
            target_square = start_square + offset

            if 0 <= target_square <= 63:
                target_piece = self.board.board[target_square]
                target_piece_type = Piece.get_piece_type(target_piece)
                target_piece_color = Color.get_piece_color(target_piece)
                if target_piece_type == Piece.NONE and not captures_only:
                    # king cannot move into a square that would put it under attack
                    if target_square not in self.opponent_attack_squares:
                        moves.append(Move(start_square, target_square))
                elif target_piece_type != Piece.NONE and target_piece_color == self.opponent_color:
                    if target_square not in self.opponent_attack_squares:
                        moves.append(Move(start_square, target_square))

        # can't castle if you are in check or if we're generating captures only
        if self.in_check or captures_only:
            return moves

        if self.friendly_color == Color.WHITE:
            can_white_king_side_castle = self.board.can_white_king_side_castle
            can_white_queen_side_castle = self.board.can_white_queen_side_castle

            # king cannot castle if he has to cross through an attacked square
            for square in [BoardHelper.F1, BoardHelper.G1]:
                if square in self.opponent_attack_squares:
                    can_white_king_side_castle = False
                    break
            for square in [BoardHelper.B1, BoardHelper.C1, BoardHelper.D1]:
                if square in self.opponent_attack_squares:
                    can_white_queen_side_castle = False
                    break

            if can_white_king_side_castle:
                f1_piece = self.board.board[BoardHelper.F1]
                g1_piece = self.board.board[BoardHelper.G1]
                f1_piece_type = Piece.get_piece_type(f1_piece)
                g1_piece_type = Piece.get_piece_type(g1_piece)

                if f1_piece_type == g1_piece_type == Piece.NONE:
                    moves.append(Move(start_square, BoardHelper.G1, flag=Move.CASTLE_FLAG))

            if can_white_queen_side_castle:
                b1_piece = self.board.board[BoardHelper.B1]
                c1_piece = self.board.board[BoardHelper.C1]
                d1_piece = self.board.board[BoardHelper.D1]
                b1_piece_type = Piece.get_piece_type(b1_piece)
                c1_piece_type = Piece.get_piece_type(c1_piece)
                d1_piece_type = Piece.get_piece_type(d1_piece)

                if b1_piece_type == c1_piece_type == d1_piece_type == Piece.NONE:
                    moves.append(Move(start_square, BoardHelper.C1, flag=Move.CASTLE_FLAG))

        else:
            can_black_king_side_castle = self.board.can_black_king_side_castle
            can_black_queen_side_castle = self.board.can_black_queen_side_castle

            # king cannot castle if he has to cross through an attacked square
            for square in [BoardHelper.F8, BoardHelper.G8]:
                if square in self.opponent_attack_squares:
                    can_black_king_side_castle = False
                    break
            for square in [BoardHelper.B8, BoardHelper.C8, BoardHelper.D8]:
                if square in self.opponent_attack_squares:
                    can_black_queen_side_castle = False
                    break

            if can_black_king_side_castle:
                f8_piece = self.board.board[BoardHelper.F8]
                g8_piece = self.board.board[BoardHelper.G8]
                f8_piece_type = Piece.get_piece_type(f8_piece)
                g8_piece_type = Piece.get_piece_type(g8_piece)

                if f8_piece_type == g8_piece_type == Piece.NONE:
                    moves.append(Move(start_square, BoardHelper.G8, flag=Move.CASTLE_FLAG))

            if can_black_queen_side_castle:
                b8_piece = self.board.board[BoardHelper.B8]
                c8_piece = self.board.board[BoardHelper.C8]
                d8_piece = self.board.board[BoardHelper.D8]
                b8_piece_type = Piece.get_piece_type(b8_piece)
                c8_piece_type = Piece.get_piece_type(c8_piece)
                d8_piece_type = Piece.get_piece_type(d8_piece)

                if b8_piece_type == c8_piece_type == d8_piece_type == Piece.NONE:
                    moves.append(Move(start_square, BoardHelper.C8, flag=Move.CASTLE_FLAG))

        return moves

    def generate_pawn_promotions(self, start_square, target_square, captures_only=False):
        if captures_only:
            return [Move(start_square, target_square, Move.PROMOTE_TO_QUEEN_FLAG)]

        promotion_flags = [Move.PROMOTE_TO_QUEEN_FLAG, Move.PROMOTE_TO_ROOK_FLAG,
                           Move.PROMOTE_TO_KNIGHT_FLAG, Move.PROMOTE_TO_BISHOP_FLAG]

        moves = []
        for flag in promotion_flags:
            moves.append(Move(start_square, target_square, flag=flag))

        return moves

    def generate_pawn_moves(self, start_square, piece, captures_only=False):
        file = BoardHelper.get_file(start_square)
        is_on_right_edge = file == 7
        is_on_left_edge = file == 0
        rank = BoardHelper.get_rank(start_square)
        piece_color = Color.get_piece_color(piece)

        pawn_direction = Offset.UP if piece_color == Color.WHITE else Offset.DOWN
        pawn_starting_rank = 1 if piece_color == Color.WHITE else 6
        pawn_promotion_rank = 7 if piece_color == Color.WHITE else 0

        moves = []

        # calculate forward moves
        if not captures_only:
            forward_offsets = [pawn_direction, pawn_direction * 2] if rank == pawn_starting_rank else [pawn_direction]
            for offset in forward_offsets:
                target_square = start_square + offset
                target_piece = self.board.board[target_square]
                target_piece_type = Piece.get_piece_type(target_piece)

                if target_piece_type == Piece.NONE:
                    # calculate promotion moves
                    if BoardHelper.get_rank(target_square) == pawn_promotion_rank:
                        moves += self.generate_pawn_promotions(start_square, target_square, captures_only=captures_only)
                    else:
                        flag = Move.NO_FLAG if offset == pawn_direction else Move.PAWN_TWO_UP_FLAG
                        moves.append(Move(start_square, target_square, flag=flag))

        # calculate attacking moves
        pawn_attacking_directions = [Offset.TOP_LEFT, Offset.TOP_RIGHT] if piece_color == Color.WHITE \
            else [Offset.BOTTOM_LEFT, Offset.BOTTOM_RIGHT]
        if is_on_left_edge:
            pawn_attacking_directions = pawn_attacking_directions[1:]
        elif is_on_right_edge:
            pawn_attacking_directions = pawn_attacking_directions[:-1]

        for offset in pawn_attacking_directions:
            target_square = start_square + offset
            target_piece = self.board.board[target_square]
            target_piece_type = Piece.get_piece_type(target_piece)
            target_piece_color = Color.get_piece_color(target_piece)

            if target_piece_type != Piece.NONE and target_piece_color == self.opponent_color:
                # calculate promotion moves
                if BoardHelper.get_rank(target_square) == pawn_promotion_rank:
                    moves += self.generate_pawn_promotions(start_square, target_square, captures_only=captures_only)
                else:
                    moves.append(Move(start_square, target_square))

        # calculate en passant moves
        en_passant_offsets = [Offset.LEFT, Offset.RIGHT]
        if is_on_left_edge:
            en_passant_offsets = [Offset.RIGHT]
        elif is_on_right_edge:
            en_passant_offsets = [Offset.LEFT]

        for offset in en_passant_offsets:
            check_square = start_square + offset
            check_file = BoardHelper.get_file(check_square)
            check_piece = self.board.board[check_square]
            check_piece_type = Piece.get_piece_type(check_piece)
            check_piece_color = Color.get_piece_color(check_piece)

            if self.board.en_passant_file == check_file and check_piece_type != Piece.NONE and \
                    check_piece_color == self.opponent_color:
                on_passant_offset = 0
                if offset == Offset.LEFT:
                    on_passant_offset = Offset.TOP_LEFT if self.friendly_color == Color.WHITE else Offset.BOTTOM_LEFT
                elif offset == Offset.RIGHT:
                    on_passant_offset = Offset.TOP_RIGHT if self.friendly_color == Color.BLACK else Offset.BOTTOM_RIGHT
                target_square = start_square + on_passant_offset

                if not self.in_check_after_en_passant(start_square, target_square, check_square):
                    moves.append(Move(start_square, target_square, flag=Move.EN_PASSANT_CAPTURE_FLAG))

        return self.filter_valid_moves(moves)

    def generate_knight_moves(self, start_square, piece, captures_only=False):
        file = BoardHelper.get_file(start_square)
        knight_offsets = [6, -10, 15, -17, 17, -15, 10, -6]  # ordered from leftmost to rightmost moves
        if file == 0:
            knight_offsets = knight_offsets[4:]
        elif file == 1:
            knight_offsets = knight_offsets[2:]
        elif file == 6:
            knight_offsets = knight_offsets[:-2]
        elif file == 7:
            knight_offsets = knight_offsets[:-4]

        moves = []
        for offset in knight_offsets:
            target_square = start_square + offset
            if 0 <= target_square <= 63:
                target_piece = self.board.board[target_square]
                target_piece_type = Piece.get_piece_type(target_piece)
                target_piece_color = Color.get_piece_color(target_piece)

                if target_piece_type == Piece.NONE and not captures_only:
                    moves.append(Move(start_square, target_square))
                elif target_piece_type != Piece.NONE and target_piece_color == self.opponent_color:
                    moves.append(Move(start_square, target_square))

        return self.filter_valid_moves(moves)

    def generate_sliding_moves(self, start_square, piece, captures_only=False):
        piece_type = Piece.get_piece_type(piece)

        moves = []
        directions = []
        directions += MoveGenerator.ORTHOGONAL_DIRECTIONS if piece_type == Piece.ROOK or piece_type == Piece.QUEEN \
            else []
        directions += MoveGenerator.DIAGONAL_DIRECTIONS if piece_type == Piece.BISHOP or piece_type == Piece.QUEEN \
            else []

        for i in range(len(directions)):
            offset = directions[i]
            for j in range(self.num_squares_to_edge(start_square, offset)):
                target_square = start_square + (offset * (j + 1))

                if 0 <= target_square <= 63:
                    target_piece = self.board.board[target_square]
                    target_piece_type = Piece.get_piece_type(target_piece)
                    target_piece_color = Color.get_piece_color(target_piece)

                    if target_piece_type != Piece.NONE and target_piece_color == self.friendly_color:
                        break
                    elif target_piece_type != Piece.NONE and target_piece_color == self.opponent_color:
                        moves.append(Move(start_square, target_square))
                        break
                    elif not captures_only:
                        moves.append(Move(start_square, target_square))

        return self.filter_valid_moves(moves)

    def num_squares_to_edge(self, square, offset):
        file = BoardHelper.get_file(square)
        is_on_right_edge = file == 7
        is_on_left_edge = file == 0

        if is_on_right_edge and offset in [Offset.RIGHT, Offset.TOP_RIGHT, Offset.BOTTOM_RIGHT]:
            return 0
        elif is_on_left_edge and offset in [Offset.LEFT, Offset.TOP_LEFT, Offset.BOTTOM_LEFT]:
            return 0

        n = 0
        while True:
            square += offset
            file = BoardHelper.get_file(square)

            is_out_of_top_edge = True if square > 63 else False
            is_out_of_bottom_edge = True if square < 0 else False
            is_out_of_left_edge = True if (file == 0) and offset in [Offset.LEFT, Offset.TOP_LEFT,
                                                                     Offset.BOTTOM_LEFT] else False
            is_out_of_right_edge = True if (file == 7) and offset in [Offset.RIGHT, Offset.TOP_RIGHT,
                                                                      Offset.BOTTOM_RIGHT] else False

            if is_out_of_top_edge or is_out_of_bottom_edge or is_out_of_left_edge or is_out_of_right_edge:
                if is_out_of_left_edge or is_out_of_right_edge:
                    n += 1
                break

            n += 1

        return n

    def in_check(self):
        return self.in_check

    def calculate_attack_data(self):
        directions = MoveGenerator.ORTHOGONAL_DIRECTIONS + MoveGenerator.DIAGONAL_DIRECTIONS
        king_square = self.board.king_square[self.friendly_color]

        # calculate rays from the king to the edge to see if a piece is pinned/king is under check
        for offset in directions:
            n = self.num_squares_to_edge(king_square, offset)
            is_friendly_piece_along_ray = False
            ray_squares = []

            for i in range(n):
                target_square = king_square + (offset * (i + 1))

                if 0 <= target_square <= 63:
                    target_piece = self.board.board[target_square]
                    target_piece_type = Piece.get_piece_type(target_piece)
                    target_piece_color = Color.get_piece_color(target_piece)
                    ray_squares.append(target_square)

                    if target_piece_type != Piece.NONE:
                        if target_piece_color == self.friendly_color:
                            # the first friendly piece we find might be pinned
                            if not is_friendly_piece_along_ray:
                                is_friendly_piece_along_ray = True

                            # this is the second friendly piece we've found along this direction, so pin is not possible
                            else:
                                break
                        else:
                            is_diagonal_dir = offset in MoveGenerator.DIAGONAL_DIRECTIONS
                            is_orthogonal_dir = offset in MoveGenerator.ORTHOGONAL_DIRECTIONS

                            if (is_orthogonal_dir and target_piece_type in [Piece.ROOK, Piece.QUEEN]) or \
                                    (is_diagonal_dir and target_piece_type in [Piece.BISHOP, Piece.QUEEN]):
                                # if friendly piece blocks the attack, it is a pin
                                if is_friendly_piece_along_ray:
                                    self.pin_rays.append(ray_squares)

                                # if there is no friendly piece blocking the attack, it is a check
                                else:
                                    self.check_squares = self.check_squares.union(ray_squares)

                                    self.in_double_check = self.in_check
                                    self.in_check = True
                                    self.board.in_check = self.in_check
                                    self.board.in_double_check = self.in_double_check
                                break
                            else:
                                # if the enemy piece isn't a rook, bishop, or queen, there are no rays to calculate
                                break
                    else:
                        pass
            # if there is a double check, the king is the only piece able to move
            if self.in_double_check:
                break

        for square in range(64):
            piece = self.board.board[square]
            piece_type = Piece.get_piece_type(piece)
            piece_color = Color.get_piece_color(piece)

            if piece_type == Piece.KNIGHT and piece_color == self.opponent_color:
                # temporarily switch the friendly color and opponent color to generate opponent moves
                self.friendly_color, self.opponent_color = self.opponent_color, self.friendly_color
                opponent_moves = self.generate_knight_moves(square, piece)
                self.friendly_color, self.opponent_color = self.opponent_color, self.friendly_color

                for move in opponent_moves:
                    self.opponent_attack_squares.add(move.target_square)
                    # if the opponent piece can capture the king as a move, we are in check
                    if move.target_square == king_square:
                        self.check_squares.add(square)
                        self.check_squares.add(move.target_square)

                        self.in_double_check = self.in_check
                        self.in_check = True
                        self.board.in_check = self.in_check
                        self.board.in_double_check = self.in_double_check

            if piece_type in [Piece.ROOK, Piece.BISHOP, Piece.QUEEN] and piece_color == self.opponent_color:
                directions = MoveGenerator.DIAGONAL_DIRECTIONS + MoveGenerator.ORTHOGONAL_DIRECTIONS
                for offset in directions:
                    n = self.num_squares_to_edge(square, offset)
                    for i in range(n):
                        is_diagonal_dir = offset in MoveGenerator.DIAGONAL_DIRECTIONS
                        is_orthogonal_dir = offset in MoveGenerator.ORTHOGONAL_DIRECTIONS

                        if (is_orthogonal_dir and piece_type in [Piece.ROOK, Piece.QUEEN]) or \
                                (is_diagonal_dir and piece_type in [Piece.BISHOP, Piece.QUEEN]):
                            target_square = square + (offset * (i + 1))
                            if 0 <= target_square <= 63:
                                target_piece = self.board.board[target_square]
                                target_piece_type = Piece.get_piece_type(target_piece)
                                target_piece_color = Color.get_piece_color(target_piece)

                                self.opponent_attack_squares.add(target_square)
                                # if the sliding piece is attacking a piece that is not our king, break
                                if target_piece_type != Piece.NONE:
                                    if not (target_piece_type == Piece.KING and target_piece_color == self.friendly_color):
                                        break

            if piece_type == Piece.PAWN and piece_color == self.opponent_color:
                file = BoardHelper.get_file(square)
                is_on_right_edge = file == 7
                is_on_left_edge = file == 0

                pawn_attacking_directions = [Offset.TOP_LEFT, Offset.TOP_RIGHT] if piece_color == Color.WHITE \
                    else [Offset.BOTTOM_LEFT, Offset.BOTTOM_RIGHT]
                if is_on_left_edge:
                    pawn_attacking_directions = pawn_attacking_directions[1:]
                elif is_on_right_edge:
                    pawn_attacking_directions = pawn_attacking_directions[:-1]

                for offset in pawn_attacking_directions:
                    target_square = square + offset
                    self.opponent_attack_squares.add(target_square)
                    self.opponent_pawn_attack_squares.add(target_square)

                    if target_square == self.board.king_square[self.friendly_color]:
                        self.check_squares.add(square)
                        self.check_squares.add(target_square)

                        self.in_double_check = self.in_check
                        self.in_check = True
                        self.board.in_check = self.in_check
                        self.board.in_double_check = self.in_double_check

            # calculate blocked squares from opponent's king
            if piece_type == Piece.KING and piece_color == self.opponent_color:
                opponent_king_square = self.board.king_square[self.opponent_color]
                file = BoardHelper.get_file(opponent_king_square)
                king_offsets = [Offset.LEFT, Offset.TOP_LEFT, Offset.BOTTOM_LEFT, Offset.DOWN, Offset.UP, Offset.RIGHT,
                                Offset.BOTTOM_RIGHT, Offset.TOP_RIGHT]
                if file == 0:
                    king_offsets = king_offsets[3:]
                elif file == 7:
                    king_offsets = king_offsets[:-3]

                for offset in king_offsets:
                    target_square = opponent_king_square + offset

                    if 0 <= target_square <= 63:
                        self.opponent_attack_squares.add(target_square)

    def in_check_after_en_passant(self, start_square, target_square, check_square):
        king_square = self.board.king_square[self.friendly_color]
        king_rank = BoardHelper.get_rank(king_square)
        king_file = BoardHelper.get_file(king_square)
        rank = BoardHelper.get_rank(start_square)
        file = BoardHelper.get_file(start_square)

        # if the king and pawn aren't on the same rank, being checked by a rook after en passant isn't possible
        if rank != king_rank:
            return False

        direction_to_king = 1 if king_file > file else -1

        # check to see if there are any pieces in between the king and pawn
        for square in range(start_square + direction_to_king, king_square, direction_to_king):
            piece = self.board.board[square]
            piece_type = Piece.get_piece_type(piece)

            if square not in [start_square, check_square, king_square] and piece_type != Piece.NONE:
                return False

        # check to see if there is a rook/queen that will check the king and no other pieces in the way
        square = start_square
        file = BoardHelper.get_file(square)
        while True:
            piece = self.board.board[square]
            piece_type = Piece.get_piece_type(piece)
            piece_color = Color.get_piece_color(piece)

            if square not in [start_square, check_square, king_square]:
                if piece_type in [Piece.ROOK, Piece.QUEEN] and piece_color == self.opponent_color:
                    return True
                elif piece_type != Piece.NONE:
                    return False

            # end search when we reach the edge of the board
            if file == 0 or file == 7:
                break

            # check the direction away from the king
            square -= direction_to_king
            file = BoardHelper.get_file(square)

        return False

    def is_pinned(self, square):
        for ray in self.pin_rays:
            if square in ray:
                return True
        return False

    def is_valid_pinned_move(self, start_square, target_square):
        for ray in self.pin_rays:
            if start_square in ray and target_square in ray:
                return True
        return False

    def filter_valid_moves(self, moves):
        filtered_moves = []
        # filter out pinned pieces and invalid pinned moves and checks
        for move in moves:
            if self.is_pinned(move.start_square):
                if self.is_valid_pinned_move(move.start_square, move.target_square):
                    filtered_moves.append(move)
            else:
                filtered_moves.append(move)

        if self.in_check:
            # filter for only moves that protect the king from check
            filtered_check_moves = []
            for move in filtered_moves:
                if move.target_square in self.check_squares:
                    filtered_check_moves.append(move)

            return filtered_check_moves

        return filtered_moves


if __name__ == "__main__":
    board = Board()
    board.board[37] = Piece.KING | Color.WHITE
    board.board[43] = Piece.PAWN | Color.BLACK
    board.king_square[Color.WHITE] = 37
    board.in_check = True

    board.print_indexes()
    mg = MoveGenerator(board)

    moves = mg.generate_moves()
    print([str(move) for move in moves])
