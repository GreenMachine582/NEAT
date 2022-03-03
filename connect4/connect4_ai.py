
import sys
import os
import random
import numpy as np
import pygame as pg
from neat import NEAT
__file__ = "connect4_ai"

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_WIDTH = 640
NETWORK_WIDTH = 480

# Flags
OVERWRITE = False
AI = True
DRAW_NETWORK = True

# Colors
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
GREY = [200, 200, 200]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
DARKER = -65

# os.environ['SDL_VIDEO_CENTERED'] = '1'
os.environ['SDL_VIDEO_WINDOW_POS'] = "250,250"
DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def changeColour(colour, change_by=DARKER):
    R = 0 if colour[0] + change_by < 0 else 255 if colour[0] + change_by > 255 else colour[0] + change_by
    G = 0 if colour[1] + change_by < 0 else 255 if colour[1] + change_by > 255 else colour[1] + change_by
    B = 0 if colour[2] + change_by < 0 else 255 if colour[2] + change_by > 255 else colour[2] + change_by
    return [R, G, B]


class Piece:
    BOARDER = 38
    TOP_PADDING = 80
    SPACING = 10

    def __init__(self, pos, rows, cols, colour):
        self.pos = pos
        self.center_pos = [0, 0]
        self.radius = 30
        self.diameter = self.radius * 2
        self.filled = False
        self.colour = colour

        self.generate(rows, cols)

    def generate(self, rows, cols):
        self.diameter = ((HEIGHT - self.BOARDER * 2) / max(rows, cols)) - self.SPACING
        self.radius = self.diameter / 2
        pos = [int(self.BOARDER + (self.pos[1] * (self.diameter + self.SPACING))),
               int(self.BOARDER + self.TOP_PADDING + (self.pos[0] * (self.diameter + self.SPACING)))]
        self.center_pos = [int(pos[0] + self.radius), int(pos[1] + self.radius)]

    def draw(self, window, boarder=5):
        pg.draw.circle(window, changeColour(self.colour), self.center_pos, self.radius)
        pg.draw.circle(window, self.colour, self.center_pos, self.radius-boarder)

    def update(self, colour):
        self.colour = colour
        self.filled = True


class Connect4:
    ROWS, COLUMNS = 6, 7
    PLAYERS = {1: RED, 2: YELLOW}
    EMPTY = WHITE
    LENGTH = 4

    def __init__(self):
        self.board = []
        self.colour = BLUE
        self.current_player = 1

        self.generate()

    def generate(self):
        self.board = [[Piece([h, j], self.ROWS, self.COLUMNS, self.EMPTY) for j in range(self.COLUMNS)] for h in range(self.ROWS)]

    def draw(self, window, boarder=10):
        window.fill(changeColour(self.colour))
        pg.draw.rect(window, self.colour, ([boarder, boarder], [GAME_WIDTH - (boarder * 2), HEIGHT - (boarder * 2)]))
        for row in self.board:
            for piece in row:
                piece.draw(window)

    def move(self, move):
        possible_move = None
        for h in range(self.ROWS):
            if not self.board[h][move].filled:
                possible_move = h
        if possible_move is not None:
            self.board[possible_move][move].update(self.PLAYERS[self.current_player])
            return possible_move
        return False

    def switchPlayer(self):
        self.current_player = 2 if self.current_player == 1 else 1

    def winChecker(self, y, x):
        draw = True
        colour = self.PLAYERS[self.current_player]

        directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]
        surviving_directions = directions[:]
        for direction in directions:
            for n in range(1, self.LENGTH):
                a, b = y + (n*direction[0]), x + (n*direction[1])
                if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                    piece = self.board[a][b]
                    if piece.colour == self.EMPTY:
                        draw = False
                    if piece.colour != colour:
                        surviving_directions.remove(direction)
                        break
                else:
                    if direction in surviving_directions:
                        surviving_directions.remove(direction)
                    break
        if surviving_directions:
            print(surviving_directions)
            return self.current_player

        return 0 if draw else -1


def generate_net(nodes):
    net_nodes = {}
    input_nodes, hidden_nodes, output_nodes = nodes[0], nodes[1], nodes[2]

    for i in input_nodes:
        x = 50
        y = 140 + i * 60
        net_nodes[i] = [(int(x), int(y)), BLUE]
    for i in output_nodes:
        x = NETWORK_WIDTH - 50
        y = HEIGHT / 2
        net_nodes[i] = [(int(x), int(y)), RED]

    for i in hidden_nodes:
        x = random.randint(NETWORK_WIDTH / 3, int(NETWORK_WIDTH * (2.0 / 3)))
        y = random.randint(20, HEIGHT - 20)
        net_nodes[i] = [(int(x), int(y)), BLACK]
    return net_nodes


def render_net(display, nodes, connections):
    for c in connections:
        pg.draw.line(display, GREEN, nodes[c[0]][0], nodes[c[1]][0], 3)
    for n in nodes:
        pg.draw.circle(display, nodes[n][1], nodes[n][0], 7)


def main():
    pg.init()

    display = pg.display.set_mode((WIDTH, HEIGHT), depth=32)
    pg.display.set_caption("Connect 4 with NEAT")
    game_display = pg.Surface((GAME_WIDTH, HEIGHT))
    network_display = pg.Surface((NETWORK_WIDTH, HEIGHT))
    clock = pg.time.Clock()

    connect4 = Connect4()

    # nodes = [[0, 1, 2, 3], [5, 6, 7], [4]]
    # connections = [(0, 4), (1, 4), (2, 4), (3, 4), (0, 5), (5, 4), (3, 7), (7, 6), (6, 4), (6, 5)]
    # net_nodes = generate_net(nodes)

    run, match = True, True
    while run:
        display.fill(BLACK)
        network_display.fill(WHITE)

        connect4.draw(game_display)

        # render_net(network_display, net_nodes, connections)
        move = None
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_1, pg.K_KP1]:
                    move = 1
                    break
                elif event.key in [pg.K_2, pg.K_KP2]:
                    move = 2
                    break
                elif event.key in [pg.K_3, pg.K_KP3]:
                    move = 3
                    break
                elif event.key in [pg.K_4, pg.K_KP4]:
                    move = 4
                    break
                elif event.key in [pg.K_5, pg.K_KP5]:
                    move = 5
                    break
                elif event.key in [pg.K_6, pg.K_KP6]:
                    move = 6
                    break
                elif event.key in [pg.K_7, pg.K_KP7]:
                    move = 7
                    break
        if move is not None and match:
            possible_move = connect4.move(move - 1)
            if possible_move:
                game_state = connect4.winChecker(possible_move, move - 1)
                if game_state != -1:
                    if game_state == 0:
                        print("draw")
                    else:
                        print(f"player {game_state} won")
                    match = False
                connect4.switchPlayer()

        display.blit(game_display, (0, 0))
        display.blit(network_display, (GAME_WIDTH, 0))
        pg.display.update()
        clock.tick(40)

    pg.quit()
    quit()


if __name__ == "__main__":
    main()
