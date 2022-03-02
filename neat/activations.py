import math
import random


def absolute(x):
    return abs(x)


def binaryStep(x):
    return 1 if x >= 0 else 0


def clamped(x):
    return max(-1.0, min(1.0, x))


def identity(x):
    return x


def log(x):
    x = max(1e-7, x)
    return math.log(x)


def tanh(x):
    x = max(-60.0, min(60.0, 2.5 * x))
    return math.tanh(x)


def leakyReLU(x):
    return x if x > 0 else 0.01 * x


def sigmoid(x):
    x = max(-60.0, min(60.0, 5 * x))
    return 1 / (1 + math.exp(-x))


def swish(x):
    return x * sigmoid(x)


def getActivation(activation=''):
    activations = {'absolute': absolute,
                   'binaryStep': binaryStep,
                   'clamped': clamped,
                   'identity': identity,
                   'log': log,
                   'tanh': tanh,
                   'leakyReLU': leakyReLU,
                   'sigmoid': sigmoid,
                   'swish': swish}
    if activation in activations:
        return activations[activation]
    else:
        return random.choice(list(activations.values()))
