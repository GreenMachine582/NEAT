from __future__ import annotations

from pygame import font

__version__ = '1.2.1'
__date__ = '19/03/2022'


font.init()


class Message(object):
    """
    Message is an object that handles updating and drawing a message.
    """
    def __init__(self, text: Any, pos: tuple, colour: list = None, size: int = 20, align: str = ''):
        """
        Initiates the Message object with given values.
        :param text: Any
        :param pos: tuple[int, int]
        :param colour: list[int]
        :param size: int
        :param align: str
        """
        self.text = text
        self.pos = pos
        self.colour = colour if colour is not None else [0, 0, 0]
        self.size = size
        self.align = align
        self.font = 'freesansbold.ttf'

        self.text_surface = None
        self.text_rect = None

        self.update()

    def update(self, dims: list = None) -> None:
        """
        Updates the position of the message.
        :param dims: list[int]
        :return:
            - None
        """
        padding = 0 if dims is None else int((dims[0] / 2) - (self.text_rect[2] / 2))

        text_font = font.Font(self.font, self.size)
        self.text_surface = text_font.render(str(self.text), True, self.colour)
        self.text_rect = self.text_surface.get_rect()
        if self.align == "ml":
            self.text_rect.midleft = (self.pos[0] + padding, self.pos[1])
        elif self.align == "mr":
            self.text_rect.midright = (self.pos[0] - padding, self.pos[1])
        else:
            self.text_rect.center = self.pos

    def draw(self, surface: Any) -> None:
        """
        Draws that text to the given surface.
        :param surface: Any
        :return:
            - None
        """
        surface.blit(self.text_surface, self.text_rect)
