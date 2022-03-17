import pygame as pg
import os

from connect4 import Connect4
from neat import NEAT
import mattslib as ml
import mattslib.pygame as mlpg

__version__ = '1.4'
__date__ = '17/03/2022'

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_PANEL = (HEIGHT, HEIGHT)
ADDON_PANEL = (WIDTH - GAME_PANEL[0], HEIGHT)
NETWORK_WIDTH, NETWORK_HEIGHT = ADDON_PANEL[0], ADDON_PANEL[1] * (1 / 2)
INFO_WIDTH, INFO_HEIGHT = ADDON_PANEL[0], 80
MENU_WIDTH, MENU_HEIGHT = ADDON_PANEL[0], NETWORK_HEIGHT - INFO_HEIGHT
OPTION_WIDTH, OPTION_HEIGHT = WIDTH, HEIGHT

FPS = 40
MAX_FPS = 500

OVERWRITE = True
TRAIN = True

GAME = 'connect4'
PLAYER_TYPES = ['human', 'neat']
SHOW_EVERY = ['Genome', 'Generation', 'None']
SPEEDS = [1, 5, 25, 100, MAX_FPS]
DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Colors
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
GREY = [200, 200, 200]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
DARKER = [-65, -65, -65]

# Globals - Defaults
players = {1: {'type': PLAYER_TYPES[1]}, 2: {'type': PLAYER_TYPES[1]}}
show_every = SHOW_EVERY[0]
game_speed = SPEEDS[-1]
evolution_speed = SPEEDS[-1]

# Globals - Pygame
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,25"
pg.init()
display = pg.display.set_mode((WIDTH, HEIGHT), depth=32)

pg.display.set_caption("Connect 4 with NEAT - v" + __version__)
game_display = pg.Surface(GAME_PANEL)
network_display = pg.Surface((NETWORK_WIDTH, NETWORK_HEIGHT))
info_display = pg.Surface((INFO_WIDTH, INFO_HEIGHT))
menu_display = pg.Surface((MENU_WIDTH, MENU_HEIGHT))
options_display = pg.Surface((OPTION_WIDTH, OPTION_HEIGHT))
display.fill(BLACK)
clock = pg.time.Clock()

connect4 = Connect4()
network = None
info = None
menu = None
options = None


def calculateFitness(result, player, opponent, turn):
    fitness = 0
    if result == player:
        fitness += 100
    elif result == 0:
        fitness += 25
    elif result == opponent:
        fitness -= 100
    fitness -= turn
    return fitness


def setupAi(player_id, inputs, outputs=1):
    if os.path.isfile(f"{DIRECTORY}\\{GAME}\\ai_{player_id}.neat") and not OVERWRITE:
        neat = NEAT.load(f"{DIRECTORY}\\{GAME}\\ai_{player_id}")
    else:
        neat = NEAT(f"{DIRECTORY}\\{GAME}")
        neat.generate(inputs, outputs, population=50)
    return neat


def getSpeedShow(current_player):
    if show_every == 'Generation' and\
            current_player['neat'].current_species == current_player['neat'].current_genome == 0:
        return game_speed, True
    if show_every in ['Generation', 'None']:
        return evolution_speed, False
    return game_speed, True


def setup():
    global connect4, network, info, menu, options, players
    connect4 = Connect4()
    network = Network()
    info = Info()
    options = Options()
    menu = Menu()
    for player_id in players:
        if players[player_id]['type'] == 'neat':
            players[player_id]['neat'] = setupAi(player_id, connect4.LENGTH)


def switch():
    global connect4, players
    temp = players[1]
    players[1] = players[2]
    players[2] = temp
    connect4.reset()


def close():
    pg.quit()
    quit()


class Network:
    BOARDER = 40
    SPACING = 1

    def __init__(self):
        self.active = True
        self.visible = True
        self.colour = {'background': WHITE,
                       'input': BLUE, 'output': RED, 'hidden': BLACK,
                       'active': GREEN, 'deactivated': RED}
        self.network = {}
        self.radius = 5
        self.diameter = self.radius * 2

    def generate(self, current_genome, width=None, height=None):
        if width is None:
            width = NETWORK_WIDTH - (2 * self.BOARDER)
        if height is None:
            height = NETWORK_HEIGHT - (2 * self.BOARDER)

        self.network = {}
        node_depths = current_genome.getNodesByDepth()
        node_depths = ml.dict.removeKeys(node_depths)
        connections = current_genome.connections

        for d, depth in enumerate(node_depths):
            for i, node_index in enumerate(node_depths[depth]):
                node_type = current_genome.nodes[node_index].layer_type
                i = 1 if len(node_depths[depth]) == 1 else i
                pos = [int(self.BOARDER + width * (d / (len(node_depths) - 1))),
                       int(self.BOARDER + height * (i / max(len(node_depths[depth]) - 1, 2)))]
                self.network[node_index] = {'pos': pos, 'colour': self.colour[node_type], 'connections': []}

        for pos in connections:
            colour = self.colour['active'] if connections[pos].active else self.colour['deactivated']
            connection = {'start': self.network[pos[0]]['pos'], 'end': self.network[pos[1]]['pos'], 'colour': colour,
                          'thickness': int(max(3, min(abs(connections[pos].weight), 1)))}
            self.network[pos[0]]['connections'].append(connection)

    def draw(self, window):
        window.fill(self.colour['background'])
        for node in self.network:
            for connection in self.network[node]['connections']:
                pg.draw.line(window, connection['colour'], connection['start'], connection['end'],
                             connection['thickness'])
        for node in self.network:
            pg.draw.circle(window, self.network[node]['colour'], self.network[node]['pos'], self.radius)


class Info:
    BOARDER = 20

    def __init__(self):
        self.active = True
        self.visible = True
        self.colour = {'background': [200, 200, 200]}

        self.header = {}
        self.data = {}

        self.generate()

    def generate(self):
        self.header['generation'] = mlpg.Message("Generation:", [self.BOARDER, self.BOARDER], align='ml')
        self.header['specie'] = mlpg.Message("Species:", [self.BOARDER, INFO_HEIGHT - self.BOARDER], align='ml')
        self.header['genome'] = mlpg.Message(":Genome", [INFO_WIDTH - self.BOARDER, self.BOARDER], align='mr')
        self.header['fitness'] = mlpg.Message(":Fitness", [INFO_WIDTH - self.BOARDER, INFO_HEIGHT - self.BOARDER],
                                              align='mr')

    def update(self, neat_info):
        self.data['generation'] = mlpg.Message(neat_info['generation'], [150, self.BOARDER], align='ml')
        self.data['species'] = mlpg.Message(neat_info['current_species'], [150, INFO_HEIGHT - self.BOARDER], align='ml')
        self.data['genome'] = mlpg.Message(neat_info['current_genome'], [360, self.BOARDER], align='mr')
        self.data['fitness'] = mlpg.Message(neat_info['fitness'], [360, INFO_HEIGHT - self.BOARDER], align='mr')

    def draw(self, window):
        window.fill(self.colour['background'])
        for text_key in self.header:
            self.header[text_key].draw(window)

        for text_key in self.data:
            self.data[text_key].draw(window)


class Menu:
    BOARDER = 30

    def __init__(self):
        self.colour = {'background': WHITE}

        self.buttons = []

        self.generate()

    def generate(self):
        self.buttons = [
            mlpg.Button("Reset", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (1 / 3)), GREY, handler=connect4.reset),
            mlpg.Button("Options", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (1 / 3)), GREY,
                        handler=options.main),
            mlpg.Button("Switch", (MENU_WIDTH * (1 / 3), MENU_HEIGHT * (2 / 3)), GREY, handler=switch),
            mlpg.Button("QUIT", (MENU_WIDTH * (2 / 3), MENU_HEIGHT * (2 / 3)), GREY, handler=close)]

    def update(self, mouse_pos, mouse_clicked):
        for button in self.buttons:
            button.mouseOver(mouse_pos, mouse_clicked, origin=(GAME_PANEL[0], ADDON_PANEL[1] - MENU_HEIGHT))

    def draw(self, window):
        window.fill(self.colour['background'])
        for button in self.buttons:
            button.draw(window)


class Options:
    BOARDER = 60

    def __init__(self):
        self.colour = {'background': WHITE}

        self.players = {}
        self.buttons = {}
        self.group_buttons = {}
        self.messages = []

        self.generate()

    def generate(self):
        self.buttons = {'back': mlpg.Button("Back", (OPTION_WIDTH * (2 / 5), OPTION_HEIGHT * (5 / 6)),
                                            GREY),
                        'quit': mlpg.Button("QUIT", (OPTION_WIDTH * (3 / 5), OPTION_HEIGHT * (5 / 6)),
                                            GREY, handler=close)}
        self.messages = []

        for player_key in players:
            button_states = [True if players[player_key]['type'] == player_type else False
                             for player_type in PLAYER_TYPES]
            self.group_buttons[f"player_{player_key}"] = mlpg.ButtonGroup(['Human', 'NEAT'],
                                                                          (
                                                                          self.BOARDER + (OPTION_WIDTH * (1 / 6)) + 100,
                                                                          self.BOARDER + (len(self.messages) * 90)),
                                                                          GREY, GREEN, button_states=button_states)
            self.messages.append(mlpg.Message(f"Player {player_key}:",
                                              (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                               self.BOARDER + (len(self.messages) * 90)), align='mr'))

        button_states = [True if speed == game_speed else False for speed in SPEEDS]
        self.group_buttons['game_speed'] = mlpg.ButtonGroup(SPEEDS, (self.BOARDER + (OPTION_WIDTH * (1 / 6)) + 100,
                                                                     self.BOARDER + (len(self.messages) * 90)),
                                                            GREY, GREEN, button_states=button_states)
        self.messages.append(mlpg.Message(f"Game Speed:", (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                                           self.BOARDER + (len(self.messages) * 90)), align='mr'))

        button_states = [True if speed == evolution_speed else False for speed in SPEEDS]
        self.group_buttons['evolution_speed'] = mlpg.ButtonGroup(SPEEDS, (self.BOARDER + (OPTION_WIDTH * (1 / 6)) + 100,
                                                                          self.BOARDER + (len(self.messages) * 90)),
                                                                 GREY, GREEN, button_states=button_states)
        self.messages.append(mlpg.Message(f"Evolution Speed:", (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                                                self.BOARDER + (len(self.messages) * 90)), align='mr'))

        button_states = [True if SHOW == show_every else False for SHOW in SHOW_EVERY]
        self.group_buttons['show'] = mlpg.ButtonGroup(SHOW_EVERY, (self.BOARDER + (OPTION_WIDTH * (1 / 6)) + 100,
                                                                   self.BOARDER + (len(self.messages) * 90)),
                                                      GREY, GREEN, button_states=button_states)
        self.messages.append(mlpg.Message(f"Show Every:", (self.BOARDER + (OPTION_WIDTH * (1 / 6)),
                                                           self.BOARDER + (len(self.messages) * 90)), align='mr'))

    def update(self, mouse_pos, mouse_clicked):
        global players, game_speed, evolution_speed, show_every
        for button_key in self.buttons:
            if self.buttons[button_key].mouseOver(mouse_pos, mouse_clicked):
                return True

        for group in self.group_buttons:
            button_key = self.group_buttons[group].update(mouse_pos, mouse_clicked)
            if button_key is not None:
                if group in ['player_1', 'player_2']:
                    players[int(group[-1])]['type'] = PLAYER_TYPES[button_key]
                    setup()
                elif group == 'game_speed':
                    game_speed = SPEEDS[button_key]
                elif group == 'evolution_speed':
                    evolution_speed = SPEEDS[button_key]
                elif group == 'show':
                    show_every = SHOW_EVERY[button_key]

    def draw(self, window):
        window.fill(self.colour['background'])
        for message in self.messages:
            message.draw(window)
        for group in self.group_buttons:
            self.group_buttons[group].draw(window)
        for button_keys in self.buttons:
            self.buttons[button_keys].draw(window)

    def main(self):
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


def main():
    global display, connect4, network, info, menu, options

    setup()

    frame_count, speed, show = 1, game_speed, True
    run = True
    while run:
        current_player = players[connect4.current_player]
        speed, show = getSpeedShow(current_player)

        possible_move = None
        mouse_clicked = False
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
            if current_player['type'] == PLAYER_TYPES[1]:
                if frame_count >= MAX_FPS / speed:
                    frame_count = 1
                    current_genome = current_player[PLAYER_TYPES[1]].getGenome()
                    if show:
                        network.generate(current_genome)
                        info.update(current_player[PLAYER_TYPES[1]].getInfo())

                    move = connect4.neatMove(current_genome)

                    if not current_player[PLAYER_TYPES[1]].shouldEvolve() and TRAIN:
                        close()

                    result = connect4.makeMove(move)
                    if result != -1:
                        connect4.match = False
                    else:
                        connect4.switchPlayer()

                    if not connect4.match and TRAIN:
                        current_genome.fitness = calculateFitness(result, connect4.current_player,
                                                                  connect4.opponent, connect4.turn)
                        current_player[PLAYER_TYPES[1]].save(f"{DIRECTORY}\\{GAME}\\ai_{connect4.current_player}")
                        current_player[PLAYER_TYPES[1]].nextGenome()

            elif current_player['type'] == PLAYER_TYPES[0]:
                if possible_move is not None:
                    move = connect4.getPossibleMove(possible_move)
                    result = connect4.makeMove(move)
                    if result not in [-2, -1]:
                        connect4.match = False
                        frame_count = 1
                    else:
                        connect4.switchPlayer()

        if not connect4.match:
            if players[1]['type'] == PLAYER_TYPES[1] and players[2]['type'] == PLAYER_TYPES[1]:
                switch()
            if frame_count >= MAX_FPS / speed:
                connect4.reset()

        menu.draw(menu_display)
        display.blit(menu_display, (GAME_PANEL[0], GAME_PANEL[1] - MENU_HEIGHT))

        if show or current_player['type'] == PLAYER_TYPES[0]:
            connect4.draw(game_display)
            network.draw(network_display)
            info.draw(info_display)

        display.blit(game_display, (0, 0))
        display.blit(network_display, (GAME_PANEL[0], 0))
        display.blit(info_display, (GAME_PANEL[0], NETWORK_HEIGHT))

        pg.display.update()
        clock.tick(MAX_FPS)
        frame_count += 1

    close()


if __name__ == '__main__':
    main()
