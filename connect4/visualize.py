from __future__ import annotations

import pygame as pg

import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.1.1'
__date__ = '29/03/2022'


class GameBoard:
    BOARDER = 10

    def __init__(self, game_dims, rows, columns):
        self.game_width = game_dims[0]
        self.game_height = game_dims[1]
        self.rows = rows
        self.columns = columns

        self.active = True
        self.visible = True
        self.colour = {'background': mlpg.BLUE, -1: mlpg.WHITE, 0: mlpg.RED, 1: mlpg.YELLOW}

        self.board_background = mlpg.Rect((self.game_width / 2, self.game_height / 2), self.colour['background'],
                                          [self.game_width - (self.BOARDER * 2), self.game_height - (self.BOARDER * 2)])
        self.player_text = mlpg.Message('', (self.game_width / 2, 60), size=40)

        self.game_board = [[Piece((h, j), self.rows, self.columns, self.colour[-1], self.game_height)
                            for j in range(self.columns)] for h in range(self.rows)]

        self.column_labels = [mlpg.Message(i + 1, (self.game_board[0][i].pos[0] + self.game_board[0][i].radius,
                                                   (self.game_height - 35)), size=30)
                              for i in range(self.columns)]

    def update(self, **kwargs):
        if 'text' in kwargs:
            self.player_text.update(text=kwargs['text'])
        if 'reset' in kwargs and kwargs['reset']:
            for h in range(self.rows):
                for j in range(self.columns):
                    self.game_board[h][j].update(colour=self.colour[-1])
        if 'move' in kwargs:
            move = kwargs['move']
            if 'player' in kwargs:
                self.game_board[move[0]][move[1]].update(colour=self.colour[kwargs['player']])
            if 'highlight_colour' in kwargs:
                self.game_board[move[0]][move[1]].update(highlight_colour=kwargs['highlight_colour'])

    def draw(self, surface: Any) -> None:
        """
        Draws the game board and pieces to the surface.
        :param surface: Any
        :return:
            - None
        """
        surface.fill(mlpg.changeColour(self.colour['background'], -70))
        self.board_background.draw(surface)
        self.player_text.draw(surface)
        for row in self.game_board:
            for piece in row:
                piece.draw(surface)
        for label in self.column_labels:
            label.draw(surface)


class Piece:
    """
    Piece is a players coloured move on the game board.
    """

    BOARDER = 38
    TOP_PADDING = 60
    SPACING = 10

    def __init__(self, coordinates: tuple, rows: int, cols: int, colour: list, game_height: int | float):
        """
        Initiates the object with required values.
        :param coordinates: tuple[int, int]
        :param rows: int
        :param cols: int
        :param height: int | float
        """
        self.coordinates = coordinates
        self.radius = 30

        self.active = True
        self.show = True
        self.colour = colour

        self.radius = (((game_height - self.BOARDER * 2) / max(rows, cols)) - self.SPACING) / 2
        self.pos = (self.BOARDER + (self.coordinates[1] * (self.radius * 2 + self.SPACING)),
                    self.BOARDER + self.TOP_PADDING + (self.coordinates[0] * (self.radius * 2 + self.SPACING)))

        self.circle = mlpg.shape.Circle(self.pos, self.colour, self.radius, 'tl')
        self.circle_boarder = mlpg.shape.Circle(self.pos, mlpg.changeColour(self.colour, -70), self.radius, 'tl')

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


class Network:
    """
    Creates and draws the visual of the current genome in a neural network form.
    """

    BOARDER = 40
    SPACING = 1

    def __init__(self, network_dims):
        self.network_width = network_dims[0]
        self.network_height = network_dims[1]

        self.active = True
        self.visible = True
        self.colour = {'background': mlpg.WHITE,
                       'input': mlpg.BLUE, 'output': mlpg.RED, 'hidden': mlpg.BLACK,
                       'active': mlpg.GREEN, 'deactivated': mlpg.RED}
        self.network = {}
        self.radius = 5

    def generate(self, current_genome: Genome, width: int | float = None, height: int | float = None) -> None:
        """
        Creates the neural network visual of the current genome.
        :param current_genome:
        :param width:
        :param height:
        :return:
        """
        if width is None:
            width = self.network_width - (2 * self.BOARDER)
        if height is None:
            height = self.network_height - (2 * self.BOARDER)

        self.network = {}
        node_depths = current_genome.getNodesByDepth()
        node_depths = ml.dict.removeKeys(node_depths)
        connections = current_genome.connections

        for d, depth in enumerate(node_depths):
            nodes_in_depth = len(node_depths[depth])
            for i, node_index in enumerate(node_depths[depth]):
                node_type = current_genome.nodes[node_index].layer_type
                pos = (int(self.BOARDER + width * (d / (len(node_depths) - 1))),
                       int(self.BOARDER + height * ((1/2) if nodes_in_depth <= 1 else (i / (nodes_in_depth - 1)))))
                self.network[node_index] = {'pos': pos, 'colour': self.colour[node_type], 'connections': []}

        for pos in connections:
            colour = self.colour['active'] if connections[pos].active else self.colour['deactivated']
            connection = {'start': self.network[pos[0]]['pos'], 'end': self.network[pos[1]]['pos'], 'colour': colour,
                          'thickness': int(max(3, min(abs(connections[pos].weight), 1)))}
            self.network[pos[0]]['connections'].append(connection)

    def draw(self, surface: Any) -> None:
        """
        Draws the neural network of the current genome.
        :param surface: Any
        :return:
            - None
        """
        surface.fill(self.colour['background'])
        for node in self.network:
            for connection in self.network[node]['connections']:
                pg.draw.line(surface, connection['colour'], connection['start'], connection['end'],
                             connection['thickness'])
        for node in self.network:
            pg.draw.circle(surface, self.network[node]['colour'], self.network[node]['pos'], self.radius)


class Info:
    """
    Info is a class that handles updating and drawing the neat information.
    """
    BOARDER = 20

    def __init__(self, info_dims):
        self.info_width = info_dims[0]
        self.info_height = info_dims[1]
        self.active = True
        self.visible = True
        self.colour = {'background': [200, 200, 200]}

        self.header = {}

        self.header = {'generation': mlpg.Message("Generation:", (self.BOARDER, self.BOARDER), align='ml'),
                       'specie': mlpg.Message("Species:", (self.BOARDER, self.info_height - self.BOARDER), align='ml'),
                       'genome': mlpg.Message(":Genome", (self.info_width - self.BOARDER, self.BOARDER), align='mr'),
                       'fitness': mlpg.Message(":Fitness", (self.info_width - self.BOARDER,
                                                            self.info_height - self.BOARDER), align='mr')}
        self.data = {'generation': mlpg.Message(0, (150, self.BOARDER), align='ml'),
                     'species': mlpg.Message(0, (150, self.info_height - self.BOARDER), align='ml'),
                     'genome': mlpg.Message(0, (360, self.BOARDER), align='mr'),
                     'fitness': mlpg.Message(0, (360, self.info_height - self.BOARDER), align='mr')}

    def update(self, neat_info: dict) -> None:
        """
        Updates the data texts with neat information.
        :param neat_info: dict[str: int]
        :return:
            - None
        """
        if self.active:
            self.data['generation'].update(text=neat_info['generation'])
            self.data['species'].update(text=neat_info['current_species'])
            self.data['genome'].update(text=neat_info['current_genome'])
            self.data['fitness'].update(text=neat_info['fitness'])

    def draw(self, surface: Any) -> None:
        """
        Draws the background and neat information to the given surface.
        :param surface: Any
        :return:
            - None
        """
        if self.visible:
            surface.fill(self.colour['background'])
            for text_key in self.header:
                self.header[text_key].draw(surface)

            for text_key in self.data:
                self.data[text_key].draw(surface)
