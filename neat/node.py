
__file__ = 'node'
__version__ = '1.2'
__date__ = '02/03/2022'


class Node(object):
    def __init__(self, activation):
        self.activation = activation
        self.output = 0
        self.bias = 0
