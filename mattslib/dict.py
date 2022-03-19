from __future__ import annotations

import logging

__version__ = '1.2.1'
__date__ = '19/03/2022'


def countOccurrence(array: list = None) -> dict:
    """
    Counts the occurrence of items from array.
    :param array: list[Any]
    :return:
        - categories - dict[Any: int]
    """
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


def combineByValues(array: dict = None) -> dict:
    """
    Combines certain keys by the given array values, producing
    inverted dict.
    :param array: dict[Any: Any]
    :return:
        - sorted_dict - dict[Any: list[Any]]
    """
    try:
        sorted_dict = {}
        for item_key in array:
            if array[item_key] not in sorted_dict:
                sorted_dict[array[item_key]] = []
            sorted_dict[array[item_key]].append(item_key)
        return sorted_dict
    except Exception as e:
        logging.exception(e)


def sortIntoDict(array: list, sort_with: list = None) -> dict:
    """
    Creates a sorted dict with given keys and array values.
    :param array: list[Any]
    :param sort_with: list[Any]
    :return:
        - lists_to_dict - dict[Any: list[Any]
    """
    lists_to_dict = {}
    for key in range(len(sort_with)):
        if sort_with[key] not in lists_to_dict:
            lists_to_dict[sort_with[key]] = []
        lists_to_dict[sort_with[key]].append(array[key])
    return lists_to_dict


def removeKeys(array: dict = None, remove: Any = None) -> dict:
    """
    Removes keys from array by given remove value.
    :param array: dict[Any: Any]
    :param remove: Any
    :return:
        - sorted_dict - dict[Any: Any]
    """
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
