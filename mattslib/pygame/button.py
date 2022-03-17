
__version__ = '1.2'
__date__ = '18/03/2022'

import pygame as pg
from .message import Message


def changeColour(colour, change_by=-40):
    new_colour = [colour[i] + change_by for i in range(len(colour))]
    for i in range(len(colour)):
        new_colour[i] = 0 if new_colour[i] < 0 else 255 if new_colour[i] > 255 else new_colour[i]
    return new_colour


class Button:
    def __init__(self, text, pos, colour, handler=None, align='', dims=None):
        self.text = text
        self.pos = pos
        self.colour = colour
        self.handler = handler
        self.align = align
        self.dims = dims

        self.active = False

        self.message = Message(text, pos, align=align)

        if self.dims is None:
            width = 120 if self.message.text_rect[2] <= 90 else self.message.text_rect[2] + 20
            height = 70 if self.message.text_rect[3] <= 60 else self.message.text_rect[3] + 20
            self.dims = [width, height]

        self.message.generate(self.dims)

    def draw(self, surface):
        colour = self.colour if not self.active else changeColour(self.colour, 40)
        highlight = changeColour(self.colour) if not self.active else self.colour
        if self.align == "ml":
            pg.draw.rect(surface, colour, pg.Rect(self.pos[0], self.pos[1] - (self.dims[1] / 2),
                                                  self.dims[0], self.dims[1]), 0, 4)
            pg.draw.rect(surface, highlight, pg.Rect(self.pos[0], self.pos[1] - (self.dims[1] / 2),
                                                     self.dims[0], self.dims[1]), 5, 4)
        elif self.align == "mr":
            pg.draw.rect(surface, colour, pg.Rect(self.pos[0] - self.dims[0],
                                                  self.pos[1] - (self.dims[1] / 2),
                                                  self.dims[0], self.dims[1]), 0, 4)
            pg.draw.rect(surface, highlight, pg.Rect(self.pos[0] - self.dims[0],
                                                     self.pos[1] - (self.dims[1] / 2),
                                                     self.dims[0], self.dims[1]), 5, 4)
        else:
            pg.draw.rect(surface, colour, pg.Rect(self.pos[0] - (self.dims[0] / 2),
                                                  self.pos[1] - (self.dims[1] / 2),
                                                  self.dims[0], self.dims[1]), 0, 4)
            pg.draw.rect(surface, highlight, pg.Rect(self.pos[0] - (self.dims[0] / 2),
                                                     self.pos[1] - (self.dims[1] / 2),
                                                     self.dims[0], self.dims[1]), 5, 4)
        self.message.draw(surface)

    def mouseOver(self, mouse_pos, mouse_clicked, origin=(0, 0)):
        if self.align == "ml":
            self.active = True if self.pos[0] <= (mouse_pos[0] - origin[0]) <= (self.pos[0] + self.dims[0]) and \
                                  (self.pos[1] - (self.dims[1]/2)) <= (mouse_pos[1] - origin[1]) <=\
                                  (self.pos[1] + (self.dims[1]/2)) else False
        elif self.align == "mr":
            self.active = True if (self.pos[0] - self.dims[0]) <= (mouse_pos[0] - origin[0]) <= self.pos[0] and \
                                  (self.pos[1] - self.dims[1]/2) <= (mouse_pos[1] - origin[1]) <= \
                                  (self.pos[1] + (self.dims[1]/2)) else False
        else:
            self.active = True if (self.pos[0] - (self.dims[0] / 2)) <= (mouse_pos[0] - origin[0]) <= \
                                  (self.pos[0] + (self.dims[0] / 2)) and (self.pos[1] - (self.dims[1] / 2)) <=\
                                  (mouse_pos[1] - origin[1]) <= (self.pos[1] + (self.dims[1] / 2)) else False

        if self.active and mouse_clicked:
            return self.clicked()
        return None

    def clicked(self):
        if self.handler is not None:
            if isinstance(self.handler, bool):
                return self.handler
            return self.handler()
        return True


class ButtonGroup:
    PADDING = 40

    def __init__(self, texts, pos, colour, active_colour, align='', dims=None, single_active=True, button_states=None):
        self.texts = texts
        self.pos = pos
        self.colour = colour
        self.active_colour = active_colour
        self.align = align
        self.dims = dims

        self.single_active = single_active
        self.buttons = {}
        self.button_states = button_states if button_states is not None else [False for _ in range(len(self.texts))]

        self.generate()

    def generate(self):
        for i, text in enumerate(self.texts):
            colour = self.active_colour if self.button_states[i] else self.colour
            self.buttons[i] = Button(text, (self.pos[0] + (i*(self.PADDING + 100)), self.pos[1]), colour, align=self.align)

    def update(self, mouse_pos, mouse_clicked):
        for button_key in self.buttons:
            action = self.buttons[button_key].mouseOver(mouse_pos, mouse_clicked)
            if action is not None:
                if self.single_active:
                    self.button_states = [False for _ in range(len(self.buttons))]
                    self.button_states[button_key] = True
                    self.generate()
                    return button_key

    def draw(self, surface):
        for button_key in self.buttons:
            self.buttons[button_key].draw(surface)
