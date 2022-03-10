import logging

__file__ = 'list'
__version__ = '1.3'
__date__ = '10/03/2022'


def condense(array, condensed_array=None, depth=0, max_depth=0):
    """
    Condenses a given array by removing depth. This is done by checking
    the instance type of items within the array list.
    :param array: list
    :param condensed_array: list
    :param depth: int
    :param max_depth: int
    :return condensed_array: list
    """
    if condensed_array is None or depth == 0:
        condensed_array = []
    try:
        if max_depth == 0 or depth <= max_depth:
            for item in array:
                if isinstance(item, list):
                    condensed_array = condense(item, condensed_array, depth + 1, max_depth)
                else:
                    condensed_array.append(item)
        else:
            condensed_array.append(array)
        return condensed_array
    except Exception as e:
        logging.exception(e)


def findMaxMin(array=None):
    """
    Finds the maximum and minimum values and indexes by searching the
    array list linearly.
    :param array: list
    :return max_min: dict
    """
    try:
        max_min = {"max": {"value": array[0], "index": 0}, "min": {"value": array[0], "index": 0}}
        for i in range(1, len(array)):
            if array[i] > max_min["max"]["value"]:
                max_min["max"]["value"] = array[i]
                max_min["max"]["index"] = i
            if array[i] < max_min["min"]["value"]:
                max_min["min"]["value"] = array[i]
                max_min["min"]["index"] = i
        return max_min
    except Exception as e:
        logging.exception(e)


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


def sortIntoDict(array, sort_with=None):
    list_to_dict = {}
    for key in range(len(sort_with)):
        if sort_with[key] not in list_to_dict:
            list_to_dict[sort_with[key]] = []
        list_to_dict[sort_with[key]].append(array[key])
    return list_to_dict


def mean(array=None):
    return sum(array) / len(array)


def medium(array=None):
    array = sorted(array)
    high = int(len(array)/2)
    low = high - 1
    return ((array[high] - array[low]) / 2) + array[low]
