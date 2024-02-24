from constants import *


class PieceList:
    def __init__(self):
        self.occupied_squares = set()
        self.num_pieces = 0

    def count(self):
        return self.num_pieces

    def add_piece(self, square):
        self.occupied_squares.add(square)
        self.num_pieces += 1

    def remove_piece(self, square):
        self.remove_piece(square)
        self.num_pieces -= 1
