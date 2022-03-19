from __future__ import annotations

import logging
import math

__version__ = '1.2'
__date__ = '19/03/2022'


def absolute(x: int | float) -> int | float:
    return abs(x)


def binaryStep(x: int | float) -> int | float:
    return 1 if x >= 0 else 0


def clamped(x: int | float) -> int | float:
    return max(-1.0, min(1.0, x))


def identity(x: int | float) -> int | float:
    return x


def log(x: int | float) -> int | float:
    return math.log(max(1e-7, x))


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


def mean(array: list = None) -> int | float:
    try:
        return sum(array) / len(array)
    except Exception as e:
        logging.exception(e)
