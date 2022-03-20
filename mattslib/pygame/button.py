from __future__ import annotations

import pygame as pg
from .message import Message
from .shape import Rect, Circle

__version__ = '1.2.1'
__date__ = '20/03/2022'


def changeColour(colour: list, change_by: Any) -> list:
    """
    Changes the given colour with value, the clamps the colour ranges.
    :param colour: list[int]
    :param change_by: Any
    :return:
        - new_colour - list[int]
    """
    if isinstance(change_by, int):
        new_colour = [colour[i] + change_by for i in range(len(colour))]
    elif isinstance(change_by, list):
        new_colour = [colour[i] + change_by[i] for i in range(len(colour))]
    else:
        return colour
    for i in range(len(colour)):
        new_colour[i] = 0 if new_colour[i] < 0 else 255 if new_colour[i] > 255 else new_colour[i]
    return new_colour


class Button:
    """
    Button is an object that creates and draws interactive buttons for
    the user to use.
    """
    def __init__(self, *args: Any, handler: Any = None, align: str = '', dims: list = None):
        """
        Initiates the Button object with given values.
        :param args: Any
        :param handler: Any
        :param align: str
        :param dims: list[int | float]
        """
        self.text = args[0]
        self.pos = args[1]
        self.colour = args[2]
        self.handler = handler
        self.align = align
        self.dims = dims

        self.selected = False
        self.active = True
        self.show = True

        self.message = Message(self.text, self.pos, align=self.align)
        if self.dims is None:
            width = 120 if self.message.text_rect[2] <= 90 else self.message.text_rect[2] + 20
            height = 70 if self.message.text_rect[3] <= 60 else self.message.text_rect[3] + 20
            self.dims = [width, height]

        self.button_rect = Rect(self.pos, self.colour, self.dims, self.align)
        self.button_boarder = Rect(self.pos, self.colour, self.dims, self.align)

        self.update()

    def update(self, *args, **kwargs: Any) -> Any:
        """
        Updates the button and sets values.
        :param args: Any
        :param kwargs: Any
        :return:
            - handler - Any
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
        if 'active' in kwargs:
            self.active = kwargs['active']
        if 'show' in kwargs:
            self.show = kwargs['show']

        if mouse_pos is not None and self.active and self.show:
            self.selected = self.button_rect.collide(mouse_pos, origin=origin)
            if self.selected and mouse_clicked:
                if callable(self.handler):
                    return self.handler()
                return self.handler if self.handler is not None else True

        if self.active and self.selected:
            colour = changeColour(self.colour, 40)
            highlight = self.colour
        else:
            colour = self.colour
            highlight = changeColour(self.colour, -40)
            if not self.active:
                colour = changeColour(colour, -50)
                highlight = changeColour(colour, -50)

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
        if self.show:
            self.button_rect.draw(surface, boarder_radius=4)
            self.button_boarder.draw(surface, width=5, boarder_radius=4)
            self.message.draw(surface)


class ButtonGroup:
    """
    Forms a group of buttons, with active and selected states.
    """

    PADDING = 40

    def __init__(self, *args: Any, align: str = '', single_active: bool = True, button_states: list = None):
        """
        Initiates the button group with given values.
        :param args: Any
        :param align: str
        :param single_active: bool
        :param button_states: list[bool]
        """
        self.texts = args[0]
        self.pos = args[1]
        self.colour = args[2]
        self.active_colour = args[3]
        self.align = align

        self.active = True

        self.single_active = single_active
        self.buttons = {}
        self.button_states = button_states if button_states is not None else [False for _ in range(len(self.texts))]
        for i, text in enumerate(self.texts):
            colour = self.active_colour if self.button_states[i] else self.colour
            self.buttons[i] = Button(text, (self.pos[0] + (i * (self.PADDING + 100)), self.pos[1]), colour,
                                     align=self.align)

        self.update()

    def update(self, *args: Any, **kwargs: Any) -> int:
        """
        Updates the group of buttons and sets values.
        :param args: Any
        :param kwargs: Any
        :return:
            - button_key - int
        """
        if len(args) == 2:
            mouse_pos, mouse_clicked = args[0], args[1]
        else:
            mouse_pos, mouse_clicked = None, False

        origin = kwargs['origin'] if 'origin' in kwargs else (0, 0)

        if 'colour' in kwargs:
            self.colour = kwargs['colour']
        if 'active_colour' in kwargs:
            self.active_colour = kwargs['active_colour']
        if 'button_states' in kwargs:
            self.button_states = kwargs['button_states']

        if mouse_pos is not None:
            for button_key in self.buttons:
                colour = self.active_colour if self.button_states[button_key] else self.colour
                action = self.buttons[button_key].update(mouse_pos, mouse_clicked, origin=origin, colour=colour)
                if action is not None:
                    if self.single_active:
                        self.button_states = [False for _ in range(len(self.buttons))]
                        self.button_states[button_key] = True
                        return button_key

    def draw(self, surface: Any) -> None:
        """
        Draws the group of buttons.
        :param surface: Any
        :return:
            - None
        """
        for button_key in self.buttons:
            self.buttons[button_key].draw(surface)
