import logging

__version__ = '1.1'
__date__ = '18/03/2022'


def mean(array=None):
    try:
        return sum(array) / len(array)
    except Exception as e:
        logging.exception(e)
