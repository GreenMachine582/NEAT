from __future__ import annotations

import json
import logging
import pickle

__version__ = '1.2.2'
__date__ = '19/03/2022'


def read(file_dir: str = '') -> Any | None:
    """
    Reads the given file and checks the extension to
    determine a fit loading method.
    :param file_dir: str
    :return:
        - contents - Any | None
    """
    try:
        if ".txt" in file_dir:
            with open(file_dir, 'r') as file:
                contents = file.readlines()
        elif ".json" in file_dir:
            with open(file_dir, 'r') as file:
                contents = json.load(file)
        else:
            with open(file_dir, 'rb') as file:
                contents = pickle.load(file)
        return contents
    except Exception as e:
        logging.exception(e)
    return None


def write(contents: Any = None, file_dir: str = '') -> None:
    """
    Writes the contents to file and checks extension
    to determine a fit writing method.
    :param contents: Any
    :param file_dir: str
    :return:
        - None
    """
    if contents is None:
        contents = []
    try:
        if ".txt" in file_dir:
            with open(file_dir, 'w') as file:
                file.writelines(contents)
        elif ".json" in file_dir:
            with open(file_dir, 'w') as file:
                if not isinstance(contents, dict):
                    json.dump(contents.__dict__, file)
                else:
                    json.dump(contents, file, indent=4)
        else:
            with open(file_dir, 'wb') as file:
                pickle.dump(contents, file, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logging.exception(e)
