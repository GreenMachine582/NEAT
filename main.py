from __future__ import annotations

import os
import pygame as pg
import random

from connect4 import Connect4
from neat import NEAT

import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.4.6'
__date__ = '26/03/2022'

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_PANEL = (HEIGHT, HEIGHT)
ADDON_PANEL = (WIDTH - GAME_PANEL[0], HEIGHT)
NETWORK_WIDTH, NETWORK_HEIGHT = ADDON_PANEL[0], ADDON_PANEL[1] * (1 / 2)
INFO_WIDTH, INFO_HEIGHT = ADDON_PANEL[0], 80
MENU_WIDTH, MENU_HEIGHT = ADDON_PANEL[0], NETWORK_HEIGHT - INFO_HEIGHT
OPTION_WIDTH, OPTION_HEIGHT = WIDTH, HEIGHT

FPS = 40
display = True

GAME = 'connect4'
PLAYER_TYPES = ['Human', 'NEAT', '1', '1000', '6000']
SHOW_EVERY = ['Genome', 'Generation', 'None']
SPEEDS = [1, 5, 25, 100, 500]
DIRECTORY = os.path.dirname(os.path.realpath(__file__))


# Globals - Defaults
players = {1: PLAYER_TYPES[1], 2: PLAYER_TYPES[1]}
neats = {1: None, 2: None}
game_speed = SPEEDS[-1]
evolution_speed = SPEEDS[-1]
show_every = SHOW_EVERY[1]
max_fps = max(FPS, max(game_speed, evolution_speed))

# Globals - Pygame
if display:
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"
    pg.init()
    display = pg.display.set_mode((WIDTH, HEIGHT), depth=32)

    pg.display.set_caption("Connect 4 with NEAT - v" + __version__)
    game_display = pg.Surface(GAME_PANEL)
    network_display = pg.Surface((NETWORK_WIDTH, NETWORK_HEIGHT))
    info_display = pg.Surface((INFO_WIDTH, INFO_HEIGHT))
    menu_display = pg.Surface((MENU_WIDTH, MENU_HEIGHT))
    options_display = pg.Surface((OPTION_WIDTH, OPTION_HEIGHT))
    display.fill(mlpg.BLACK)
    clock = pg.time.Clock()

connect4 = Connect4(GAME_PANEL)
network = None
info = None
menu = None
options = None


def calculateFitness(win: bool) -> int:
    """
    Calculates the fitness with match results.
    :param win: bool
    :return:
        - fitness - int
    """
    fitness = (connect4.ROWS * connect4.COLUMNS) - connect4.turn
    if connect4.result in list(players.keys()):
        fitness = fitness + 50 if win else 0
    return fitness


def getSpeedShow(current_player: int) -> tuple:
    """
    Returns that speed and show values depending on neat details.
    :param current_player: int
    :return:
        - speed, show - tuple[int, bool]
    """
    if players[current_player] != PLAYER_TYPES[0]:
        if show_every == 'Generation':
            for player_id in [current_player, connect4.player_ids[connect4.opponent]]:
                if neats[player_id] is not None:
                    if neats[player_id].current_species == 0 and neats[player_id].current_genome == 0:
                        return game_speed, True
            return evolution_speed, False
        elif show_every == 'None':
            return evolution_speed, False
    return game_speed, True


def setupAi(player_id: int, inputs: int = 4, outputs: int = 1, population: int = 100) -> NEAT:
    """
    Sets up neat with game settings in mind.
    :rtype: object
    :param player_id: int
    :param inputs: int
    :param outputs: int
    :param population: int
    :return:
        - neat - NEAT
    """
    if players[player_id] == PLAYER_TYPES[1]:
        if os.path.isfile(f"{DIRECTORY}\\{GAME}\\ai_{player_id}.neat"):
            neat = NEAT.load(f"ai_{player_id}", f"{DIRECTORY}\\{GAME}")
            return neat
    else:
        if os.path.isfile(f"{DIRECTORY}\\{GAME}\\ai_{player_id}_gen_{players[player_id]}.neat"):
            neat = NEAT.load(f"ai_{player_id}_gen_{players[player_id]}", f"{DIRECTORY}\\{GAME}")
            return neat
    neat = NEAT(DIRECTORY, f"\\{GAME}")
    neat.generate(inputs, outputs, population=population)
    return neat


def neatMove(genome: Genome) -> int:
    """
    Calculates the best move for the current genome to make.
    :param genome: Genome
    :return:
        - move - int
    """
    possible_moves = {}
    for i in range(connect4.COLUMNS):
        possible_move = connect4.getPossibleMove(i)
        if possible_move[0] != connect4.INVALID_MOVE:
            possible_moves[possible_move] = 0
    for possible_move in possible_moves:
        directions, _ = connect4.getPieceSlices(possible_move)
        for direction_pair in directions:
            for direction in directions[direction_pair]:
                if directions[direction_pair][direction] is not None:
                    inputs = directions[direction_pair][direction]
                    possible_moves[possible_move] += sum(genome.forward(inputs))
    sorted_moves = ml.dict.combineByValues(possible_moves)
    max_min_keys = ml.list.findMaxMin(list(sorted_moves.keys()))
    move = random.choice(sorted_moves[max_min_keys['max']['value']])
    return move[1]


def setup() -> None:
    """
    Sets up the global variables and neat players.
    :return:
        - None
    """
    global connect4, network, info, menu, options, players, neats
    connect4 = Connect4(GAME_PANEL)
    network = Network()
    info = Info()
    options = Options()
    menu = Menu()
    for player_id in players:
        neats[player_id] = None
        if players[player_id] != PLAYER_TYPES[0]:
            neats[player_id] = setupAi(player_id)


def close() -> None:
    """
    Closes and quits pygame and python.
    :return:
        - None
    """
    for player_id in players:
        if players[player_id] == PLAYER_TYPES[1]:
            neats[player_id].save(f"\\ai_{player_id}")
    pg.quit()
    quit()


class Network:
    """
    Creates and draws the visual of the current genome in a neural network form.
    """

    BOARDER = 40
    SPACING = 1

    def __init__(self):
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
            width = NETWORK_WIDTH - (2 * self.BOARDER)
        if height is None:
            height = NETWORK_HEIGHT - (2 * self.BOARDER)

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

    def __init__(self):
        self.active = True
        self.visible = True
        self.colour = {'background': [200, 200, 200]}

        self.header = {}

        self.header = {'generation': mlpg.Message("Generation:", (self.BOARDER, self.BOARDER), align='ml'),
                       'specie': mlpg.Message("Species:", (self.BOARDER, INFO_HEIGHT - self.BOARDER), align='ml'),
                       'genome': mlpg.Message(":Genome", (INFO_WIDTH - self.BOARDER, self.BOARDER), align='mr'),
                       'fitness': mlpg.Message(":Fitness", (INFO_WIDTH - self.BOARDER, INFO_HEIGHT - self.BOARDER),
                                               align='mr')}
        self.data = {'generation': mlpg.Message(0, (150, self.BOARDER), align='ml'),
                     'species': mlpg.Message(0, (150, INFO_HEIGHT - self.BOARDER), align='ml'),
                     'genome': mlpg.Message(0, (360, self.BOARDER), align='mr'),
                     'fitness': mlpg.Message(0, (360, INFO_HEIGHT - self.BOARDER), align='mr')}

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


class Menu:
    """
    Menu is a class that allows buttons to be accessed during the main loop and handles the assigned action.
    """

    BOARDER = 30

    def __init__(self):
        self.colour = {'background': mlpg.WHITE}

        self.buttons = [
            mlpg.Button("Reset", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (1 / 3)), mlpg.GREY, handler=connect4.reset),
            mlpg.Button("Options", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (1 / 3)), mlpg.GREY, handler=options.main),
            mlpg.Button("Switch", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (2 / 3)), mlpg.GREY,
                        handler=connect4.switchPlayer),
            mlpg.Button("QUIT", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (2 / 3)), mlpg.GREY, handler=close)]

        self.update()

    def update(self, *args: Any) -> None:
        """
        Updates the menu buttons and passes environment information.
        :param args: Any
        :return:
            - None
        """
        if len(args) == 2:
            for button in self.buttons:
                button.update(args[0], args[1], origin=(GAME_PANEL[0], ADDON_PANEL[1] - MENU_HEIGHT))

    def draw(self, surface: Any) -> None:
        """
        Draws the background and buttons to the given surface.
        :param surface: Any
        :return:
            - None
        """
        surface.fill(self.colour['background'])
        for button in self.buttons:
            button.draw(surface)


class Options:
    """
    Options handles changing the global variables like a settings menu.
    """
    BOARDER = 60

    def __init__(self):
        self.colour = {'background': mlpg.WHITE}

        self.players = {}
        self.buttons = {}
        self.group_buttons = {}
        self.messages = []

        self.generate()

    def generate(self) -> None:
        """
        Generates the options messages and buttons with default and global values.
        :return:
            - None
        """
        self.buttons = {'back': mlpg.Button("Back", (OPTION_WIDTH * (2 / 5), OPTION_HEIGHT * (5 / 6)),
                                            mlpg.GREY, handler=True),
                        'quit': mlpg.Button("QUIT", (OPTION_WIDTH * (3 / 5), OPTION_HEIGHT * (5 / 6)),
                                            mlpg.GREY, handler=close)}
        self.messages = []

        gbi = {'Player 1:': {'selected': players[1], 'options': PLAYER_TYPES},
               'Player 2:': {'selected': players[2], 'options': PLAYER_TYPES},
               'Game Speed:': {'selected': game_speed, 'options': SPEEDS},
               'Evolution Speed:': {'selected': evolution_speed, 'options': SPEEDS},
               'Show Every:': {'selected': show_every, 'options': SHOW_EVERY}}
        for group_key in gbi:
            button_states = [True if option == gbi[group_key]['selected'] else False
                             for option in gbi[group_key]['options']]
            self.group_buttons[group_key] = mlpg.ButtonGroup(gbi[group_key]['options'],
                                                             (self.BOARDER + (OPTION_WIDTH * (1 / 6) + 100),
                                                              self.BOARDER + (len(self.messages) * 90)),
                                                             mlpg.GREY, mlpg.GREEN, button_states=button_states)
            self.messages.append(mlpg.Message(group_key, (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                                          self.BOARDER + (len(self.messages) * 90)), align='mr'))

    def update(self, mouse_pos: tuple, mouse_clicked: bool) -> bool:
        """
        Updates the option buttons, global variables and other related attributes.
        :param mouse_pos: tuple[int, int]
        :param mouse_clicked: bool
        :return:
            - continue - bool
        """
        global players, game_speed, evolution_speed, max_fps, show_every
        self.generate()
        for button_key in self.buttons:
            action = self.buttons[button_key].update(mouse_pos, mouse_clicked)
            if action is not None:
                return True

        if players[1] != PLAYER_TYPES[1] or players[2] != PLAYER_TYPES[1]:
            evolution_speed = SPEEDS[0]
            show_every = SHOW_EVERY[0]
            self.group_buttons['Evolution Speed:'].update(active=False)
            self.group_buttons['Show Every:'].update(active=False)
        else:
            if game_speed > evolution_speed:
                evolution_speed = game_speed
            self.group_buttons['Evolution Speed:'].update(active=True)
            self.group_buttons['Show Every:'].update(active=True)

        for group in self.group_buttons:
            button_key = self.group_buttons[group].update(mouse_pos, mouse_clicked)
            if button_key is not None and self.group_buttons[group].active:
                if group in ['Player 1:', 'Player 2:']:
                    if button_key == 0:
                        game_speed = SPEEDS[0]
                        show_every = SHOW_EVERY[0]
                    players[int(group[-2])] = PLAYER_TYPES[button_key]
                    if button_key != 1:
                        game_speed = SPEEDS[0]
                        show_every = SHOW_EVERY[0]
                    setup()
                elif group == 'Game Speed:':
                    game_speed = SPEEDS[button_key]
                elif group == 'Evolution Speed:':
                    evolution_speed = SPEEDS[button_key] if game_speed <= SPEEDS[button_key] else game_speed
                elif group == 'Show Every:':
                    show_every = SHOW_EVERY[0]
                    if players[1] == players[2] == PLAYER_TYPES[1]:
                        show_every = SHOW_EVERY[button_key]

                max_fps = max(FPS, max(game_speed, evolution_speed))

    def draw(self, surface: Any) -> None:
        """
        Draws the option buttons and texts to the surface.
        :param surface: Any
            - None
        :return:
        """
        surface.fill(self.colour['background'])
        for message in self.messages:
            message.draw(surface)
        for group in self.group_buttons:
            self.group_buttons[group].draw(surface)
        for button_keys in self.buttons:
            self.buttons[button_keys].draw(surface)

    def main(self) -> bool:
        """
        Main is the main loop for the options state and will display, update and check
        collisions with objects.
        :return:
            - continue - bool
        """
        global display, options_display
        run, typing = True, False
        while run:
            mouse_clicked = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    close()
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        close()
                    if typing:
                        if event.key in [pg.K_1, pg.K_KP1]:
                            pass
            mouse_pos = pg.mouse.get_pos()
            if self.update(mouse_pos, mouse_clicked) is not None:
                return True

            self.draw(options_display)
            display.blit(options_display, (0, 0))

            pg.display.update()
            clock.tick(FPS)


def main() -> None:
    """
    Main is the main loop for the project and will display, update and check
    collisions with objects.
    :return:
        - None
    """
    global display, connect4, network, info, menu, options

    setup()

    frame_count, speed, show = 1, game_speed, True
    run = True
    while run:
        current_player = connect4.player_ids[connect4.current_player]
        speed, show = getSpeedShow(current_player)

        possible_move = None
        mouse_clicked = False
        if display:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    close()
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        close()
                    if connect4.match and players[current_player] == PLAYER_TYPES[0]:
                        if event.key in [pg.K_1, pg.K_KP1]:
                            possible_move = 0
                        elif event.key in [pg.K_2, pg.K_KP2]:
                            possible_move = 1
                        elif event.key in [pg.K_3, pg.K_KP3]:
                            possible_move = 2
                        elif event.key in [pg.K_4, pg.K_KP4]:
                            possible_move = 3
                        elif event.key in [pg.K_5, pg.K_KP5]:
                            possible_move = 4
                        elif event.key in [pg.K_6, pg.K_KP6]:
                            possible_move = 5
                        elif event.key in [pg.K_7, pg.K_KP7]:
                            possible_move = 6
                if possible_move is not None:
                    break

            mouse_pos = pg.mouse.get_pos()
            menu.update(mouse_pos, mouse_clicked)

        if connect4.match:
            if players[current_player] != PLAYER_TYPES[0]:
                if frame_count >= max_fps / speed:
                    frame_count = 1

                    if players[current_player] == PLAYER_TYPES[1] and neats[current_player].shouldEvolve():
                        current_genome = neats[current_player].getGenome()
                    else:
                        current_genome = neats[current_player].best_genome

                    possible_move = neatMove(current_genome)
                    connect4.main(possible_move)

                    if show and display:
                        network.generate(current_genome)
                        info.update(neats[current_player].getInfo())

            elif players[current_player] == PLAYER_TYPES[0]:
                if possible_move is not None:
                    connect4.main(possible_move)
                    if not connect4.match:
                        frame_count = 1

        if not connect4.match:
            if frame_count >= max_fps / speed:
                if players[current_player] == PLAYER_TYPES[1] and neats[current_player].shouldEvolve():
                    gen = f"Generation:"
                    for i, player_key in enumerate([current_player, connect4.player_ids[connect4.opponent]]):
                        current_genome = neats[player_key].getGenome()
                        current_genome.fitness = calculateFitness(bool(i))
                        neats[player_key].nextGenome(f"ai_{player_key}")
                        gen += f" {player_key} - {neats[player_key].generation}"
                    if show:
                        print(gen)
                connect4.reset()

        if display:
            menu.draw(menu_display)
            display.blit(menu_display, (GAME_PANEL[0], GAME_PANEL[1] - MENU_HEIGHT))

            if show or players[current_player] == PLAYER_TYPES[0]:
                connect4.draw(game_display)
                network.draw(network_display)
                info.draw(info_display)

            display.blit(game_display, (0, 0))
            display.blit(network_display, (GAME_PANEL[0], 0))
            display.blit(info_display, (GAME_PANEL[0], NETWORK_HEIGHT))

            pg.display.update()
            clock.tick(max_fps)
            frame_count += 1

    close()


if __name__ == '__main__':
    main()
