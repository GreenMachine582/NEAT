
import random

import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.5'
__date__ = '21/03/2022'

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
        self.radius = 30

        self.active = False
        self.show = True
        self.colour = colour

        self.radius = (((GAME_HEIGHT - self.BOARDER * 2) / max(rows, cols)) - self.SPACING) / 2
        self.pos = (self.BOARDER + (self.coordinates[1] * (self.radius * 2 + self.SPACING)),
                    self.BOARDER + self.TOP_PADDING + (self.coordinates[0] * (self.radius * 2 + self.SPACING)))

        self.circle = mlpg.shape.Circle(self.pos, self.colour, self.radius, 'tl')
        self.circle_boarder = mlpg.shape.Circle(self.pos, mlpg.changeColour(colour, -70), self.radius, 'tl')

        self.update()

    def update(self, **kwargs):
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
            self.circle.update(colour=self.colour)
            self.circle_boarder.update(colour=mlpg.changeColour(kwargs['colour'], -70))
            self.active = True
        if 'highlight_colour' in kwargs:
            self.circle_boarder.update(colour=mlpg.changeColour(kwargs['highlight_colour'], -70))
        if 'active' in kwargs:
            self.active = kwargs['active']
        if 'show' in kwargs:
            self.show = kwargs['show']

    def draw(self, surface, width=5):
        if self.show:
            self.circle.draw(surface)
            self.circle_boarder.draw(surface, width)


class Connect4:
    ROWS, COLUMNS = 6, 7
    PLAYERS = {1: RED, 2: YELLOW}
    EMPTY = WHITE
    INVALID_MOVE = -2
    LENGTH = 4
    GAME_STATES = {-2: 'Invalid move', -1: '', 0: 'Draw', 1: 'Player 1 Wins', 2: 'Player 2 Wins'}
    BOARDER = 10

    def __init__(self):
        self.board = []
        self.active = True
        self.visible = True
        self.colour = {'background': BLUE}
        self.current_player = 1
        self.opponent = 2 if self.current_player == 1 else 1
        self.match = True
        self.turn = 0

        self.board_background = mlpg.Rect((GAME_WIDTH / 2, GAME_HEIGHT / 2), self.colour['background'],
                                          [GAME_WIDTH - (self.BOARDER * 2), GAME_HEIGHT - (self.BOARDER * 2)])
        self.player_text = mlpg.Message(f"Player {self.current_player}'s turn!", (int(GAME_WIDTH / 2), 60), size=40)

        self.board = [[Piece([h, j], self.ROWS, self.COLUMNS, self.EMPTY) for j in range(self.COLUMNS)]
                      for h in range(self.ROWS)]

    def reset(self):
        self.board = [[Piece([h, j], self.ROWS, self.COLUMNS, self.EMPTY) for j in range(self.COLUMNS)]
                      for h in range(self.ROWS)]
        self.match = True
        self.turn = 0
        self.current_player = 1
        self.opponent = 2 if self.current_player == 1 else 1

    def draw(self, surface):
        self.player_text.update(text=f"Player {self.current_player}'s turn!")

        surface.fill(mlpg.changeColour(self.colour['background'], -70))
        self.board_background.draw(surface)
        self.player_text.draw(surface)
        for row in self.board:
            for piece in row:
                piece.draw(surface)

    def neatMove(self, genome):
        possible_moves = {}
        for i in range(self.COLUMNS):
            possible_move = self.getPossibleMove(i)
            if possible_move[0] != -2:
                possible_moves[possible_move] = 0
        for possible_move in possible_moves:
            directions, _ = self.getPieceSlices(possible_move)
            for direction_pair in directions:
                for direction in directions[direction_pair]:
                    if directions[direction_pair][direction] is not None:
                        inputs = directions[direction_pair][direction]
                        possible_moves[possible_move] += genome.forward(inputs)[0]
        sorted_moves = ml.dict.combineByValues(possible_moves)
        max_min_keys = ml.list.findMaxMin(list(sorted_moves.keys()))
        move = random.choice(sorted_moves[max_min_keys['max']['value']])
        return move

    def makeMove(self, move: tuple) -> None:
        """
        Receives the move to update the game board and increments turn.
        :param move: tuple[int, int]
        :return:
            - None
        """
        self.board[move[0]][move[1]].update(colour=self.PLAYERS[self.current_player])
        self.turn += 1

    def getPossibleMove(self, possible_move: int) -> tuple:
        """
        Checks each row with given column in board for an available move.
        :param possible_move: int
        :return:
            - move - tuple[int, int]
        """
        move = self.INVALID_MOVE
        for row in range(self.ROWS):
            if self.board[row][possible_move].active:
                break
            move = row
        return move, possible_move

    def showWin(self, move, direction_pair, colour):
        self.board[move[0]][move[1]].update(highlight_colour=colour)
        for direction in direction_pair:
            for n in range(1, self.LENGTH):
                a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                    piece = self.board[a][b]
                    if piece.colour == self.PLAYERS[self.current_player]:
                        self.board[a][b].update(highlight_colour=colour)
                    else:
                        break
                else:
                    break

    def switchPlayer(self) -> None:
        """
        Switches the current player with opponent.
        :return: 
            - None
        """
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

    def winChecker(self, move: tuple) -> int:
        """
        Checks the connections with move for a win, draw or nothing and updates match status.
        :param move: tuple[int, int]
        :return: 
            - result - int
        """
        draw, win = True, False
        
        directions, counts = self.getPieceSlices(move)
        for direction_pair in counts:
            if sum(counts[direction_pair]) >= self.LENGTH - 1:
                self.showWin(move, directions[direction_pair], GREEN)
                win = True
        if win:
            self.match = False
            return self.current_player

        for row in self.board:
            for piece in row:
                if piece.colour == self.EMPTY:
                    draw = False

        if draw:
            self.match = False
            return 0
        return -1

    def main(self, possible_move: int) -> int:
        """
        Checks for possible moves, makes the move, checks board status and then
        switches player turn.
        :param possible_move: int
        :return:
            - result - int
        """
        move = self.getPossibleMove(possible_move)
        if move[0] != self.INVALID_MOVE:
            self.makeMove(move)
            result = self.winChecker(move)
            if self.match:
                self.switchPlayer()
            return result
        return self.INVALID_MOVE
