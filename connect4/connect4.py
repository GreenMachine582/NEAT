from __future__ import annotations

from .visualize import GameBoard
import mattslib.pygame as mlpg

__version__ = '1.4.4'
__date__ = '6/04/2022'


class Connect4:
    """
    Connect 4 is a 2 player game where the piece colours are red and yellow. This
    object handles all related features of a normal connect 4 game.
    """

    ROWS, COLUMNS = 6, 7
    LENGTH = 4
    MAX_PLAYERS = 2
    PLAYERS = ['Red', 'Yellow']
    INVALID_MOVE, EMPTY, DRAW, WIN = -2, -1, 0, 1

    def __init__(self, game_dims: tuple = None, **kwargs: Any):
        """
        Initiates the object with required values.
        :param game_dims: tuple[int | float, int | float]
        :param kwargs: Any
        """
        self.current_player = 0
        self.opponent = abs(self.current_player - 1)
        self.match = True
        self.turn = 0
        self.result = self.EMPTY

        self.active = True
        self.visible = False

        self.board = [[self.EMPTY for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        self.game_board = None

        if 'kwargs' in kwargs:
            kwargs = kwargs['kwargs']

        if game_dims is not None:
            self.visible = True
            self.game_board = GameBoard(game_dims, self.ROWS, self.COLUMNS, kwargs=kwargs)

    def reset(self) -> None:
        """
        Resets key connect4 attributes for next match.
        :return:
            - None
        """
        self.switchPlayer()
        self.match = True
        self.turn = 0
        self.result = self.EMPTY

        self.board = [[self.EMPTY for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

        if self.visible:
            self.game_board.update(reset=True)

    def makeMove(self, move: tuple) -> None:
        """
        Receives the move to update the game board and increments turn.
        :param move: tuple[int, int]
        :return:
            - None
        """
        self.board[move[0]][move[1]] = self.current_player
        if self.visible:
            self.game_board.update(move=move, player=self.current_player)
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
            if self.board[row][possible_move] != self.EMPTY:
                break
            move = row
        return move, possible_move

    def showWin(self, move: tuple, direction_pair: list, colour: list = mlpg.GREEN) -> None:
        """
        Shows the connections made with move that result in a win.
        :param move: tuple[int, int]
        :param direction_pair: list[tuple[int, int]]
        :param colour: list[int]
        :return:
            - None
        """
        self.game_board.update(move=move, highlight_colour=colour)
        for direction in direction_pair:
            for n in range(1, self.LENGTH):
                a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                    if self.board[a][b] == self.current_player:
                        self.game_board.update(move=(a, b), highlight_colour=colour)
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

    def getPieceSlices(self, move: tuple) -> dict:
        """
        Gets the piece slices around the move and counts connecting pieces.
        :param move: tuple[int, int]
        :return:
            - directions - dict[str: dict[tuple[int, int]: list[int]]]
        """
        directions = {'vertical': {(1, 0): [], (-1, 0): []},
                      'horizontal': {(0, 1): [], (0, -1): []},
                      'diagonal1': {(-1, 1): [], (1, -1): []},
                      'diagonal2': {(1, 1): [], (-1, -1): []}}
        for direction_pair in directions:
            search_length = self.ROWS if direction_pair != 'horizontal' else self.COLUMNS
            for direction in directions[direction_pair]:
                if directions[direction_pair][direction] is not None:
                    directions[direction_pair][direction].append(self.board[move[0]][move[1]])
                    for n in range(1, search_length):
                        a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                        if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                            directions[direction_pair][direction].append(self.board[a][b])
                        else:
                            break
        return directions

    def getConnectionCounts(self, directions, player: int = None):
        counts = {}
        if player is None:
            player = self.current_player
        for direction_pair in directions:
            counts[direction_pair] = []
            for direction in directions[direction_pair]:
                connection_count = 0
                count_connections = True
                for piece_key in range(1, len(directions[direction_pair][direction])):
                    if directions[direction_pair][direction][piece_key] == player and count_connections:
                        connection_count += 1
                    else:
                        count_connections = False
                counts[direction_pair].append(connection_count)
        return counts

    def winChecker(self, move: tuple) -> None:
        """
        Checks the connections with move for a win, draw or nothing and updates match status.
        :param move: tuple[int, int]
        :return:
            - None
        """
        win = False

        directions = self.getPieceSlices(move)
        connection_counts = self.getConnectionCounts(directions)
        for direction_pair in directions:
            if sum(connection_counts[direction_pair]) + 1 >= self.LENGTH:
                if self.visible:
                    self.showWin(move, directions[direction_pair])
                win = True
        if win:
            self.match = False
            self.result = self.WIN
            return

        for h in range(self.ROWS):
            for j in range(self.COLUMNS):
                if self.board[h][j] == self.EMPTY:
                    self.result = self.EMPTY
                    return

        self.match = False
        self.result = self.DRAW

    def fitnessEvaluation(self) -> tuple:
        """
        Calculates the fitness score using match results.
        :return:
            - fitness - tuple[int, int]
        """
        min_required_moves = (2 * self.LENGTH) - 1
        winner = max(0, (self.ROWS * self.COLUMNS) - self.turn - min_required_moves)
        loser = max(0, self.turn - min_required_moves)
        return winner, loser

    def draw(self, surface: Any) -> None:
        """
        Draws the game board and pieces to the surface.
        :param surface: Any
        :return:
            - None
        """
        if self.visible:
            self.game_board.update(text=f"{self.PLAYERS[self.current_player]}'s turn!")
            self.game_board.draw(surface)

    def main(self, possible_move: int) -> None:
        """
        Checks for possible moves, makes the move, checks board status and then
        switches player turn.
        :param possible_move: int
        :return:
            - None
        """
        if self.active:
            move = self.getPossibleMove(possible_move)
            if move[0] != self.INVALID_MOVE:
                self.makeMove(move)
                self.winChecker(move)
                if self.match:
                    self.switchPlayer()
