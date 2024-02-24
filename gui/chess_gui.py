from board import Board
from constants import *
import time

import pygame


class ChessGUI:
    GAME_OVER = 0
    GAME_RUNNING = 1

    def __init__(self, screen):
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.board = Board()

    def draw(self):
        pieces_to_ascii = {
            Piece.KING: "♚",
            Piece.QUEEN: "♛",
            Piece.ROOK: "♜",
            Piece.BISHOP: "♝",
            Piece.KNIGHT: "♞",
            Piece.PAWN: "♟︎",
        }

        screen.fill("black")
        square_side_length = 100 if self.width >= 1000 and self.height >= 1000 else 50
        margin_left = (self.width - square_side_length * 8) // 2
        margin_top = (self.height - square_side_length * 8) // 2
        white_square_color = (242, 225, 195)
        black_square_color = (195, 160, 130)
        offset = 0
        row = 7
        col = 0
        for i in range(64):
            offset += 1
            square_color = white_square_color if (i + row) % 2 else black_square_color
            x = col * square_side_length + margin_left
            y = row * square_side_length + margin_top
            square_coords = (x, y)
            square_size = (square_side_length, square_side_length)

            square = pygame.Rect(square_coords, square_size)
            pygame.draw.rect(self.screen, square_color, square)

            font = pygame.font.SysFont("mspgothic", 100)
            piece = self.board.board[i]
            piece_type = piece & Piece.MASK
            piece_color = piece & Color.MASK
            if piece_type != Piece.NONE:
                ascii_piece = pieces_to_ascii[piece_type]
                text = font.render(ascii_piece, True, "black" if piece_color == Color.BLACK else "white", square_color)
                screen.blit(text, square)

            col += 1
            if (i + 1) % 8 == 0:
                col = 0
                row -= 1

        pygame.display.flip()

    def update(self):
        pass

    def on_mouse_down(self):
        pass

    def state(self):
        return ChessGUI.GAME_RUNNING


if __name__ == "__main__":
    pygame.init()
    HEIGHT = 1000
    WIDTH = 1000
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    running = True
    board = ChessGUI(screen)
    while running:
        board.draw()
        board.update()

        running = True if board.state() else False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
