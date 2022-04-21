from __future__ import annotations

from .shape import Rect, Circle
from .button import Button, ButtonGroup
from .message import Message

__all__ = ['changeColour', 'Rect', 'Circle', 'Button', 'ButtonGroup', 'Message']
__version__ = '1.2'


# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
DARK_RED = (200, 0, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 140, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (100, 255, 100)
DARK_BLUE = (0, 0, 140)
BLUE = (0, 0, 255)
DARK_YELLOW = (200, 200, 0)
YELLOW = (255, 255, 0)


def changeColour(colour: tuple, change_by: Any) -> tuple:
    """
    Changes the given colour with value, the clamps the colour ranges.
    :param colour: tuple[int, int, int]
    :param change_by: Any
    :return:
        - new_colour - tuple[int, int, int]
    """
    if isinstance(change_by, int):
        new_colour = [colour[i] + change_by for i in range(len(colour))]
    elif isinstance(change_by, list):
        new_colour = [colour[i] + change_by[i] for i in range(len(colour))]
    else:
        return colour
    for i in range(len(colour)):
        new_colour[i] = 0 if new_colour[i] < 0 else 255 if new_colour[i] > 255 else new_colour[i]
    return tuple(new_colour)
