"""
eprint to print to stderr instead of stdout.
"""

import sys


def eprint(*args, **kwargs):
    red_start = "\033[91m"
    red_end = "\033[0m"
    print(red_start, *args, red_end, file=sys.stderr, **kwargs)
