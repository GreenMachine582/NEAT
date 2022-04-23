from __future__ import annotations

import logging
import math

__version__ = '1.2.2'
__date__ = '23/04/2022'


def absolute(x: float) -> float:
    return abs(x)


def binaryStep(x: float) -> int:
    return 1 if x >= 0 else 0


def clamped(x: float) -> float:
    return max(-1.0, min(1.0, x))


def identity(x: float) -> float:
    return x


def log(x: float) -> float:
    return math.log(max(1e-7, x))


def tanh(x: float) -> float:
    return math.tanh(max(-60.0, min(60.0, 2.5 * x)))


def leakyReLU(x: float) -> float:
    return x if x > 0 else 0.01 * x


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-max(-60.0, min(60.0, 5 * x))))


def swish(x: float) -> float:
    return x * sigmoid(x)


def mean(array: list = None) -> int | float:
    try:
        return sum(array) / len(array)
    except Exception as e:
        logging.exception(e)


def euclideanDistance(x_array: Any, y_array: Any) -> float:
    try:
        if isinstance(x_array, (int, float)) and isinstance(y_array, (int, float)):
            return math.sqrt((y_array - x_array) ** 2)
        elif isinstance(x_array, (list, tuple)) and isinstance(y_array, (list, tuple)):
            return math.sqrt(sum([(y - x) ** 2 for x, y in zip(x_array, y_array)]))
    except Exception as e:
        logging.exception(e)


def brayCurtisIndividualDistance(x_array: Any, y_array: Any) -> float:
    try:
        if isinstance(x_array, (int, float)) and isinstance(y_array, (int, float)):
            return 1 - 2 * (min(x_array, y_array) / (x_array + y_array))
        elif isinstance(x_array, (list, tuple)) and isinstance(y_array, (list, tuple)):
            min_sum = sum([min(x, y) for x, y in zip(x_array, y_array)])
            return 1 - 2 * (min_sum / (sum(x_array) + sum(y_array)))
    except ZeroDivisionError:
        return 0
    except Exception as e:
        logging.exception(e)
