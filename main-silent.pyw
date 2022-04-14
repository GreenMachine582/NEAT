from __future__ import annotations

import os
import sys
import time
import random

import pygame as pg

from connect4 import Connect4
from connect4 import visualize
from neat import NEAT

import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.5.8'
__date__ = '7/04/2022'

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_PANEL = (HEIGHT, HEIGHT)
ADDON_PANEL = (WIDTH - GAME_PANEL[0], HEIGHT)
NETWORK_BOX = (ADDON_PANEL[0], ADDON_PANEL[1] * (1 / 2))
INFO_BOX = (ADDON_PANEL[0], 80)
MENU_WIDTH, MENU_HEIGHT = ADDON_PANEL[0], NETWORK_BOX[1] - INFO_BOX[1]
OPTION_WIDTH, OPTION_HEIGHT = WIDTH, HEIGHT

FPS = 40
display = True

ENVIRONMENT = 'connect4'
PLAYER_TYPES = ['Human', 'Best', 'Train']
DIFFICULTY = ['Medium', 'Hard']
NEAT_INPUTS = {DIFFICULTY[0]: 2, DIFFICULTY[1]: 8}
SPEEDS = [1, 2, 10, 100, 500]
SHOW_EVERY = ['Genome', 'Generation', 'None']
COLOUR_THEMES = ['Light', 'Dark']

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
ENVIRONMENT_DIR = f"{ROOT_DIR}\\{ENVIRONMENT}"
MODELS_DIR = f"{ENVIRONMENT_DIR}\\models\\"
MODEL_NAME = "%s_%s"

# Globals - Defaults
players = [{'type': PLAYER_TYPES[0], 'difficulty': DIFFICULTY[0], 'neat': None},
           {'type': PLAYER_TYPES[1], 'difficulty': DIFFICULTY[0], 'neat': None}]
game_speed = SPEEDS[2]
evolution_speed = SPEEDS[-1]
max_fps = max(FPS, max(game_speed, evolution_speed))
show_every = SHOW_EVERY[1]
colour_theme = COLOUR_THEMES[1]

# Globals - Pygame
if display:
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"
    pg.init()
    display = pg.display.set_mode((WIDTH, HEIGHT), depth=32)

    pg.display.set_caption("Connect 4 with NEAT - v" + __version__)
    game_display = pg.Surface(GAME_PANEL)
    network_display = pg.Surface(NETWORK_BOX)
    info_display = pg.Surface(INFO_BOX)
    menu_display = pg.Surface((MENU_WIDTH, MENU_HEIGHT))
    options_display = pg.Surface((OPTION_WIDTH, OPTION_HEIGHT))
    display.fill(mlpg.BLACK)
    clock = pg.time.Clock()

connect4 = None
network = None
info = None
menu = None
options = None

if not os.path.exists(os.path.dirname(MODELS_DIR)):
    os.makedirs(os.path.dirname(MODELS_DIR))


def getSpeedShow() -> tuple:
    """
    Returns that speed and show values depending on player details.
    :return:
        - speed, show - tuple[int, bool]
    """
    if players[0]['type'] == PLAYER_TYPES[2] or players[1]['type'] == PLAYER_TYPES[2]:
        if show_every == SHOW_EVERY[1]:
            for player_key in range(connect4.MAX_PLAYERS):
                if players[player_key]['type'] == PLAYER_TYPES[2] and\
                        players[player_key]['neat'].current_species == players[player_key]['neat'].current_genome == 0:
                    return game_speed, True
            return evolution_speed, False
        elif show_every == SHOW_EVERY[2]:
            return evolution_speed, False
    return game_speed, True


def getColourTheme() -> dict:
    if colour_theme == COLOUR_THEMES[1]:
        colours = {'text': mlpg.LIGHT_GRAY, 'button': mlpg.GRAY,
                   'selected': mlpg.DARK_GREEN, 'bg1': mlpg.DARK_GRAY, 'bg2': mlpg.GRAY, 'bg3': mlpg.DARK_BLUE,
                   '-1': mlpg.LIGHT_GRAY, '0': mlpg.DARK_RED, '1': mlpg.DARK_YELLOW,
                   'input': mlpg.DARK_BLUE, 'output': mlpg.DARK_RED, 'hidden': mlpg.LIGHT_GRAY,
                   'active': mlpg.DARK_GREEN, 'deactivated': mlpg.DARK_RED}
    else:
        colours = {'text': mlpg.BLACK, 'button': mlpg.LIGHT_GRAY,
                   'selected': mlpg.GREEN, 'bg1': mlpg.WHITE, 'bg2': mlpg.LIGHT_GRAY, 'bg3': mlpg.BLUE,
                   '-1': mlpg.WHITE, '0': mlpg.RED, '1': mlpg.YELLOW,
                   'input': mlpg.BLUE, 'output': mlpg.RED, 'hidden': mlpg.BLACK,
                   'active': mlpg.GREEN, 'deactivated': mlpg.RED}
    return colours


def setupAi(current_player: dict, outputs: int = 1, population: int = 100) -> NEAT:
    """
    Sets up neat with game settings in mind.
    :param current_player: dict[str: Any]
    :param outputs: int
    :param population: int
    :return:
        - neat - NEAT
    """
    file = MODELS_DIR + MODEL_NAME % (current_player['type'], current_player['difficulty'])
    if os.path.isfile(file + '.neat'):
        neat = NEAT.load(file)
    else:
        neat = NEAT(ENVIRONMENT_DIR)
        inputs = NEAT_INPUTS[current_player['difficulty']]
        neat.generate(inputs, outputs, population=population)
        neat.save(file)
    return neat


def setup(users: list) -> list:
    """
    Sets the global variables and neats for players.
    :param users: list[dict[str: Any]]
    :return:
        - users - list[dict[str: Any]]
    """
    global connect4, network, info, menu, options
    colours = getColourTheme()
    connect4 = Connect4(GAME_PANEL, colour_theme=colours)
    network = visualize.Network(NETWORK_BOX, colour_theme=colours)
    info = visualize.Info(INFO_BOX, colour_theme=colours)
    options = Options(colour_theme=colours)
    menu = Menu(colour_theme=colours)
    for player_key in range(connect4.MAX_PLAYERS):
        current_player = users[player_key]
        users[player_key]['neat'] = None
        if current_player['type'] != PLAYER_TYPES[0]:
            users[player_key]['neat'] = setupAi(current_player)
    return users


def neatMove(player: dict, genome: Genome) -> int:
    """
    Calculates the best move for the genome with input data based on AI difficulty.
    :param player: dict[str: Any]
    :param genome: Genome
    :return:
        - move - int
    """
    possible_moves = {}
    for i in range(connect4.COLUMNS):
        possible_move = connect4.getPossibleMove(i)
        if possible_move[0] != connect4.INVALID_MOVE:
            possible_moves[possible_move] = 0
    input_range = {'max': max(connect4.ROWS, connect4.COLUMNS), 'min': 0}
    for possible_move in possible_moves:
        if player['difficulty'] == DIFFICULTY[0]:
            inputs = {}
            directions = connect4.getPieceSlices(possible_move)
            for player_key in [connect4.current_player, connect4.opponent]:
                connection_counts = connect4.getConnectionCounts(directions, player_key)
                for direction_pair in directions:
                    if direction_pair not in inputs:
                        inputs[direction_pair] = []
                    connection = sum(connection_counts[direction_pair]) + 1
                    normalized_input = (connection - input_range['min']) / (input_range['max'] - input_range['min'])
                    inputs[direction_pair].append(normalized_input)
            for direction_pair in inputs:
                possible_moves[possible_move] += sum(genome.forward(inputs[direction_pair]))
        elif player['difficulty'] == DIFFICULTY[1]:
            inputs = []
            directions = connect4.getPieceSlices(possible_move)
            for player_key in [connect4.current_player, connect4.opponent]:
                connection_counts = connect4.getConnectionCounts(directions, player_key)
                for direction_pair in directions:
                    connection = sum(connection_counts[direction_pair]) + 1
                    normalized_input = (connection - input_range['min']) / (input_range['max'] - input_range['min'])
                    inputs.append(normalized_input)
            possible_moves[possible_move] += sum(genome.forward(inputs))
    sorted_moves = ml.dict.combineByValues(possible_moves)
    max_min_keys = ml.list.findMaxMin(list(sorted_moves.keys()))
    move = random.choice(sorted_moves[max_min_keys['max']['value']])
    return move[1]


def checkBest(player_key: int, match_range: int = 50, win_threshold: float = 0.1) -> None:
    """
    Update the best neat for each difficulty depending on win rate with current
    trained neat.
    :param player_key: int
    :param match_range: int
    :param win_threshold: float
    :return:
        - None
    """
    setup(players)
    win_count = 0
    for _ in range(match_range):
        run = True
        while run:
            current_player = players[connect4.current_player]
            if connect4.match:
                current_genome = current_player['neat'].best_genome
                possible_move = neatMove(current_player, current_genome)
                connect4.main(possible_move)

            if not connect4.match:
                if connect4.result == connect4.WIN:
                    win_count += 1 if connect4.current_player == player_key else -1
                connect4.reset()
                run = False
    if (win_count / match_range) >= win_threshold:
        print(f"New Best {players[player_key]['difficulty']} NEAT Gen[{players[player_key]['neat'].generation}]"
              f" (win rate): {round(win_count / match_range * 100, 2)}")
        file = MODELS_DIR + MODEL_NAME % (PLAYER_TYPES[1], players[player_key]['difficulty'])
        players[player_key]['neat'].save(file)
        setup(players)


def close() -> None:
    """
    Closes pygame and python in a safe manner.
    :return:
        - None
    """
    pg.quit()
    print(f"Thanks for using C4 with NEAT")
    time.sleep(1)
    sys.exit()


class Menu:
    """
    Menu is a class that allows buttons to be accessed during the main loop and handles the assigned action.
    """

    BOARDER = 30

    def __init__(self, **kwargs: Any):
        """
        Initiates the object with required values.
        :param kwargs: Any
        """
        self.colours = getColourTheme()

        self.buttons = [
            mlpg.Button("Reset", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (1 / 3)), self.colours['button'],
                        handler=connect4.reset),
            mlpg.Button("Options", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (1 / 3)), self.colours['button'],
                        handler=options.main),
            mlpg.Button("Null", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (2 / 3)), self.colours['button']),
            mlpg.Button("QUIT", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (2 / 3)), self.colours['button'],
                        handler=close)]

        self.update(kwargs=kwargs)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Updates the menu buttons and passes environment information.
        :param args: Any
        :param kwargs: Any
        :return:
            - None
        """
        if len(args) == 2:
            for button in self.buttons:
                button.update(args[0], args[1], origin=(GAME_PANEL[0], ADDON_PANEL[1] - MENU_HEIGHT))

        if 'kwargs' in kwargs:
            kwargs = kwargs['kwargs']
        if 'colour_theme' in kwargs:
            self.colours = kwargs['colour_theme']
            for button in self.buttons:
                button.update(colour=self.colours['button'], text_colour=self.colours['text'])

    def draw(self, surface: Any) -> None:
        """
        Draws the background and buttons to the given surface.
        :param surface: Any
        :return:
            - None
        """
        surface.fill(self.colours['bg1'])
        for button in self.buttons:
            button.draw(surface)


class Options:
    """
    Options handles changing the global variables like a settings menu.
    """
    BOARDER = 60

    def __init__(self, **kwargs: Any):
        """
        Initiates the object with required values.
        :param kwargs: Any
        """
        self.colours = getColourTheme()

        self.players = {}
        self.group_buttons = {}
        self.buttons = []
        self.messages = []

        self.generate()
        self.update()

    def generate(self) -> None:
        """
        Generates the options messages and buttons with default and global values.
        :return:
            - None
        """
        self.buttons = [mlpg.Button("Back", (OPTION_WIDTH * (2 / 5), OPTION_HEIGHT * (5 / 6)), self.colours['button'],
                                    handler=True),
                        mlpg.Button("QUIT", (OPTION_WIDTH * (3 / 5), OPTION_HEIGHT * (5 / 6)), self.colours['button'],
                                    handler=close)]
        self.messages = []

        gbi = {}
        for player_key in range(connect4.MAX_PLAYERS):
            gbi[f"Player {player_key + 1}:"] = {'selected': players[player_key]['type'], 'options': PLAYER_TYPES}
            self.group_buttons[f"Difficulty {player_key + 1}:"] = mlpg.ButtonGroup(DIFFICULTY,
                                                                                   (self.BOARDER + ((OPTION_WIDTH *
                                                                                                    (1 / 6)) + 520),
                                                                                    self.BOARDER + (player_key * 90)),
                                                                                   self.colours,
                                                                                   players[player_key]['difficulty'])

        gbi['Game Speed:'] = {'selected': game_speed, 'options': SPEEDS}
        gbi['Evolution Speed:'] = {'selected': evolution_speed, 'options': SPEEDS}
        gbi['Show Every:'] = {'selected': show_every, 'options': SHOW_EVERY}
        for group_key in gbi:
            self.group_buttons[group_key] = mlpg.ButtonGroup(gbi[group_key]['options'],
                                                             (self.BOARDER + (OPTION_WIDTH * (1 / 6) + 100),
                                                              self.BOARDER + (len(self.messages) * 90)),
                                                             self.colours, gbi[group_key]['selected'])
            self.messages.append(mlpg.Message(group_key, (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                                          self.BOARDER + (len(self.messages) * 90)),
                                              self.colours['text'], align='mr'))
        self.group_buttons[f"Colour Theme:"] = mlpg.ButtonGroup(COLOUR_THEMES,
                                                                (self.BOARDER + ((OPTION_WIDTH * (1 / 6)) + 520),
                                                                 self.BOARDER + ((len(self.messages) - 1) * 90)),
                                                                self.colours, colour_theme)

    def update(self, mouse_pos: tuple = None, mouse_clicked: bool = False, **kwargs: Any) -> bool:
        """
        Updates the option buttons, global variables and other related attributes.
        :param mouse_pos: tuple[int, int]
        :param mouse_clicked: bool
        :param kwargs: Any
        :return:
            - continue - bool
        """
        global players, game_speed, evolution_speed, max_fps, show_every, colour_theme
        if mouse_pos is not None:
            for button in self.buttons:
                action = button.update(mouse_pos, mouse_clicked, text_colour=self.colours['text'])
                if action is not None:
                    return True

        if players[0]['type'] == PLAYER_TYPES[2] or players[1]['type'] == PLAYER_TYPES[2]:
            if game_speed > evolution_speed:
                evolution_speed = game_speed
            self.group_buttons['Evolution Speed:'].update(active=True)
            self.group_buttons['Show Every:'].update(active=True)

        if players[0]['difficulty'] == players[1]['difficulty']:
            if players[0]['type'] == players[1]['type'] == PLAYER_TYPES[2]:
                players[0]['difficulty'] = DIFFICULTY[0]
                players[1]['difficulty'] = DIFFICULTY[1]

        if players[0]['type'] != PLAYER_TYPES[2] and players[1]['type'] != PLAYER_TYPES[2]:
            evolution_speed = SPEEDS[0]
            show_every = SHOW_EVERY[0]
            self.group_buttons['Evolution Speed:'].update(active=False)
            self.group_buttons['Show Every:'].update(active=False)
        if players[0]['type'] == PLAYER_TYPES[0] or players[1]['type'] == PLAYER_TYPES[0]:
            self.group_buttons['Game Speed:'].update(active=False)
            game_speed = SPEEDS[0]
        else:
            self.group_buttons['Game Speed:'].update(active=True)

        if players[0]['type'] == PLAYER_TYPES[0]:
            self.group_buttons['Difficulty 1:'].update(active=False)
        else:
            self.group_buttons['Difficulty 1:'].update(active=True)

        if players[1]['type'] == PLAYER_TYPES[0]:
            self.group_buttons['Difficulty 2:'].update(active=False)
        else:
            self.group_buttons['Difficulty 2:'].update(active=True)

        if mouse_pos is not None:
            for group in self.group_buttons:
                button_key = self.group_buttons[group].update(mouse_pos, mouse_clicked)
                if button_key is not None and self.group_buttons[group].active:
                    if 'Player' in group:
                        players[int(group[-2]) - 1]['type'] = PLAYER_TYPES[button_key]
                        setup(players)
                    elif 'Difficulty' in group:
                        players[int(group[-2]) - 1]['difficulty'] = DIFFICULTY[button_key]
                        if players[0]['difficulty'] == players[1]['difficulty']:
                            if players[0]['type'] == players[1]['type'] == PLAYER_TYPES[2]:
                                players[0]['difficulty'] = DIFFICULTY[0]
                                players[1]['difficulty'] = DIFFICULTY[1]
                        setup(players)
                    elif group == 'Game Speed:':
                        game_speed = SPEEDS[button_key]
                    elif group == 'Evolution Speed:':
                        evolution_speed = SPEEDS[button_key] if game_speed <= SPEEDS[button_key] else game_speed
                    elif group == 'Show Every:':
                        show_every = SHOW_EVERY[0]
                        if players[0]['type'] == PLAYER_TYPES[2] or players[1]['type'] == PLAYER_TYPES[2]:
                            show_every = SHOW_EVERY[button_key]
                    elif group == 'Colour Theme:':
                        colour_theme = COLOUR_THEMES[button_key]
                        self.colours = getColourTheme()
                        for group_key in self.group_buttons:
                            self.group_buttons[group_key].update(colours=self.colours)
                        for button in self.buttons:
                            button.update(colour=self.colours['button'], text_colour=self.colours['text'])
                        for message in self.messages:
                            message.update(colour=self.colours['text'])
                        connect4.game_board.update(colour_theme=self.colours)
                        network.update(colour_theme=self.colours)
                        info.update(colour_theme=self.colours)
                        menu.update(colour_theme=self.colours)

                    max_fps = max(FPS, max(game_speed, evolution_speed))

    def draw(self, surface: Any) -> None:
        """
        Draws the option buttons and texts to the surface.
        :param surface: Any
            - None
        :return:
        """
        surface.fill(self.colours['bg1'])
        for message in self.messages:
            message.draw(surface)
        for group in self.group_buttons:
            self.group_buttons[group].draw(surface)
        for button in self.buttons:
            button.draw(surface)

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
        - play - bool
    """
    global display, connect4, network, info, menu, options

    setup(players)

    run, frame_count = True, 1
    while run:
        current_player = players[connect4.current_player]
        speed, show = getSpeedShow()

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
                    if connect4.match and current_player['type'] == PLAYER_TYPES[0]:
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
            if current_player['type'] == PLAYER_TYPES[0]:
                if possible_move is not None:
                    connect4.main(possible_move)
                    if not connect4.match:
                        frame_count = 1
            else:
                if not display or not show or frame_count >= max_fps / speed:
                    frame_count = 1

                    current_genome = None
                    if current_player['type'] == PLAYER_TYPES[2]:
                        if current_player['neat'].shouldEvolve():
                            current_genome = current_player['neat'].getGenome()
                        else:
                            close()
                    elif current_player['type'] == PLAYER_TYPES[1]:
                        current_genome = current_player['neat'].best_genome

                    possible_move = neatMove(current_player, current_genome)
                    connect4.main(possible_move)

                    if show and display:
                        network.generate(current_genome)
                        info.update(current_player['neat'].getInfo())

        if not connect4.match:
            if not display or not show or frame_count >= max_fps / speed:
                fitness = connect4.fitnessEvaluation()
                gen_str = 'Generation: 1 - %d, 2 - %d'
                gens = [0, 0]
                for i, player_key in enumerate([connect4.current_player, connect4.opponent]):
                    if players[player_key]['type'] == PLAYER_TYPES[2] and players[player_key]['neat'].shouldEvolve():
                        current_genome = players[player_key]['neat'].getGenome()
                        current_genome.fitness = fitness[i]
                        file_name = MODELS_DIR + MODEL_NAME % (players[player_key]['type'],
                                                               players[player_key]['difficulty'])
                        if players[player_key]['neat'].nextGenome(file_name):
                            checkBest(player_key)
                    if players[player_key]['type'] != PLAYER_TYPES[0]:
                        gens[player_key] = players[player_key]['neat'].generation
                if not display and show:
                    print(gen_str % tuple(gens))
                connect4.reset()

        if display:
            menu.draw(menu_display)
            display.blit(menu_display, (GAME_PANEL[0], GAME_PANEL[1] - MENU_HEIGHT))

            if show or current_player['type'] == PLAYER_TYPES[0]:
                connect4.draw(game_display)
                network.draw(network_display)
                info.draw(info_display)

            display.blit(game_display, (0, 0))
            display.blit(network_display, (GAME_PANEL[0], 0))
            display.blit(info_display, (GAME_PANEL[0], NETWORK_BOX[1]))

            pg.display.update()
            clock.tick(max_fps)
            frame_count += 2


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        close()
