from __future__ import annotations

__version__ = '1.4.1'
__date__ = '17/03/2022'


class Connection(object):
    """
    Contains key information about the connection.
    """
    def __init__(self, weight: int | float):
        """
        Initiates the Connection object with default and given values.
        :param weight: int | float
        """
        self.weight = weight
        self.active = True
