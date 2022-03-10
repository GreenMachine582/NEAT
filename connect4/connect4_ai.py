
import pygame as pg
import os
import random

from neat import NEAT
from mattslib import condense, findMaxMin

__version__ = '1.4'
__date__ = '10/03/2022'

# Constants
WIDTH, HEIGHT = 1120, 640
GAME_WIDTH, GAME_HEIGHT = HEIGHT, HEIGHT
NETWORK_WIDTH, NETWORK_HEIGHT = WIDTH - GAME_WIDTH, HEIGHT * (3/4)
INFO_WIDTH, INFO_HEIGHT = NETWORK_WIDTH, HEIGHT - NETWORK_HEIGHT

RPS = 144  # Loops per second
FPS = 40  # Frames per second

OVERWRITE = False
AI = True
TRAIN = True
DRAW = True

# Colors
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
GREY = [200, 200, 200]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
DARKER = [-65, -65, -65]

# os.environ['SDL_VIDEO_CENTERED'] = '1'
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,25"
DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def changeColour(colour, change_by=None):
    if change_by is None:
        change_by = DARKER
    new_colour = [colour[i] + change_by[i] for i in range(len(colour))]
    for i in range(len(colour)):
        new_colour[i] = 0 if new_colour[i] < 0 else 255 if new_colour[i] > 255 else new_colour[i]
    return new_colour


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
            pg.draw.circle(window, changeColour(self.highlight_colour), self.center_pos, self.radius)
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

    def __init__(self):
        self.board = []
        self.condensed_board = []
        self.active = True
        self.visible = True
        self.colour = {'background': BLUE}
        self.current_player = 1
        self.opponent = 2 if self.current_player == 1 else 1
        self.turn = 0

        self.generate()

    def generate(self):
        self.board = [[Piece([h, j], self.ROWS, self.COLUMNS, self.EMPTY)
                       for j in range(self.COLUMNS)] for h in range(self.ROWS)]
        self.condensed_board = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def reset(self):
        self.generate()
        self.turn = 0
        self.current_player = random.choice([1, 2])
        # print(f"Player {self.current_player} will move first!")

    def draw(self, window, boarder=10):
        window.fill(changeColour(self.colour['background']))
        pg.draw.rect(window, self.colour['background'], ([boarder, boarder],
                                                         [GAME_WIDTH - (boarder * 2), GAME_HEIGHT - (boarder * 2)]))
        for row in self.board:
            for piece in row:
                piece.draw(window)

    def makeTurn(self, move):
        if move is not None:
            self.board[move[0]][move[1]].setColour(self.PLAYERS[self.current_player])
            self.condensed_board[move[0]][move[1]] = self.current_player
            self.turn += 1
        game_state = self.winChecker(move) if move is not None else -2
        if game_state != -1:
            pass
            # print(self.GAME_STATES[game_state])
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

    def winChecker(self, move):
        draw = True
        colour = self.PLAYERS[self.current_player]

        directions = {'vertical': {(1, 0): 0, (-1, 0): 0}, 'horizontal': {(0, 1): 0, (0, -1): 0},
                      'diagonal1': {(-1, 1): 0, (1, -1): 0}, 'diagonal2': {(1, 1): 0, (-1, -1): 0}}
        connected = False
        for direction_pair in directions:
            for direction in directions[direction_pair]:
                for n in range(1, self.LENGTH):
                    a, b = move[0] + (n * direction[0]), move[1] + (n * direction[1])
                    if 0 <= a < self.ROWS and 0 <= b < self.COLUMNS:
                        piece = self.board[a][b]
                        if piece.colour == colour:
                            directions[direction_pair][direction] += 1
                        else:
                            if piece.colour == self.EMPTY:
                                draw = False
                            break
                    else:
                        break
            if sum(directions[direction_pair].values()) == self.LENGTH - 1:
                self.showWin(move, directions[direction_pair], GREEN)
                connected = True
        if connected:
            return self.current_player

        if draw:
            for row in self.board:
                for piece in row:
                    if piece.colour == self.EMPTY:
                        draw = False

        return 0 if draw else -1


class Network:
    BOARDER = 20
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

    def generate(self, current_genome):
        node_depths = current_genome.getNodesByDepth()
        connections = current_genome.connections

        max_depth = max(list(node_depths.keys()))

        for depth in node_depths:
            for i, node_index in enumerate(node_depths[depth]):
                node_type = current_genome.getNodeType(node_index)
                pos = [int(self.BOARDER + (self.BOARDER/3) + (NETWORK_WIDTH - (2 * self.BOARDER)) * (depth/max_depth)),
                       int(self.BOARDER + (NETWORK_HEIGHT - (2 * self.BOARDER)) * (i/len(node_depths[depth])))]
                center_pos = [int(pos[0] - self.radius), int(pos[1] - self.radius)]
                self.network[node_index] = {'pos': center_pos, 'colour': self.colour[node_type], 'connections': []}

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
    BOARDER = 30

    def __init__(self):
        self.active = True
        self.visible = True
        self.colour = {'background': WHITE}
        self.font = pg.font.Font('freesansbold.ttf', 20)

        self.texts = {}

        self.generate()

    def generate(self):
        self.texts['1'] = self.makeText("Generation:", [20, 10], 'ml')
        self.texts['2'] = self.makeText("Species:", [20, 45], 'ml')
        self.texts['3'] = self.makeText("Genome:", [20, 80], 'ml')
        self.texts['4'] = self.makeText("Fittest:", [20, 115], 'ml')

    def makeText(self, content, pos, align='center'):
        text = self.font.render(content, True, BLACK, WHITE)
        text_rect = text.get_rect()
        if align == "ml":
            text_rect.midleft = pos
        elif align == "mr":
            text_rect.midright = pos
        else:
            text_rect.center = pos
        return [text, text_rect]

    def update(self, neat_info):
        self.texts['generation'] = self.makeText(str(neat_info['generation']), [150, 10], 'ml')
        self.texts['current_species'] = self.makeText(str(neat_info['current_species']), [150, 45], 'ml')
        self.texts['current_genome'] = self.makeText(str(neat_info['current_genome']), [150, 80], 'ml')
        self.texts['fittest'] = self.makeText(str(neat_info['fittest']), [150, 115], 'ml')

    def draw(self, window):
        window.fill(self.colour['background'])
        for text_key in self.texts:
            window.blit(self.texts[text_key][0], self.texts[text_key][1])


def main():
    global DRAW
    pg.init()

    display = pg.display.set_mode((WIDTH, HEIGHT), depth=32)
    pg.display.set_caption("Connect 4 with NEAT")
    game_display = pg.Surface((GAME_WIDTH, GAME_HEIGHT))
    network_display = pg.Surface((NETWORK_WIDTH, NETWORK_HEIGHT))
    info_display = pg.Surface((INFO_WIDTH, INFO_HEIGHT))
    clock = pg.time.Clock()

    connect4 = Connect4()
    network = Network()
    info = Info()

    neat_ai = {}
    if AI:
        for player in connect4.PLAYERS:
            if os.path.isfile(f"{__file__}_{player}.neat") and not OVERWRITE:
                neat_ai[player] = NEAT.load(f"{__file__}_{player}")
            else:
                neat_ai[player] = NEAT(DIRECTORY)
                neat_ai[player].generate(connect4.ROWS * connect4.COLUMNS, connect4.COLUMNS, population=100)

    alive = True
    run, match, frame_count = True, True, 0
    while run:
        current_genome = None
        if AI:
            current_genome = neat_ai[connect4.current_player].getGenome()
            if frame_count == 0:
                network.generate(current_genome)
                if connect4.current_player == 1:
                    info.update(neat_ai[connect4.current_player].getInfo())

        possible_move = None
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
                    break
                elif event.key == pg.K_s:
                    DRAW = not DRAW
                if match and not AI:
                    if event.key == pg.K_r:
                        connect4.reset()

                    elif event.key in [pg.K_1, pg.K_KP1]:
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

        if AI:
            inputs = condense(connect4.condensed_board)
            if neat_ai[connect4.current_player].shouldEvolve():
                outputs = current_genome.forward(inputs)
                possible_move = findMaxMin(outputs)['max']['index']
                current_genome.fitness = connect4.turn
            # else:
            #     pg.quit()
            #     quit()

        move = None
        if possible_move is not None and match:
            move = connect4.getPossibleMove(possible_move)
            result = connect4.makeTurn(move)
            if result in [0, 1, 2]:
                match = False
            if result in [-2, 0, connect4.opponent] and AI:
                alive = False
                match = False

        if frame_count == 0:
            if DRAW:
                display.fill(BLACK)
                connect4.draw(game_display)
                network.draw(network_display)
                info.draw(info_display)
                display.blit(game_display, (0, 0))
                display.blit(network_display, (GAME_WIDTH, 0))
                display.blit(info_display, (GAME_WIDTH, NETWORK_HEIGHT))
            # print(neat_ai[connect4.current_player].getInfo())
            pg.display.update()

        frame_count = 0 if frame_count >= RPS else frame_count + FPS
        clock.tick(RPS)

        if not match and TRAIN and AI:
            if alive:
                pass
                # print("Good job ai you pass")
            if AI:
                neat_ai[connect4.current_player].save(f"{__file__}_{connect4.current_player}")
                neat_ai[connect4.current_player].nextGenome()
                current_genome = neat_ai[connect4.current_player].getGenome()
                network.generate(current_genome)
                connect4.reset()
                match, alive = True, True

        if move is not None:
            connect4.switchPlayer()

    pg.quit()
    quit()


if __name__ == "__main__":
    main()
