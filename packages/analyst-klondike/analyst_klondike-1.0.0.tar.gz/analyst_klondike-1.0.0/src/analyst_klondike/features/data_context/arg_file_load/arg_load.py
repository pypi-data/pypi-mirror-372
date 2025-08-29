from os import getcwd
from os.path import dirname, join, exists, basename

from analyst_klondike.features.code_import.ui_actions.actions import SwitchToTeacherModeAction
from analyst_klondike.features.data_context.set_opened_file_action import SetOpenedFileAction
from analyst_klondike.features.events.event_actions import DisableEvents
from analyst_klondike.state.app_dispatch import app_dispatch


class TooManyArgumentsException(Exception):
    pass


def process_args(argv: list[str]) -> None:
    if len(argv) < 2:
        return

    python_file_dir = dirname(argv[0])
    cmd = getcwd()
    fpath = _first_existed_path(argv[1:],
                                python_file_dir,
                                cmd)
    if "--no-events" in argv:
        app_dispatch(DisableEvents())
    if "--teacher" in argv:
        app_dispatch(SwitchToTeacherModeAction())
    if fpath is not None:
        fname = basename(fpath)
        app_dispatch(SetOpenedFileAction(
            opened_file_name=fname,
            opened_file_path=fpath
        ))


def _first_existed_path(file_names: list[str], *dirs: str) -> str | None:
    return next((
        join(d, f) for f in file_names for d in dirs if exists(join(d, f))
    ), None)
