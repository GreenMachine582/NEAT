
import pygame as pg
import random

import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.4'
__date__ = '16/03/2022'

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_WIDTH, GAME_HEIGHT = HEIGHT, HEIGHT

# Colors
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
GREY = [200, 200, 200]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]


class Piece:
    BOARDER = 38
    TOP_PADDING = 80
    SPACING = 10

    def __init__(self, coordinates, rows, cols, colour):
        self.coordinates = coordinates
        self.center_pos = [0, 0]
        self.radius = 30
        self.diameter = self.radius * 2
        self.active = False
        self.visible = True
        self.colour = colour
        self.highlight_colour = self.colour

        self.generate(rows, cols)

    def generate(self, rows, cols):
        self.diameter = ((GAME_HEIGHT - self.BOARDER * 2) / max(rows, cols)) - self.SPACING
        self.radius = self.diameter / 2
        pos = [int(self.BOARDER + (self.coordinates[1] * (self.diameter + self.SPACING))),
               int(self.BOARDER + self.TOP_PADDING + (self.coordinates[0] * (self.diameter + self.SPACING)))]
        self.center_pos = [int(pos[0] + self.radius), int(pos[1] + self.radius)]

    def draw(self, window, boarder=5):
        if self.visible:
            pg.draw.circle(window, mlpg.changeColour(self.highlight_colour), self.center_pos, self.radius)
            pg.draw.circle(window, self.colour, self.center_pos, self.radius-boarder)

    def setColour(self, colour):
        self.colour = colour
        self.highlight_colour = colour
        self.active = True


class Connect4:
    ROWS, COLUMNS = 6, 7
    PLAYERS = {1: RED, 2: YELLOW}
    EMPTY = WHITE
    LENGTH = 4
    GAME_STATES = {-2: 'Invalid move', -1: '', 0: 'Draw', 1: 'Player 1 Wins', 2: 'Player 2 Wins'}
    BOARDER = 0

    def __init__(self):
        self.board = []
        self.active = True
        self.visible = True
        self.colour = {'background': BLUE}
        self.current_player = 1
        self.opponent = 2 if self.current_player == 1 else 1
        self.match = True
        self.turn = 0

        self.generate()

    def generate(self):
        self.board = [[Piece([h, j], self.ROWS, self.COLUMNS, self.EMPTY) for j in range(self.COLUMNS)]
                      for h in range(self.ROWS)]

    def reset(self):
        self.generate()
        self.match = True
        self.turn = 0
        self.current_player = 1
        self.opponent = 2 if self.current_player == 1 else 1

    def draw(self, window, boarder=10):
        window.fill(mlpg.changeColour(self.colour['background']))
        pg.draw.rect(window, self.colour['background'], ([boarder, boarder],
                                                         [GAME_WIDTH - (boarder * 2), GAME_HEIGHT - (boarder * 2)]))
        message = mlpg.Message(f"Player {self.current_player}'s turn!", [int(GAME_WIDTH / 2), 60], size=40)
        message.draw(window)
        for row in self.board:
            for piece in row:
                piece.draw(window)

    def neatMove(self, genome):
        possible_moves = {}
        for i in range(self.COLUMNS):
            possible_move = self.getPossibleMove(i)
            if possible_move is not None:
                possible_moves[tuple(possible_move)] = 0
        for possible_move in possible_moves:
            directions, _ = self.getPieceSlices(possible_move)
            for direction_pair in directions:
                for direction in directions[direction_pair]:
                    if directions[direction_pair][direction] is not None:
                        inputs = directions[direction_pair][direction]
                        possible_moves[possible_move] += genome.forward(inputs)[0]
        sorted_moves = ml.dict.sortByValues(possible_moves)
        max_min_keys = ml.list.findMaxMin(list(sorted_moves.keys()))
        move = random.choice(sorted_moves[max_min_keys['max']['value']])
        return move

    def makeMove(self, move):
        if move is not None:
            self.board[move[0]][move[1]].setColour(self.PLAYERS[self.current_player])
            self.turn += 1
        game_state = self.winChecker(move) if move is not None else -2
        return game_state

    def getPossibleMove(self, possible_move):
        move = None
        for h in range(self.ROWS):
            if not self.board[h][possible_move].active:
                move = h
            else:
                break
        if move is None:
            return None
        return [move, possible_move]

    def showWin(self, move, direction_pair, colour):
        self.board[move[0]][move[1]].highlight_colour = colour
        for direction in direction_pair:
            for n in range(1, self.LENGTH):
                a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                    piece = self.board[a][b]
                    if piece.colour == self.PLAYERS[self.current_player]:
                        self.board[a][b].highlight_colour = colour
                    else:
                        break
                else:
                    break

    def switchPlayer(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.opponent = 2 if self.current_player == 1 else 1

    def getPieceSlices(self, move):
        # don't need to check up
        directions = {'vertical': {(1, 0): [], (-1, 0): None},
                      'horizontal': {(0, 1): [], (0, -1): []},
                      'diagonal1': {(-1, 1): [], (1, -1): []},
                      'diagonal2': {(1, 1): [], (-1, -1): []}}
        counts = {}
        for direction_pair in directions:
            counts[direction_pair] = []
            for direction in directions[direction_pair]:
                connection_count = 0
                count_connections = True
                if directions[direction_pair][direction] is not None:
                    directions[direction_pair][direction].append(self.current_player)
                    for n in range(1, self.LENGTH):
                        a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                        if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                            piece = self.board[a][b]
                            if piece.colour == self.PLAYERS[self.current_player]:
                                directions[direction_pair][direction].append(self.current_player)
                                if count_connections:
                                    connection_count += 1
                            else:
                                count_connections = False
                                if piece.colour == self.PLAYERS[self.opponent]:
                                    directions[direction_pair][direction].append(self.opponent)
                                elif piece.colour == self.EMPTY:
                                    directions[direction_pair][direction].append(0)
                        else:
                            directions[direction_pair][direction].append(-1)  # out of bounds

                counts[direction_pair].append(connection_count)
        return directions, counts

    def winChecker(self, move):
        draw, win = True, False
        
        directions, counts = self.getPieceSlices(move)
        for direction_pair in counts:
            if sum(counts[direction_pair]) >= self.LENGTH - 1:
                self.showWin(move, directions[direction_pair], GREEN)
                win = True
        if win:
            return self.current_player

        for row in self.board:
            for piece in row:
                if piece.colour == self.EMPTY:
                    draw = False

        return 0 if draw else -1
