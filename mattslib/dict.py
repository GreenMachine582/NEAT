import logging

__version__ = '1.1'
__date__ = '14/03/2022'


def sortByValues(array=None):
    try:
        sorted_dict = {}
        for item_key in array:
            if array[item_key] not in sorted_dict:
                sorted_dict[array[item_key]] = []
            sorted_dict[array[item_key]].append(item_key)
        return sorted_dict
    except Exception as e:
        logging.exception(e)


def removeKeys(array=None, remove=None):
    if remove is None:
        remove = []
    try:
        sorted_dict = {}
        for item_key in array:
            if array[item_key] != remove:
                sorted_dict[item_key] = array[item_key]
        return sorted_dict
    except Exception as e:
        logging.exception(e)
