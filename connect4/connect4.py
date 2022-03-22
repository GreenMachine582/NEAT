from __future__ import annotations

import mattslib.pygame as mlpg

__version__ = '1.5.1'
__date__ = '22/03/2022'

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_WIDTH, GAME_HEIGHT = HEIGHT, HEIGHT


class Piece:
    """
    Piece is a players coloured move on the game board.
    """

    BOARDER = 38
    TOP_PADDING = 80
    SPACING = 10

    def __init__(self, coordinates: tuple, rows: int, cols: int, colour: list):
        """
        Initiates the object with required values.
        :param coordinates: tuple[int, int]
        :param rows: int
        :param cols: int
        :param colour: list[int]
        """
        self.coordinates = coordinates
        self.radius = 30

        self.active = True
        self.show = True
        self.colour = colour

        self.radius = (((GAME_HEIGHT - self.BOARDER * 2) / max(rows, cols)) - self.SPACING) / 2
        self.pos = (self.BOARDER + (self.coordinates[1] * (self.radius * 2 + self.SPACING)),
                    self.BOARDER + self.TOP_PADDING + (self.coordinates[0] * (self.radius * 2 + self.SPACING)))

        self.circle = mlpg.shape.Circle(self.pos, self.colour, self.radius, 'tl')
        self.circle_boarder = mlpg.shape.Circle(self.pos, mlpg.changeColour(colour, -70), self.radius, 'tl')

        self.update()

    def update(self, **kwargs: Any) -> None:
        """
        Updates relevant attributes.
        :param kwargs: Any
        :return:
            - None
        """
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
            self.circle.update(colour=self.colour)
            self.circle_boarder.update(colour=mlpg.changeColour(self.colour, -70))
        if 'highlight_colour' in kwargs:
            self.circle_boarder.update(colour=mlpg.changeColour(kwargs['highlight_colour'], -70))
        if 'active' in kwargs:
            self.active = kwargs['active']
        if 'show' in kwargs:
            self.show = kwargs['show']

    def draw(self, surface: Any, width: int = 5) -> None:
        """
        Draws the piece to the given game board.
        :param surface: Any
        :param width: int
        :return:
            - None
        """
        if self.show:
            self.circle.draw(surface)
            self.circle_boarder.draw(surface, width)


class Connect4:
    """
    Connect 4 is a 2 player game where the piece colours are red and yellow. This
    object handles all related features of a normal connect 4 game.
    """

    ROWS, COLUMNS = 6, 7
    PLAYERS = {0: 'Red', 1: "Yellow"}
    COLOURS = {0: mlpg.RED, 1: mlpg.YELLOW}
    EMPTY = mlpg.WHITE
    INVALID_MOVE = -2
    LENGTH = 4
    GAME_STATES = {-2: 'Invalid move', -1: '', 0: 'Draw', 1: 'Player 1 Wins', 2: 'Player 2 Wins'}
    BOARDER = 10

    def __init__(self):
        self.board = []
        self.active = True
        self.visible = True
        self.colour = {'background': mlpg.BLUE}

        self.current_player = 0
        self.opponent = abs(self.current_player - 1)
        self.match = True
        self.turn = 0
        self.result = -1

        self.player_ids = [1, 2]

        self.board_background = mlpg.Rect((GAME_WIDTH / 2, GAME_HEIGHT / 2), self.colour['background'],
                                          [GAME_WIDTH - (self.BOARDER * 2), GAME_HEIGHT - (self.BOARDER * 2)])
        self.player_text = mlpg.Message(f"Player {self.player_ids[self.current_player]} - {self.PLAYERS[self.current_player]}'s turn!",
                                        (GAME_WIDTH / 2, 60), size=40)

        self.board = [[Piece((h, j), self.ROWS, self.COLUMNS, self.EMPTY) for j in range(self.COLUMNS)]
                      for h in range(self.ROWS)]

    def reset(self) -> None:
        """
        Resets specific connect4 attributes for next match.
        :return:
            - None
        """
        for h in range(self.ROWS):
            for j in range(self.COLUMNS):
                self.board[h][j].update(colour=self.EMPTY)
        self.match = True
        self.turn = 0
        self.current_player = 0
        self.opponent = abs(self.current_player - 1)
        self.result = -1
        self.player_ids = self.player_ids[::-1]

    def draw(self, surface: Any) -> None:
        """
        Draws the game board and pieces to the surface.
        :param surface: Any
        :return:
            - None
        """
        self.player_text.update(text=f"Player {self.player_ids[self.current_player]} - {self.PLAYERS[self.current_player]}'s turn!")

        surface.fill(mlpg.changeColour(self.colour['background'], -70))
        self.board_background.draw(surface)
        self.player_text.draw(surface)
        for row in self.board:
            for piece in row:
                piece.draw(surface)

    def makeMove(self, move: tuple) -> None:
        """
        Receives the move to update the game board and increments turn.
        :param move: tuple[int, int]
        :return:
            - None
        """
        self.board[move[0]][move[1]].update(colour=self.COLOURS[self.current_player])
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
            if self.board[row][possible_move].colour != self.EMPTY:
                break
            move = row
        return move, possible_move

    def showWin(self, move: tuple, direction_pair: list, colour: list) -> None:
        """
        Shows the connections made with move that result in a win.
        :param move: tuple[int, int]
        :param direction_pair: list[tuple[int, int]]
        :param colour: list[int]
        :return:
            - None
        """
        self.board[move[0]][move[1]].update(highlight_colour=colour)
        for direction in direction_pair:
            for n in range(1, self.LENGTH):
                a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                    piece = self.board[a][b]
                    if piece.colour == self.COLOURS[self.current_player]:
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
        self.current_player = self.opponent
        self.opponent = abs(self.current_player - 1)

    def getPieceSlices(self, move: tuple) -> tuple:
        """
        Gets the piece slices around the move and counts connecting pieces.
        :param move: tuple[int, int]
        :return:
            - directions, counts - tuple[dict[str: dict[tuple[int, int]: list[int]]], dict[tuple[int, int]: int]]
        """
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
                    directions[direction_pair][direction].append(self.player_ids[self.current_player])
                    for n in range(1, self.LENGTH):
                        a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                        if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                            piece = self.board[a][b]
                            if piece.colour == self.COLOURS[self.current_player]:
                                directions[direction_pair][direction].append(self.player_ids[self.current_player])
                                if count_connections:
                                    connection_count += 1
                            else:
                                count_connections = False
                                if piece.colour == self.COLOURS[self.opponent]:
                                    directions[direction_pair][direction].append(self.opponent)
                                elif piece.colour == self.EMPTY:
                                    directions[direction_pair][direction].append(0)
                        else:
                            directions[direction_pair][direction].append(-1)  # out of bounds

                counts[direction_pair].append(connection_count)
        return directions, counts

    def winChecker(self, move: tuple) -> None:
        """
        Checks the connections with move for a win, draw or nothing and updates match status.
        :param move: tuple[int, int]
        :return:
            - None
        """
        draw, win = True, False
        
        directions, counts = self.getPieceSlices(move)
        for direction_pair in counts:
            if sum(counts[direction_pair]) >= self.LENGTH - 1:
                self.showWin(move, directions[direction_pair], mlpg.GREEN)
                win = True
        if win:
            self.match = False
            self.result = self.player_ids[self.current_player]
            return

        for row in self.board:
            for piece in row:
                if piece.colour == self.EMPTY:
                    draw = False

        if draw:
            self.match = False
            self.result = 0
        else:
            self.result = -1

    def main(self, possible_move: int) -> None:
        """
        Checks for possible moves, makes the move, checks board status and then
        switches player turn.
        :param possible_move: int
        :return:
            - None
        """
        move = self.getPossibleMove(possible_move)
        if move[0] != self.INVALID_MOVE:
            self.makeMove(move)
            self.winChecker(move)
            if self.match:
                self.switchPlayer()
