
__version__ = '1.1'
__date__ = '14/03/2022'

import pygame as pg


class Shape:
    def __init__(self, pos, colour, align, dimensions=None):
        self.pos = pos
        self.colour = colour
        self.align = align
        self.dimensions = dimensions

    def drawRect(self, game_display):
        if self.align == "l":
            p.draw.rect(game_display, self.colour, ((self.pos[0]), (self.pos[1] - (self.dimensions[1]/2)),
                                                    self.dimensions[0], self.dimensions[1]))
        elif self.align == "r":
            p.draw.rect(game_display, self.colour, ((self.pos[0] - self.dimensions[0]), (self.pos[1] -
                                                                                         (self.dimensions[1]/2)),
                                                    self.dimensions[0], self.dimensions[1]))
        else:
            p.draw.rect(game_display, self.colour, ((self.pos[0] - (self.dimensions[0]/2)), (self.pos[1] -
                                                                                             (self.dimensions[1]/2)),
                                                    self.dimensions[0], self.dimensions[1]))

