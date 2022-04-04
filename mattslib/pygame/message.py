from __future__ import annotations

from pygame import font

import mattslib.pygame as mlpg

__version__ = '1.2.2'
__date__ = '5/04/2022'


font.init()


class Message(object):
    """
    Message is an object that handles updating and drawing a message.
    """
    def __init__(self, text: Any, pos: tuple, colour: list = None, size: int = 20, align: str = ''):
        """
        Initiates the Message object with given values.
        :param text: Any
        :param pos: tuple[int | float, int | float]
        :param colour: list[int]
        :param size: int
        :param align: str
        """
        self.text = text
        self.pos = pos
        self.colour = colour if colour is not None else mlpg.BLACK
        self.size = size
        self.align = align

        self.font = 'freesansbold.ttf'

        self.text_surface = None
        self.text_rect = None

        self.update()

    def update(self, **kwargs: Any) -> None:
        """
        Updates the position of the message and other relevant attributes.
        :param kwargs: Any
        :return:
            - None
        """

        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'pos' in kwargs:
            self.pos = kwargs['pos']
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
        if 'size' in kwargs:
            self.size = kwargs['size']
        if 'align' in kwargs:
            self.align = kwargs['align']
        if 'font' in kwargs:
            self.font = kwargs['font']

        text_font = font.Font(self.font, self.size)
        self.text_surface = text_font.render(str(self.text), True, self.colour)
        self.text_rect = self.text_surface.get_rect()

        padding = [self.text_rect[2] / 2, self.text_rect[3] / 2]
        if 'dims' in kwargs:
            for i in range(len(padding)):
                padding[i] = int(kwargs['dims'][i] / 2)

        hotspot = [int(self.pos[0]), int(self.pos[1])]
        if 'l' in self.align:
            hotspot[0] += padding[0]
        elif 'r' in self.align:
            hotspot[0] -= padding[0]
        if 't' in self.align:
            hotspot[1] -= padding[1]
        elif 'b' in self.align:
            hotspot[1] += padding[1]
        self.text_rect.center = hotspot

    def draw(self, surface: Any) -> None:
        """
        Draws that text to the given surface.
        :param surface: Any
        :return:
            - None
        """
        surface.blit(self.text_surface, self.text_rect)
