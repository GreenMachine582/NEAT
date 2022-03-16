from .shape import Shape
from .button import Button, ButtonGroup
from .message import Message


def changeColour(colour, change_by=-70):
    new_colour = [colour[i] + change_by for i in range(len(colour))]
    for i in range(len(colour)):
        new_colour[i] = 0 if new_colour[i] < 0 else 255 if new_colour[i] > 255 else new_colour[i]
    return new_colour


__all__ = ['changeColour', 'Shape', 'Button', 'ButtonGroup', 'Message']
