
__file__ = 'node'
__version__ = '1.3'
__date__ = '08/03/2022'


class Node(object):
    def __init__(self, activation):
        self.activation = activation
        self.depth = 0
        self.output = 0
        self.bias = 0
        self.backtrack = 0
