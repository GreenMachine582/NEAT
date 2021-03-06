from __future__ import annotations

import os
import random
import sys
import time

import pygame as pg

from connect4 import Connect4
import visualize
from neat import NEAT

import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.6.7'
__date__ = '29/04/2022'

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
overwrite = False

ENVIRONMENT = 'connect4'
PLAYER_TYPES = ['Human', 'Best', 'Train']
DIFFICULTY = ['Easy', 'Medium', 'Hard']
NEAT_INPUTS = {DIFFICULTY[0]: 2, DIFFICULTY[1]: 8, DIFFICULTY[2]: 42}
NEAT_OUTPUTS = {DIFFICULTY[0]: 1, DIFFICULTY[1]: 1, DIFFICULTY[2]: 7}
SPEEDS = [1, 2, 5, 10, 40]
SHOW_EVERY = ['Genome', 'Generation']
COLOUR_THEMES = ['Light', 'Dark']

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
ENVIRONMENT_DIR = f"{ROOT_DIR}\\{ENVIRONMENT}"
MODELS_DIR = f"{ENVIRONMENT_DIR}\\models\\"

# Globals - Defaults
players = [{'type': PLAYER_TYPES[1], 'difficulty': DIFFICULTY[0], 'neat': None},
           {'type': PLAYER_TYPES[1], 'difficulty': DIFFICULTY[1], 'neat': None}]
game_speed = SPEEDS[0]
show_every = SHOW_EVERY[1]
colour_theme = COLOUR_THEMES[1]

# Global - objects
connect4 = None
game_board = None
network = None
info = None
menu = None
options = None

# Pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"

if not os.path.exists(os.path.dirname(MODELS_DIR)):
    os.makedirs(os.path.dirname(MODELS_DIR))


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


def setupAi(player: dict, population: int = 15) -> NEAT:
    """
    Sets up neat with game settings in mind.
    :param player: dict[str: Any]
    :param population: int
    :return:
        - neat - NEAT
    """
    file = f"{MODELS_DIR}{player['type']}_{player['difficulty']}"
    if os.path.isfile(file + '.neat') and not overwrite:
        neat = NEAT.load(file)
    else:
        neat = NEAT(ENVIRONMENT_DIR, file_name=f"{player['type']}_{player['difficulty']}")
        neat.generate(NEAT_INPUTS[player['difficulty']], NEAT_OUTPUTS[player['difficulty']], population=population)
        neat.save()
    return neat


def setup() -> None:
    """
    Sets the global variables and NEATs for players.
    :return:
        - None
    """
    global connect4, game_board, network, info, menu, options, players
    connect4 = Connect4()
    if display:
        colours = getColourTheme()
        game_board = visualize.GameBoard(GAME_PANEL, connect4.ROWS, connect4.COLUMNS, colour_theme=colours)
        network = visualize.Network(NETWORK_BOX, colour_theme=colours)
        info = visualize.Info(INFO_BOX, colour_theme=colours)
        options = Options()
        menu = Menu()
    for player_key in range(connect4.MAX_PLAYERS):
        player = players[player_key]
        players[player_key]['neat'] = None
        if player['type'] != PLAYER_TYPES[0]:
            players[player_key]['neat'] = setupAi(player)


def neatMove(genome: Genome, args: Any = None) -> tuple:
    """
    Calculates the best move for the genome with input data based on AI difficulty.
    :param genome: Genome
    :param args: Any
    :return:
        - move - tuple[int, int]
    """
    c4, difficulty = args[0], args[1]
    player_ids = [c4.current_player, c4.opponent]
    possible_moves = {}
    for i in range(c4.COLUMNS):
        possible_move = c4.getPossibleMove(i)
        if possible_move[0] != c4.INVALID_MOVE:
            possible_moves[possible_move] = 0

    if genome.inputs == NEAT_INPUTS[difficulty[2]]:
        inputs = []
        for row in range(c4.ROWS):
            for piece in c4.board[row]:
                piece = 0 if piece == c4.current_player else 1 if piece == c4.opponent else piece
                inputs.append(piece)
        outputs = genome.forward(ml.list.normalize(inputs))
        for column in range(len(outputs)):
            for possible_move in possible_moves:
                if possible_move[1] == column:
                    possible_moves[possible_move] = outputs[column]

    input_range = {'max': max(c4.ROWS, c4.COLUMNS), 'min': 0}
    for possible_move in possible_moves:
        if genome.inputs == NEAT_INPUTS[difficulty[0]]:
            inputs = {}
            directions = c4.getDirectionalSlices(possible_move)
            for player_key in player_ids:
                connection_counts = c4.getConnectionCounts(directions, player_key, immediate_only=False)
                for direction_pair in directions:
                    if direction_pair not in inputs:
                        inputs[direction_pair] = []
                    connection = sum(connection_counts[direction_pair]) + 1
                    normalized_input = (connection - input_range['min']) / (input_range['max'] - input_range['min'])
                    inputs[direction_pair].append(normalized_input)
            for direction_pair in inputs:
                possible_moves[possible_move] += sum(genome.forward(inputs[direction_pair]))
        elif genome.inputs == NEAT_INPUTS[difficulty[1]]:
            inputs = []
            directions = c4.getDirectionalSlices(possible_move)
            for player_key in player_ids:
                connection_counts = c4.getConnectionCounts(directions, player_key, immediate_only=False)
                for direction_pair in directions:
                    connection = sum(connection_counts[direction_pair]) + 1
                    normalized_input = (connection - input_range['min']) / (input_range['max'] - input_range['min'])
                    inputs.append(normalized_input)
            possible_moves[possible_move] += sum(genome.forward(inputs))

    sorted_moves = ml.dict.combineByValues(possible_moves)
    max_min_keys = ml.list.findMaxMin(list(sorted_moves.keys()))
    return random.choice(sorted_moves[max_min_keys['max']['value']])


def checkBest(player_key: int, total_matches: int = 80, success_rate: float = 0.2) -> None:
    """
    Update the best neat for each difficulty depending on win rate with current
    trained neat.
    :param player_key: int
    :param total_matches: int
    :param success_rate: float
    :return:
        - None
    """
    global players
    opponent = abs(player_key - 1)
    temp_opponent = players[opponent]

    players[opponent] = {'type': PLAYER_TYPES[1], 'difficulty': players[player_key]['difficulty'], 'neat': None}
    players[opponent]['neat'] = setupAi(players[opponent])
    c4 = Connect4()

    lose_count, draw_count, win_count = 0, 0, 0
    for _ in range(total_matches):
        while c4.match:
            current_player = players[c4.current_player]
            best_genome = current_player['neat'].best_specie.representative
            possible_move = neatMove(best_genome, (c4, DIFFICULTY))
            result = c4.main(possible_move)
            if result == c4.WIN:
                if c4.current_player == player_key:
                    win_count += 1
                else:
                    lose_count += 1
            elif result == c4.DRAW:
                draw_count += 1
        c4.reset()

    if win_count - lose_count >= total_matches * success_rate:
        print(f"New Best {players[player_key]['difficulty']} NEAT Gen[{players[player_key]['neat'].generation}]"
              f" (l-d-w): {lose_count}-{draw_count}-{win_count} {round((win_count - lose_count) / total_matches * 100, 2):2}%")
        players[player_key]['neat'].save(f"{players[opponent]['type']}_{players[opponent]['difficulty']}")

    players[opponent] = temp_opponent
    if players[opponent]['type'] != PLAYER_TYPES[0]:
        players[opponent]['neat'] = setupAi(players[opponent])


def reset(args: Any = None):
    if args is not None:
        connect4.reset(args[0])
    else:
        connect4.reset()
    if display:
        game_board.reset()


def close() -> None:
    """
    Closes pygame and python after cleaning in a safe manner.
    :return:
        - None
    """
    pg.quit()
    print(f"Cleaning processes...")
    time.sleep(3)
    sys.exit('Thanks for using NEAT with Connect 4')


class Menu:
    """
    Menu is a class that allows buttons to be accessed during the main loop and handles the assigned action.
    """

    BOARDER = 30

    def __init__(self):
        """
        Initiates the object with required values.
        """
        self.colours = getColourTheme()

        self.buttons = [mlpg.Button("Reset", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (1 / 3)), self.colours['button'],
                                    handler=reset, args=(False,)),
                        mlpg.Button("Options", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (1 / 3)), self.colours['button'],
                                    handler=options.main),
                        mlpg.Button("Swap Turn", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (2 / 3)), self.colours['button'],
                                    handler=reset),
                        mlpg.Button("QUIT", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (2 / 3)), self.colours['button'],
                                    handler=close)]
        for button in self.buttons:
            button.update(text_colour=self.colours['text'])
        self.update()

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

    def __init__(self):
        """
        Initiates the object with required values.
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
                                                                                    self.BOARDER + 80 +
                                                                                    (player_key * 90)),
                                                                                   self.colours,
                                                                                   players[player_key]['difficulty'])

        gbi['Game Speed:'] = {'selected': game_speed, 'options': SPEEDS}
        gbi['Show Every:'] = {'selected': show_every, 'options': SHOW_EVERY}
        for group_key in gbi:
            self.group_buttons[group_key] = mlpg.ButtonGroup(gbi[group_key]['options'],
                                                             (self.BOARDER + (OPTION_WIDTH * (1 / 6) + 100),
                                                              self.BOARDER + 80 + (len(self.messages) * 90)),
                                                             self.colours, gbi[group_key]['selected'])
            self.messages.append(mlpg.Message(group_key, (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                                          self.BOARDER + 80 + (len(self.messages) * 90)),
                                              self.colours['text'], align='mr'))
        self.group_buttons[f"Colour Theme:"] = mlpg.ButtonGroup(COLOUR_THEMES,
                                                                (self.BOARDER + ((OPTION_WIDTH * (1 / 6)) + 520),
                                                                 self.BOARDER + 80 + ((len(self.messages) - 1) * 90)),
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
        global players, game_speed, show_every, colour_theme
        if mouse_pos is not None:
            for button in self.buttons:
                action = button.update(mouse_pos, mouse_clicked, text_colour=self.colours['text'])
                if action is not None:
                    return True

        if players[0]['type'] == PLAYER_TYPES[2] or players[1]['type'] == PLAYER_TYPES[2]:
            self.group_buttons['Show Every:'].update(active=True)

        if players[0]['difficulty'] == players[1]['difficulty']:
            if players[0]['type'] == players[1]['type'] == PLAYER_TYPES[2]:
                players[0]['difficulty'] = DIFFICULTY[0]
                players[1]['difficulty'] = DIFFICULTY[1]

        if players[0]['type'] != PLAYER_TYPES[2] and players[1]['type'] != PLAYER_TYPES[2]:
            self.group_buttons['Show Every:'].update(active=False)
        if players[0]['type'] == PLAYER_TYPES[0] or players[1]['type'] == PLAYER_TYPES[0]:
            game_speed = SPEEDS[0]
            self.group_buttons['Game Speed:'].selected = game_speed
            self.group_buttons['Game Speed:'].update(active=False)
        else:
            self.group_buttons['Game Speed:'].selected = game_speed
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
                        setup()
                    elif 'Difficulty' in group:
                        players[int(group[-2]) - 1]['difficulty'] = DIFFICULTY[button_key]
                        if players[0]['difficulty'] == players[1]['difficulty']:
                            if players[0]['type'] == players[1]['type'] == PLAYER_TYPES[2]:
                                players[0]['difficulty'] = DIFFICULTY[0]
                                players[1]['difficulty'] = DIFFICULTY[1]
                        setup()
                    elif group == 'Game Speed:':
                        game_speed = SPEEDS[button_key]
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
                        game_board.update(colour_theme=self.colours)
                        network.update(colour_theme=self.colours)
                        info.update(colour_theme=self.colours)
                        menu.update(colour_theme=self.colours)

        if 'kwargs' in kwargs:
            kwargs = kwargs['kwargs']
        if 'colour_theme' in kwargs:
            self.colours = kwargs['colour_theme']
            for button in self.buttons:
                button.update(colour=self.colours['button'], text_colour=self.colours['text'])

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

    setup()

    run, frame_count = True, 1
    while run:
        current_player = connect4.current_player
        player = players[connect4.current_player]

        possible_move = None
        mouse_clicked = False
        if display:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if connect4.match and player['type'] == PLAYER_TYPES[0]:
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
            move = connect4.INVALID_MOVE
            if display and player['type'] == PLAYER_TYPES[0]:  # Human move
                if possible_move is not None:
                    move = connect4.getPossibleMove(possible_move)
            else:  # NEAT Move
                if not display or frame_count % int(FPS / game_speed) == 0:
                    current_genome = None
                    if show_every == SHOW_EVERY[1] or player['type'] == PLAYER_TYPES[1]:
                        current_genome = player['neat'].best_specie.representative
                    elif show_every == SHOW_EVERY[0]:
                        current_genome = player['neat'].getGenome()

                    if player['type'] == PLAYER_TYPES[2]:
                        if player['neat'].shouldEvolve():
                            if show_every == SHOW_EVERY[0]:
                                player['neat'].nextGenome()
                            elif show_every == SHOW_EVERY[1]:
                                results = player['neat'].parallelTest(neatMove, connect4, DIFFICULTY)
                                player['neat'].parallelEvolve(connect4.fitnessEvaluation(), results)
                        else:
                            return
                        checkBest(current_player)

                    move = neatMove(current_genome, (connect4, DIFFICULTY))

                    if display:
                        network.generate(current_genome)
                        info.update(player['neat'].getInfo())

            if move != connect4.INVALID_MOVE:
                result = connect4.main(move)
                if display:
                    game_board.update(move=move, player=current_player)
                    if result == connect4.WIN:
                        game_board.showWin(connect4, move)

                if not connect4.match:
                    frame_count = 1

        if not connect4.match:
            if not display:
                print("NEATs: 1 - %d %d, 2 - %d %d" % (players[0]['neat'].generation, len(players[0]['neat'].species),
                                                       players[1]['neat'].generation, len(players[1]['neat'].species)))
            if not display or frame_count % int(FPS / game_speed) == 0:
                reset()

        if display:
            menu.draw(menu_display)
            display.blit(menu_display, (GAME_PANEL[0], GAME_PANEL[1] - MENU_HEIGHT))

            game_board.update(text=f"{connect4.PLAYERS[connect4.current_player]}'s turn!")
            game_board.draw(game_display)
            network.draw(network_display)
            info.draw(info_display)

            display.blit(game_display, (0, 0))
            display.blit(network_display, (GAME_PANEL[0], 0))
            display.blit(info_display, (GAME_PANEL[0], NETWORK_BOX[1]))

            pg.display.update()
            clock.tick(FPS)
            frame_count += 1


if __name__ == '__main__':
    if display:
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
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     pass
    # raise close()
