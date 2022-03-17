from __future__ import annotations

import math
import random

__version__ = '1.4.1'
__date__ = '17/03/2022'


def absolute(x: int | float) -> int | float:
    return abs(x)


def binaryStep(x: int | float) -> int | float:
    return 1 if x >= 0 else 0


def clamped(x: int | float) -> int | float:
    return max(-1.0, min(1.0, x))


def identity(x: int | float) -> int | float:
    return x


def log(x: int | float) -> int | float:
    x = max(1e-7, x)
    return math.log(x)


def tanh(x: int | float) -> int | float:
    x = max(-60.0, min(60.0, 2.5 * x))
    return math.tanh(x)


def leakyReLU(x: int | float) -> int | float:
    return x if x > 0 else 0.01 * x


def sigmoid(x: int | float) -> int | float:
    x = max(-60.0, min(60.0, 5 * x))
    return 1 / (1 + math.exp(-x))


def swish(x: int | float) -> int | float:
    return x * sigmoid(x)


def getActivation(activation: str = '') -> activation_function:
    """
    Returns the requested or a random activation function.
    :param activation: str
    :return:
        - activation_function - (x: int | float) -> int | float
    """
    activations = {'absolute': absolute,
                   'binaryStep': binaryStep,
                   'clamped': clamped,
                   'identity': identity,
                   'log': log,
                   'tanh': tanh,
                   'leakyReLU': leakyReLU,
                   'sigmoid': sigmoid,
                   'swish': swish}
    activation_function = activations[activation] if activation in activations \
        else random.choice(list(activations.values()))
    return activation_function
