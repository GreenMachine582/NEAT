import logging

__version__ = '1.2.1'
__date__ = '19/03/2022'


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
