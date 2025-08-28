
"""
Module for working with text outputs for the SDK
"""

import os

END = '\033[0m'


class formats(object):
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'


class colors(object):
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = FAIL = '\033[91m'
    PURPLE = '\033[95m'


def fmt(
        text: str,
        c: colors = None,
        f: formats = None) -> str:
    """
    Format a piece of text for output to the terminal

    If the env var NO_COLOR is set by the user, we do not add any colors or formats

    :param text: the text to return
    :type text: str
    :param c: An attribute from the `colors` class. If specified, prefixes the str with the relevant
        ANSI code. Defaults to None
    :type c: colors, optional
    :param f: An attribute from the `formats` class. If specified, prefixes the str with the relevant
        ANSI code. Defaults to None, defaults to None
    :type f: formats, optional
    :return: the formatted text. If the env var `NO_COLOR` is set, we just return the given text
    :rtype: str
    """

    rtn_text = text

    # As per https://no-color.org/ we check if the user does not want any colors
    if "NO_COLOR" in os.environ:
        return rtn_text

    if f:
        rtn_text = f"{f}{rtn_text}"

    if c:
        rtn_text = f"{c}{rtn_text}"

    if f or c:
        rtn_text = f"{rtn_text}{END}"

    return rtn_text
