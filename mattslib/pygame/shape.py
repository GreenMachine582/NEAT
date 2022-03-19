from __future__ import annotations

import pygame as pg

__version__ = '1.2.1'
__date__ = '19/03/2022'


class Rect:
    """
    Rect is an object that creates, and draws rectangles to given surface.
    """
    def __init__(self, pos: tuple, align: str, dims: list, colour: list):
        """
        Initiates the Shape object with given values.
        :param pos: tuple[int, int]
        :param align: str
        :param dims: list[int]
        :param colour: list[int]
        """
        self.pos = pos
        self.hotspot = pos
        self.align = align
        self.dims = dims
        self.colour = colour

        self.update()

    def update(self) -> None:
        """
        Updates hotspot of rect.
        :return:
            - None
        """
        if self.align == "ml":
            self.hotspot = (self.pos[0], (self.pos[1] - (self.dims[1]/2)))
        elif self.align == "mr":
            self.hotspot = ((self.pos[0] - self.dims[0]), (self.pos[1] - (self.dims[1]/2)))
        else:
            self.hotspot = ((self.pos[0] - (self.dims[0]/2)), (self.pos[1] - (self.dims[1]/2)))

    def draw(self, surface: Any, width: int = 0, boarder_radius: int = 0) -> None:
        """
        Draws an aligned rectangle to surface with given values.
        :param surface: Any
        :param width: int
        :param boarder_radius: int
        :return:
            - None
        """
        pg.draw.rect(surface, self.colour, pg.Rect(self.hotspot, self.dims), width, boarder_radius)

    def collide(self, pos: tuple, origin: tuple = (0, 0)) -> bool:
        """
        Checks if given pos collides with the rect object
        :param pos:  tuple[int, int]
        :param origin: tuple[int, int]
        :return:
            - collide - bool
        """
        pos = (pos[0] - origin[0], pos[1] - origin[1])
        if self.align == "ml":
            return True if self.hotspot[0] <= pos[0] <= (self.pos[0] + self.dims[0]) and \
                           self.hotspot[1] <= pos[1] <= (self.pos[1] + (self.dims[1]/2)) else False
        elif self.align == "mr":
            return True if self.hotspot[0] <= pos[0] <= self.pos[0] and \
                           self.hotspot[1] <= pos[1] <= (self.pos[1] + (self.dims[1]/2)) else False
        else:
            return True if self.hotspot[0] <= pos[0] <= (self.pos[0] + (self.dims[0] / 2)) and \
                           self.hotspot[1] <= pos[1] <= (self.pos[1] + (self.dims[1] / 2)) else False
