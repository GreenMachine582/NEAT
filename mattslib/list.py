import logging

__version__ = '1.2.3'
__date__ = '1/05/2022'


def condense(array: list, condensed_array: list = None, depth: int = 0, max_depth: int = 0) -> list:
    """
    Condenses a given array by joining inner lists.
    :param array: list[Any]
    :param condensed_array: list[Any]
    :param depth: int
    :param max_depth: int
    :return:
        - condensed_array - list[Any]
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


def findMaxMin(array: list = None) -> dict:
    """
    Finds the maximum and minimum values and indexes by searching
    the array list linearly.
    :param array: list
    :return:
        - max_min - dict[str: dict[str: Any | int]]
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


def difference(array_a: list, array_b: list) -> list:
    """
    Calculates the differences between two given values.
    :param array_a: list[int | float]
    :param array_b: list[int | float]
    :return:
        - differences - list[int | float]
    """
    differences = []
    if len(array_a) == len(array_b):
        for i in zip(array_a, array_b):
            differences.append(i[0] - i[1])
    return differences


def normalize(array: list = None) -> list:
    """
    Normalizes the values using feature scaling to a value
    between 0 and 1.
    :param array: list
    :return:
        - array - list
    """
    max_value, min_value = max(array), min(array)
    for i, value in enumerate(array):
        try:
            array[i] = (value - min_value) / (max_value - min_value)
        except ZeroDivisionError:
            array[i] = 0
    return array

