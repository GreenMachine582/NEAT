import logging

__version__ = '1.2'
__date__ = '17/03/2022'


def countOccurrence(array=None):
    try:
        categories = {}
        for n in array:
            if n not in categories:
                categories[n] = 1
            else:
                categories[n] += 1
        return categories
    except Exception as e:
        logging.exception(e)


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


def sortIntoDict(array, sort_with=None):
    list_to_dict = {}
    for key in range(len(sort_with)):
        if sort_with[key] not in list_to_dict:
            list_to_dict[sort_with[key]] = []
        list_to_dict[sort_with[key]].append(array[key])
    return list_to_dict


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
