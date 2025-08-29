from os.path import dirname, join, realpath
from textwrap import dedent


def _fpath() -> str:
    this_file_dir = dirname(realpath(__file__))
    return join(this_file_dir, "message_text.txt")


def get_wellcome_message_text():
    with open(_fpath(), encoding='UTF-8') as f:
        return dedent(f.read())
