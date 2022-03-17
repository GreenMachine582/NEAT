from __future__ import annotations

__version__ = '1.4.1'
__date__ = '17/03/2022'


class Node(object):
    """
    Contains key information about the node.
    """
    def __init__(self, layer_type: str, activation: Any):
        """
        Initiates the Node object with default and given values.
        :param layer_type: str
        :param activation: (x: int | float) -> int | float
        """
        self.layer_type = layer_type
        self.activation = activation
        self.depth = 0
        self.output = 0
        self.bias = 0
        self.backtrack = 0
