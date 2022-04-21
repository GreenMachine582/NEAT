from __future__ import annotations

import mattslib.pygame as mlpg
from .message import Message
from .shape import Rect

__version__ = '1.2.5'
__date__ = '21/04/2022'


class Button(object):
    """
    Button is an object that creates and draws interactive buttons for
    the user to use.
    """
    def __init__(self, text: Any, pos: tuple, colour: tuple, handler: Any = None, args: Any = None, align: str = '',
                 dims: list = None):
        """
        Initiates the Button object with given values.
        :param text: Any
        :param pos: tuple[float, float]
        :param colour: tuple[int, int, int]
        :param handler: Any
        :param args: Any
        :param align: str
        :param dims: list[int | float]
        """
        self.text = text
        self.pos = pos
        self.colour = colour
        self.handler = handler
        self.args = args
        self.align = align
        self.dims = dims

        self.mouse_over = False
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
        if 'args' in kwargs:
            self.args = kwargs['args']
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
            self.mouse_over = self.button_rect.collide(mouse_pos, origin=origin)
            if self.mouse_over and mouse_clicked:
                if callable(self.handler):
                    if self.args is None:
                        return self.handler()
                    else:
                        return self.handler(self.args)
                return self.handler if self.handler is not None else True

        if self.active and self.mouse_over:
            colour = mlpg.changeColour(self.colour, 40)
            highlight = self.colour
        else:
            colour = self.colour
            highlight = mlpg.changeColour(self.colour, -40)
            if not self.active:
                colour = mlpg.changeColour(colour, -50)
                highlight = mlpg.changeColour(colour, -50)

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


class ButtonGroup(object):
    """
    Forms a group of buttons, with active and selected states.
    """

    PADDING = 40

    def __init__(self, *args: Any, align: str = ''):
        """
        Initiates the button group with given values.
        :param args: Any
        :param align: str
        :param button_states: list[bool]
        """
        self.options = args[0]
        self.pos = args[1]
        self.colours = args[2]
        self.selected = args[3]

        self.align = align

        self.active = True
        self.show = True

        self.buttons = []
        for i, text in enumerate(self.options):
            self.buttons.append(Button(text, (self.pos[0] + (i * (self.PADDING + 100)), self.pos[1]),
                                       self.colours['button'], align=self.align))
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

        if 'colours' in kwargs:
            self.colours = kwargs['colours']
        if 'active' in kwargs:
            self.active = kwargs['active']
            for button in self.buttons:
                button.update(active=self.active)
        if 'show' in kwargs:
            self.show = kwargs['show']
            for button in self.buttons:
                button.update(show=self.show)

        for button_key, button in enumerate(self.buttons):
            button.update(text_colour=self.colours['text'])
            button.update(colour=self.colours['button'])
            if self.options[button_key] == self.selected:
                button.update(colour=self.colours['selected'])

        if mouse_pos is not None and self.active:
            for button_key, button in enumerate(self.buttons):
                action = button.update(mouse_pos, mouse_clicked, origin=origin)
                if action is not None:
                    self.selected = self.options[button_key]
                    self.update()
                    return button_key

    def draw(self, surface: Any) -> None:
        """
        Draws the group of buttons.
        :param surface: Any
        :return:
            - None
        """
        for button in self.buttons:
            button.draw(surface)
