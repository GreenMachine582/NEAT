from __future__ import annotations

import pygame as pg
from .message import Message
from .shape import Rect

__version__ = '1.2.1'
__date__ = '19/03/2022'


def changeColour(colour: list, change_by: int = -40) -> list:
    """
    Changes the given colour with value, the clamps the colour ranges.
    :param colour: list[int]
    :param change_by: int
    :return:
        - new_colour - list[int]
    """
    new_colour = [colour[i] + change_by for i in range(len(colour))]
    for i in range(len(colour)):
        new_colour[i] = 0 if new_colour[i] < 0 else 255 if new_colour[i] > 255 else new_colour[i]
    return new_colour


class Button:
    """
    Button is an object that creates and draws interactive buttons for
    the user to use.
    """
    def __init__(self, text: Any, pos: tuple, colour: list, handler: Any = None, align: str = '', dims: list = None):
        """
        Initiates the Button object with given values.
        :param text: Any
        :param pos: tuple[int | float, int | float]
        :param colour: list[int]
        :param handler: Any
        :param align: str
        :param dims: list[int | float]
        """
        self.text = text
        self.pos = pos
        self.colour = colour
        self.handler = handler
        self.align = align
        self.dims = dims

        self.selected = False
        self.active = True

        self.message = Message(self.text, self.pos, align=self.align)
        if self.dims is None:
            width = 120 if self.message.text_rect[2] <= 90 else self.message.text_rect[2] + 20
            height = 70 if self.message.text_rect[3] <= 60 else self.message.text_rect[3] + 20
            self.dims = [width, height]

        self.button_rect = Rect(self.pos, self.align, self.dims, colour)
        self.button_boarder = Rect(self.pos, self.align, self.dims, colour)

        self.update()

    def update(self, *args, **kwargs: Any) -> None:
        """
        Updates the button and sets values.
        :param args: Any
        :param kwargs: Any
        :return:
            - None
        """
        if len(args) == 2:
            mouse_pos, mouse_clicked = args[0], args[1]
        else:
            mouse_pos, mouse_clicked = None, False

        origin = kwargs['origin'] if 'origin' in kwargs else (0, 0)
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.message.update(text=self.text)
        if 'pos' in kwargs:
            self.pos = kwargs['pos']
            self.button_rect.update(pos=self.pos)
            self.button_boarder.update(pos=self.pos)
            self.message.update(pos=self.pos)
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
        if 'text_colour' in kwargs:
            self.message.update(colour=kwargs['text_colour'])
        if 'handler' in kwargs:
            self.handler = kwargs['handler']
        if 'align' in kwargs:
            self.align = kwargs['align']
            self.button_rect.update(align=self.align)
            self.button_boarder.update(align=self.align)
            self.message.update(align=self.align)
        if 'dims' in kwargs:
            self.dims = kwargs['dims']
            self.button_rect.update(dims=self.dims)
            self.button_boarder.update(dims=self.dims)

        if mouse_pos is not None:
            self.selected = self.button_rect.collide(mouse_pos, origin=origin)
            if self.selected and mouse_clicked:
                if callable(self.handler):
                    return self.handler()
                return self.handler if self.handler is not None else True

        colour = self.colour if not self.selected else changeColour(self.colour, 40)
        highlight = changeColour(self.colour) if not self.selected else self.colour

        self.button_rect.update(colour=colour)
        self.button_boarder.update(colour=highlight)
        self.message.update(dims=self.dims)

    def draw(self, surface: Any) -> None:
        """
        Draws the button, boarder and text to the given surface.
        :param surface: Any
        :return:
            - None
        """
        self.button_rect.draw(surface, boarder_radius=4)
        self.button_boarder.draw(surface, width=5, boarder_radius=4)
        self.message.draw(surface)


class ButtonGroup:
    PADDING = 40

    def __init__(self, texts, pos, colour, active_colour, align='', dims=None, single_active=True, button_states=None):
        self.texts = texts
        self.pos = pos
        self.colour = colour
        self.active_colour = active_colour
        self.align = align
        self.dims = dims

        self.active = True

        self.single_active = single_active
        self.buttons = {}
        self.button_states = button_states if button_states is not None else [False for _ in range(len(self.texts))]

        self.update()

    def update(self, *args, **kwargs: Any) -> None:
        """
        Updates the group of buttons and sets values.
        :param args: Any
        :param kwargs: Any
        :return:
            - None
        """
        if len(args) == 2:
            mouse_pos, mouse_clicked = args[0], args[1]
        else:
            mouse_pos, mouse_clicked = None, False

        origin = kwargs['origin'] if 'origin' in kwargs else (0, 0)
        for i, text in enumerate(self.texts):
            colour = self.active_colour if self.button_states[i] else self.colour
            self.buttons[i] = Button(text, (self.pos[0] + (i * (self.PADDING + 100)), self.pos[1]), colour, align=self.align)

        if mouse_pos is not None:
            for button_key in self.buttons:
                action = self.buttons[button_key].update(mouse_pos, mouse_clicked, origin=origin)
                if action is not None:
                    if self.single_active:
                        self.button_states = [False for _ in range(len(self.buttons))]
                        self.button_states[button_key] = True
                        return button_key

    def draw(self, surface) -> None:
        """
        Draws the group of buttons.
        :param surface: Any
        :return:
            - None
        """
        for button_key in self.buttons:
            self.buttons[button_key].draw(surface)
