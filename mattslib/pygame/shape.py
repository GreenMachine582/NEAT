from __future__ import annotations

import math

import pygame as pg

__version__ = '1.2.2'
__date__ = '7/04/2022'


class Rect(object):
    """
    Rect is an object that draws, updates and checks collisions with
    given environment.
    """

    def __init__(self, pos: tuple, colour: list, dims: list, align: str = ''):
        """
        Initiates the Rect object with given values.
        :param pos: tuple[int | float, int | float]
        :param colour: list[int]
        :param dims: list[int | float]
        :param align: str
        """
        self.pos = pos
        self.colour = colour
        self.dims = dims
        self.align = align

        self.hotspot = pos

        self.update()

    def update(self, **kwargs: Any) -> None:
        """
        Updates hotspot of rect and other values if necessary.
        :param kwargs: Any
        :return:
            - None
        """
        if 'pos' in kwargs:
            self.pos = kwargs['pos']
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
        if 'dims' in kwargs:
            self.dims = kwargs['dims']
        if 'align' in kwargs:
            self.align = kwargs['align']

        hotspot = [int(self.pos[0]), int(self.pos[1])]

        if 'l' in self.align:
            hotspot[0] += int(self.dims[0] / 2)
        elif 'r' in self.align:
            hotspot[0] -= int(self.dims[0] / 2)
        if 't' in self.align:
            hotspot[1] -= int(self.dims[1] / 2)
        elif 'b' in self.align:
            hotspot[1] += int(self.dims[1] / 2)

        self.hotspot = tuple(hotspot)

    def draw(self, surface: Any, width: int = 0, boarder_radius: int = 0) -> None:
        """
        Draws an aligned rectangle to surface with given values.
        :param surface: Any
        :param width: int
        :param boarder_radius: int
        :return:
            - None
        """
        pos = (self.hotspot[0] - self.dims[0]/2, self.hotspot[1] - self.dims[1]/2)
        pg.draw.rect(surface, self.colour, pg.Rect(pos, self.dims), width, boarder_radius)

    def collide(self, pos: tuple, origin: tuple = (0, 0)) -> bool:
        """
        Checks if given pos collides with the rect object
        :param pos:  tuple[int, int]
        :param origin: tuple[int, int]
        :return:
            - collide - bool
        """
        pos = (pos[0] - origin[0], pos[1] - origin[1])
        if pos[0] in range(int(self.hotspot[0] - self.dims[0] / 2), int(self.hotspot[0] + self.dims[0] / 2)) and \
                pos[1] in range(int(self.hotspot[1] - self.dims[1] / 2), int(self.hotspot[1] + self.dims[1] / 2)):
            return True
        return False


class Circle(object):
    """
    Circle is an object that draws, updates and checks collisions with
    given environment.
    """

    def __init__(self, pos: tuple, colour: list, radius: float, align: str = ''):
        """
        Initiates the Circle object with given values.
        :param pos: tuple[float, float]
        :param colour: list[int]
        :param radius: float
        :param align: str
        """
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.align = align

        self.hotspot = pos

        self.update()

    def update(self, **kwargs: Any) -> None:
        """
        Updates hotspot and other values if necessary.
        :param kwargs: Any
        :return:
            - None
        """
        if 'pos' in kwargs:
            self.pos = kwargs['pos']
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
        if 'radius' in kwargs:
            self.radius = kwargs['radius']
        if 'align' in kwargs:
            self.align = kwargs['align']

        hotspot = [self.pos[0], self.pos[1]]

        if 'l' in self.align:
            hotspot[0] += self.radius
        elif 'r' in self.align:
            hotspot[0] -= self.radius
        if 't' in self.align:
            hotspot[1] += self.radius
        elif 'b' in self.align:
            hotspot[1] -= self.radius

        self.hotspot = tuple(hotspot)

    def draw(self, surface: Any, width: int = 0) -> None:
        """
        Draws the shape to surface.
        :param surface: Any
        :param width: int
        :return:
            - None
        """
        pg.draw.circle(surface, self.colour, self.hotspot, self.radius, width)

    def collide(self, pos: tuple, origin: tuple = (0, 0)) -> bool:
        """
        Checks if given position collides with the shape.
        :param pos:  tuple[int, int]
        :param origin: tuple[int, int]
        :return:
            - collide - bool
        """
        pos = (pos[0] - origin[0], pos[1] - origin[1])

        if pos[0] in range(int(self.hotspot[0] - self.radius), int(self.hotspot[0] + self.radius)) and \
                pos[1] in range(int(self.hotspot[1] - self.radius), int(self.hotspot[1] + self.radius)):
            distance = math.sqrt((pos[0] - self.hotspot[0]) ** 2 + (pos[1] - self.hotspot[1]) ** 2)
            if distance <= self.radius:
                return True
        return False
