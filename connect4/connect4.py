from __future__ import annotations

from math import inf


__version__ = '1.5.6'
__date__ = '29/04/2022'


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

    def __init__(self):
        """
        Initiates the object with required values.
        :param game_dims: tuple[int | float, int | float]
        :param kwargs: Any
        """
        self.current_player = 0
        self.opponent = abs(self.current_player - 1)
        self.match = True
        self.turn = 0

        self.active = True

        self.board = [[self.EMPTY for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def reset(self, switch: bool = True) -> None:
        """
        Resets attributes in preparation for next match.
        :param switch: bool
        :return:
            - None
        """
        if switch:  # defaulted so loser or opponent can go first
            self.switchPlayer()
        self.match = True
        self.turn = 0
        self.board = [[self.EMPTY for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def switchPlayer(self) -> None:
        """
        Switches the current player with opponent.
        :return:
            - None
        """
        self.current_player = self.opponent
        self.opponent = abs(self.current_player - 1)

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

    def getDirectionalSlices(self, move: tuple) -> dict:
        """
        Gets the piece slices surrounding the move.
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

    def getConnectionCounts(self, directions: dict, player: int = None, immediate_only: bool = True) -> dict:
        """
        Counts the surrounding connections using given directional slices.
        :param directions: dict[str: dict]
        :param player: int
        :param immediate_only: bool
        :return:
            - counts - dict[str: dict]
        """
        counts = {}
        player = player if player is not None else self.current_player
        for direction_pair in directions:
            counts[direction_pair] = []
            for direction in directions[direction_pair]:
                connection_count, count_connections = 0, True
                for piece_key in range(1, len(directions[direction_pair][direction])):
                    piece = directions[direction_pair][direction][piece_key]
                    if piece == player and count_connections:
                        connection_count += 1
                    else:
                        if piece != self.EMPTY or immediate_only:
                            count_connections = False
                counts[direction_pair].append(connection_count)
        return counts

    def getBoardStatus(self, move: tuple, player: int = None) -> int:
        """
        Checks the status of the board and return the result.
        :param move: tuple[int, int]
        :param player: int
        :return:
            - result - int
        """
        # Checks for a winning connection
        directions = self.getDirectionalSlices(move)
        connection_counts = self.getConnectionCounts(directions, player)
        for direction_pair in directions:
            if sum(connection_counts[direction_pair]) + 1 >= self.LENGTH:
                return self.WIN

        # Checks for an empty move
        for h in range(self.ROWS):
            for j in range(self.COLUMNS):
                if self.board[h][j] == self.EMPTY:
                    return self.EMPTY
        # Draw
        return self.DRAW

    def fitnessEvaluation(self, *args: Any, minimax: bool = False) -> int | dict:
        """
        Evaluates the fitness score using surrounding connections or the minimax algorithm.
        :param args: Any
        :param minimax: bool
        :return:
            - fitness - int | dict[tuple: int]
        """
        move = None if not args else args[0]
        raw_fitness = {}
        for i in range(self.COLUMNS):
            possible_move = self.getPossibleMove(i)
            if possible_move[0] != self.INVALID_MOVE:
                if minimax:
                    self.board[possible_move[0]][i] = self.current_player
                    score = self.minimax(possible_move, self.opponent, self.current_player, max_depth=4)
                    self.board[possible_move[0]][i] = self.EMPTY
                elif not minimax:
                    player_score, opponent_score = 0, 0
                    directions = self.getDirectionalSlices(possible_move)
                    player_counts = self.getConnectionCounts(directions, self.current_player, immediate_only=False)
                    opponent_counts = self.getConnectionCounts(directions, self.opponent, immediate_only=False)
                    for direction_pair in player_counts:
                        player_score = max(min(sum(player_counts[direction_pair]) + 1, self.LENGTH), player_score)
                        opponent_score = max(min(sum(opponent_counts[direction_pair]) + 1, self.LENGTH), opponent_score)
                    score = max(player_score + 0.5, opponent_score)
                else:
                    self.board[possible_move[0]][i] = self.current_player
                    score = self.getBoardStatus(possible_move)
                    self.board[possible_move[0]][i] = self.EMPTY
                if score not in raw_fitness:
                    raw_fitness[score] = []
                raw_fitness[score].append(possible_move)

        fitness = {}
        while raw_fitness:
            score = min(raw_fitness)
            for possible_move in raw_fitness[score]:
                fitness[possible_move] = (self.COLUMNS + 1 - len(raw_fitness))
            raw_fitness.pop(score)
        if len(args) == 1:
            return fitness[move]
        return fitness

    def minimax(self, move: tuple, maxi_piece: int, mini_piece: int, depth: int = 0, maximizing: bool = True,
                alpha: int = -inf, beta: int = inf, max_depth: int = None):
        """
        Minimax is a search algorithm that finds a score of minimal possible loss
        for the worst case scenario.
        :param move: tuple[int, int]
        :param maxi_piece: int
        :param mini_piece: int
        :param depth: int
        :param maximizing: bool
        :param alpha: int
        :param beta: int
        :param max_depth: int
        :return:
            - score - int
        """
        result = self.getBoardStatus(move, maxi_piece)
        score = None
        if result == self.WIN:
            score = 1 if maximizing else -1
        elif result == self.DRAW:
            score = 0
        if score is not None:
            return score

        if maximizing:
            best_score = -inf
            if max_depth is None or depth < max_depth:
                for i in range(self.COLUMNS):
                    possible_move = self.getPossibleMove(i)
                    if possible_move[0] != self.INVALID_MOVE:
                        self.board[possible_move[0]][i] = maxi_piece
                        score = self.minimax(possible_move, mini_piece, maxi_piece, depth + 1, not maximizing, alpha, beta, max_depth)
                        self.board[possible_move[0]][i] = self.EMPTY
                        best_score = max(best_score, score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
        else:
            best_score = inf
            if max_depth is None or depth < max_depth:
                for i in range(self.COLUMNS):
                    possible_move = self.getPossibleMove(i)
                    if possible_move[0] != self.INVALID_MOVE:
                        self.board[possible_move[0]][i] = mini_piece
                        score = self.minimax(possible_move, mini_piece, maxi_piece, depth + 1, not maximizing, alpha, beta, max_depth)
                        self.board[possible_move[0]][i] = self.EMPTY
                        best_score = min(best_score, score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
        return best_score

    def main(self, move: tuple) -> int | None:
        """
        Adds the move to board and switches the players turn or concludes
        match depending on board status results.
        :param move: tuple[int, int]
        :return:
            - result - int | None
        """
        if self.match and self.active:
            self.board[move[0]][move[1]] = self.current_player
            self.turn += 1
            result = self.getBoardStatus(move)
            if result == self.EMPTY:
                self.switchPlayer()
            else:
                self.match = False
            return result
