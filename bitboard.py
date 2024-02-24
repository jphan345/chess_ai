import numpy as np
from constants import *


class BitBoard:
    def __init__(self):
        self.black_pawns_bb   = np.uint64(0b0000000011111111000000000000000000000000000000000000000000000000)
        self.black_rooks_bb   = np.uint64(0b1000000100000000000000000000000000000000000000000000000000000000)
        self.black_knights_bb = np.uint64(0b0100001000000000000000000000000000000000000000000000000000000000)
        self.black_bishops_bb = np.uint64(0b0010010000000000000000000000000000000000000000000000000000000000)
        self.black_queens_bb  = np.uint64(0b0000100000000000000000000000000000000000000000000000000000000000)
        self.black_king_bb    = np.uint64(0b0001000000000000000000000000000000000000000000000000000000000000)

        self.white_pawns_bb   = np.uint64(0b0000000000000000000000000000000000000000000000001111111100000000)
        self.white_rooks_bb   = np.uint64(0b0000000000000000000000000000000000000000000000000000000010000001)
        self.white_knights_bb = np.uint64(0b0000000000000000000000000000000000000000000000000000000001000010)
        self.white_bishops_bb = np.uint64(0b0000000000000000000000000000000000000000000000000000000000100100)
        self.white_queens_bb  = np.uint64(0b0000000000000000000000000000000000000000000000000000000000010000)
        self.white_king_bb    = np.uint64(0b0000000000000000000000000000000000000000000000000000000000001000)

    def display(self):
        square_mask = np.uint64(0b1000000000000000000000000000000000000000000000000000000000000000)
        for i in range(64):
            if self.white_pawns_bb & square_mask:
                print(" P ", end="")
            elif self.white_rooks_bb & square_mask:
                print(" R ", end="")
            elif self.white_knights_bb & square_mask:
                print(" N ", end="")
            elif self.white_bishops_bb & square_mask:
                print(" B ", end="")
            elif self.white_queens_bb & square_mask:
                print(" Q ", end="")
            elif self.white_king_bb & square_mask:
                print(" K ", end="")
            elif self.black_pawns_bb & square_mask:
                print(" p ", end="")
            elif self.black_rooks_bb & square_mask:
                print(" r ", end="")
            elif self.black_knights_bb & square_mask:
                print(" n ", end="")
            elif self.black_bishops_bb & square_mask:
                print(" b ", end="")
            elif self.black_queens_bb & square_mask:
                print(" q ", end="")
            elif self.black_king_bb & square_mask:
                print(" k ", end="")
            else:
                print(" - ", end="")

            if (i + 1) % 8 == 0:
                print()
            square_mask = square_mask >> np.uint8(1)


if __name__ == "__main__":
    bb = BitBoard()
    bb.display()
