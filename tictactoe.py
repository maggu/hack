#!/usr/bin/env python3

# Copyright (C) 2019  C C Magnus Gustavsson
# Released under the GNU General Public License

"""Tic-tac-toe / noughts and crosses / Xs and Os using Pygame

Choose if each side is to be played by the computer or a human
"""

import pygame
import sys

from math import sqrt
from random import choice
from time import sleep

# Define the colors (RGB)
BLACK = ( 16,  16,  16)
GREEN = (128, 192, 128)
WHITE = (255, 255, 255)

# For easy translation
STRINGS = {
    'player':   "Player",
    'computer': "Computer",
    'human':    "Human"
}

# Initialize graphics
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# Set grid position and sizes
INFO = pygame.display.Info()
WIDTH, HEIGHT = INFO.current_w, INFO.current_h
SIZE = min(WIDTH, HEIGHT)

START_X = (WIDTH - SIZE) // 2
START_Y = (HEIGHT - SIZE) // 2

SQUARE_SIZE = SIZE // 3
SYMBOL_SIZE = SIZE // 10
LINE_SIZE = SIZE // 20

# Player selection
COMPUTER = 1
HUMAN = 2
MENU = [
    # text, x, y, color
    ["{} {{}}".format(STRINGS['player']), 4, 4, BLACK],
    ["1 - {}".format(STRINGS['computer']), 5, 5, WHITE],
    ["2 - {}".format(STRINGS['human']), 5, 6, WHITE]
]

# Initialize pygame
pygame.init()

# Fonts
FONT = 'freesansbold.ttf'
LARGE_FONT = pygame.font.Font(FONT, SIZE // 16)
SMALL_FONT = pygame.font.Font(FONT, SIZE // 32)

# X and O shapes
X_INNER = LINE_SIZE // sqrt(2)
X_OUTER = (SYMBOL_SIZE - LINE_SIZE / 2) // sqrt(2)

O_INNER = SYMBOL_SIZE - LINE_SIZE
O_OUTER = SYMBOL_SIZE


# Grid coordinates for the squares
POSITION_X = [0, 1, 2, 0, 1, 2, 0, 1, 2]
POSITION_Y = [2, 2, 2, 1, 1, 1, 0, 0, 0]

# The two diagonals
DIAGONALS = [
    [0, 4, 8], [2, 4, 6]
]

# All possible ways to place three in a row
ROWS = [
    [0, 4, 8], [2, 4, 6], [0, 1, 2], [3, 4, 5],
    [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8]
]

WIN_COUNTS = [(3, 0), (0, 3)] # Three in a row

# Computer heuristic
COUNT_PRIORITIES = [
    [(2, 0), (0, 2), (1, 0)], # Player 1
    [(0, 2), (2, 0), (0, 1)]  # Player 2
]
SQUARE_PRIORITIES = [
    [4],          # Center
    [0, 2, 6, 8], # Corner
    [1, 3, 5, 7]  # Remaining
]

def get_key(any_key=False):
    """Get a number key between 1 and 9, or any key"""
    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if any_key:
                return None
            for base in [pygame.K_0, pygame.K_KP0]:
                if base + 1 <= event.key <= base + 9:
                    return event.key - base

def draw_menuitem(player, line, invert=False):
    """Draw an item in the player selection menu"""
    item = MENU[line]
    text = item[0].format(player + 1)
    x = LINE_SIZE * item[1]
    y = LINE_SIZE * (5 * player + item[2])
    if invert:
        color, background = GREEN, item[3]
    else:
        color, background = item[3], GREEN
    text = SMALL_FONT.render(text, True, color, background)
    rect = text.get_rect()
    rect.left, rect.top = x, y
    SCREEN.blit(text, rect)

def player_select():
    """Select which player is to be played by the computer"""
    SCREEN.fill(GREEN)
    is_computer = [None, None]
    for player in range(2):
        for line in range(3):
            draw_menuitem(player, line)
        pygame.display.flip()
        while True:
            key = get_key()
            if key == COMPUTER:
                is_computer[player] = True
                draw_menuitem(player, 1, True)
                pygame.display.flip()
                break
            if key == HUMAN:
                is_computer[player] = False
                draw_menuitem(player, 2, True)
                pygame.display.flip()
                break
    sleep(0.5)
    return is_computer

def draw_line(start_pos, end_pos):
    """Draw a black line"""
    pygame.draw.line(SCREEN, BLACK, start_pos, end_pos, LINE_SIZE)

def draw_grid():
    """Draw the 3 times 3 grid"""
    SCREEN.fill(GREEN)
    end_x = START_X + SIZE
    end_y = START_Y + SIZE
    for i in range(0, SIZE, SQUARE_SIZE):
        draw_line((START_X + i, START_Y), (START_X + i, end_y))
        draw_line((START_X, START_Y + i), (end_x, START_Y + i))
    for i in range(9):
        text = LARGE_FONT.render(str(i + 1), True, WHITE, GREEN)
        rect = text.get_rect()
        rect.center = get_position(i)
        SCREEN.blit(text, rect)
    pygame.display.flip()

def draw_x(x, y, color):
    """Mark a square with an X"""
    points = [(x,                     y - X_INNER),
              (x + X_OUTER,           y - X_OUTER - X_INNER),
              (x + X_OUTER + X_INNER, y - X_OUTER),
              (x + X_INNER,           y),
              (x + X_OUTER + X_INNER, y + X_OUTER),
              (x + X_OUTER,           y + X_OUTER + X_INNER),
              (x,                     y + X_INNER),
              (x - X_OUTER,           y + X_OUTER + X_INNER),
              (x - X_OUTER - X_INNER, y + X_OUTER),
              (x - X_INNER,           y),
              (x - X_OUTER - X_INNER, y - X_OUTER),
              (x - X_OUTER,           y - X_OUTER - X_INNER)]
    pygame.draw.polygon(SCREEN, color, points)

def draw_o(x, y, color):
    """Mark a square with an O"""
    pygame.draw.circle(SCREEN, color, (x, y), O_OUTER)
    pygame.draw.circle(SCREEN, GREEN, (x, y), O_INNER)

def draw_mark(player, square, color=WHITE, flip=True):
    """Mark a square"""
    x, y = get_position(square)
    if player == 1:
        draw_x(x, y, color)
    elif player == 2:
        draw_o(x, y, color)
    if flip:
        pygame.display.flip()

def square_to_coord(start, position):
    """Convert position to screen coordinates"""
    return start + position * SQUARE_SIZE + SQUARE_SIZE // 2

def get_position(number):
    """Get screen coordinates for a square"""
    x = square_to_coord(START_X, POSITION_X[number])
    y = square_to_coord(START_Y, POSITION_Y[number])
    return x, y

def analyze(state):
    """Get player counts for all rows"""
    row_state = [[state[s] for s in row] for row in ROWS]
    return [(row.count(1), row.count(2)) for row in row_state]

def computer_select(player, counts, state):
    """Choose a square for the computer to play,
    using a heuristic that won't always play optimally"""
    sleep(0.5)
    for priority in COUNT_PRIORITIES[player - 1]:
        good = [r for r, c in zip(ROWS, counts) if c == priority]
        if good:
            diagonal = [r for r in good if r in DIAGONALS]
            if diagonal:
                row = choice(diagonal)
            else:
                row = choice(good)
            for square in row:
                if state[square] == 0:
                    return square
    for squares in SQUARE_PRIORITIES:
        empty = [s for s in squares if state[s] == 0]
        if empty:
            return choice(empty)

def game_over(state, keep_color):
    """Paint non-winning squares black"""
    for square in [s for s in range(9) if not s in keep_color]:
        draw_mark(state[square], square, color=BLACK, flip=False)
    pygame.display.flip()
    get_key(any_key=True)

def play_game():
    """Play one game"""
    is_computer = player_select()
    counts = []
    player = 1
    state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    draw_grid()
    while True:
        if is_computer[player - 1]:
            square = computer_select(player, counts, state)
        else:
            while True:
                square = get_key() - 1
                # Check that a human player chose a valid square
                if state[square] == 0:
                    break
        # Mark the square as belonging to the player
        state[square] = player
        if player == 1 and 0 not in state:
            # It's a draw
            game_over(state, [])
            break
        draw_mark(player, square)
        counts = analyze(state)
        wins = (r for r, c in zip(ROWS, counts) if c in WIN_COUNTS)
        win = next(wins, None)
        if win:
            game_over(state, win)
            break
        # Other player's turn (1 -> 2, 2 -> 1)
        player = 3 - player

while True:
    play_game()
