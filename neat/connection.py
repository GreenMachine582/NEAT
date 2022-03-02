
__file__ = 'connection'
__version__ = '1.2'
__date__ = '02/03/2022'


class Connection(object):
    def __init__(self, weight):
        self.weight = weight
        self.active = True
