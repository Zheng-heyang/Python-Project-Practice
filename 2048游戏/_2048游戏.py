
from pickle import TRUE
import pygame
import random
import numpy as np
import sys

# init
pygame.init()

# define colors
COLORS = {
    0: (204, 192, 179),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    'background': (187, 173, 160),
    'text': (119, 110, 101),
    'text_light': (249, 246, 242)
    }

SIZE = 4
GRID_SIZE = 100
GRID_MARGIN = 10
WIDTH = SIZE * (GRID_SIZE + GRID_MARGIN) + GRID_MARGIN
HEIGHT = WIDTH + 50 
FONT = pygame.font.SysFont("Arial",36,bold=True)
SMALL_FONT = pygame.font.SysFont("Arial",24,bold=True)

# create windows
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

class Game2048:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = np.zeros((SIZE, SIZE),dtype=int)
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()
        self.game_over = False

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(SIZE) for j in range(SIZE) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def move(self, direction):
        # 0: up, 1: right, 2: down, 3: left
        moved = False
        board_before = self.board.copy()

        if direction == 0: # up
            self.board = self.board.T
        elif direction == 1: # right
            self.board = np.fliplr(self.board)
        elif direction == 2: # down
            self.board = np.fliplr(self.board).T

        for i in range(SIZE):
            row = self.board[i]
            # remove "0"
            non_zero  = row[row != 0]
            # combine the same numbers
            for j in range(len(non_zero) - 1):
                if non_zero[j] == non_zero[j + 1]:
                    non_zero[j] *= 2
                    non_zero[j + 1] = 0
                    self.score += non_zero[j]
            # remove "0" again
            non_zero = non_zero[non_zero != 0]
            # add "0"
            new_row = np.zeros(SIZE, dtype=int)
            new_row[:len(non_zero)] = non_zero
            self.board[i]= new_row

        if direction == 0: # up
            self.board = self.board.T
        elif direction == 1: # right
            self.board = np.fliplr(self.board)
        elif direction == 2: # down
            self.board = np.fliplr(self.board.T)

        if not np.array_equal(board_before, self.board):
            moved = True
            self.add_new_tile()
            if self.is_game_over():
                self.game_over = True

        return moved
    def is_game_over(self):
        if 0 in self.board:
            return False

        for i in range(SIZE):
            for j in range(SIZE):
                if j < SIZE - 1 and self.board[i][j] == self.board[i][j + 1]:
                    return False
                if i < SIZE - 1 and self.board[i][j] == self.board[i + 1][j]:
                    return False

        return True

    def draw(self):
        screen.fill(COLORS['background'])

        # draw scores
        score_text = SMALL_FONT.render(f"Score: {self.score}", True, COLORS['text_light'])
        screen.blit(score_text, (10, 10))

        # draw button "Restart"
        restart_text = SMALL_FONT.render("Press R to restart", True, COLORS['text_light'])
        screen.blit(restart_text, (WIDTH - 180, 10))

        # draw game
        for i in range(SIZE):
            for j in range(SIZE):
                value = self.board[i][j]
                color = COLORS[value] if value in COLORS else COLORS[2048]

                # calculate grids' positions
                x = GRID_MARGIN + j * (GRID_SIZE + GRID_MARGIN)
                y = 50 + GRID_MARGIN + i * (GRID_SIZE + GRID_MARGIN)

                # draw background
                pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE), 0, 5)

                # draw number if it exists
                if value != 0:
                    text_color = COLORS['text'] if value <= 4 else COLORS['text_light']
                    text = FONT.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=(x + GRID_SIZE // 2, y + GRID_SIZE // 2))
                    screen.blit(text, text_rect)

        # display ending information if gameover
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((238, 228, 218, 180))
            screen.blit(overlay, (0, 0))

            game_over_text = FONT.render("Gameover!", True, COLORS['text'])
            score_text = FONT.render(f"Score: {self.score}", True, COLORS['text'])
            restart_text = SMALL_FONT.render("Press R to restart", True, COLORS['text'])

            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + score_text.get_height() // 2))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + game_over_text.get_height()))

        pygame.display.flip()

def main():
    game = Game2048()
    clock = pygame.time.Clock()

    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                elif not game.game_over:
                    if event.key == pygame.K_UP:
                        game.move(0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1)
                    elif event.key == pygame.K_DOWN:
                        game.move(2)
                    elif event.key == pygame.K_LEFT:
                        game.move(3)

        game.draw()
        clock.tick(30)

if __name__ == "__main__":
    main()