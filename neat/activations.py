from __future__ import annotations

import math
import random

from mattslib import math_util

__version__ = '1.5.1'
__date__ = '19/03/2022'


def getActivation(activation: str = '') -> activation_function:
    """
    Returns the requested or a random activation function.
    :param activation: str
    :return:
        - activation_function - (x: int | float) -> int | float
    """
    activations = {'absolute': math_util.absolute,
                   'binaryStep': math_util.binaryStep,
                   'clamped': math_util.clamped,
                   'identity': math_util.identity,
                   'log': math_util.log,
                   'tanh': math_util.tanh,
                   'leakyReLU': math_util.leakyReLU,
                   'sigmoid': math_util.sigmoid,
                   'swish': math_util.swish}
    activation_function = activations[activation] if activation in activations \
        else random.choice(list(activations.values()))
    return activation_function
