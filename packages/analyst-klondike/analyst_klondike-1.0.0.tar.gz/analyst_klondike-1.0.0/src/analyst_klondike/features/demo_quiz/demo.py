import os
from analyst_klondike.features.code.actions import RunAllCodeAction
from analyst_klondike.features.data_context.init_action import InitAction
from analyst_klondike.features.data_context.json_load.dc import get_quiz_json
from analyst_klondike.features.data_context.set_opened_file_action import SetOpenedFileAction
from analyst_klondike.features.events.event_hook import send_event
from analyst_klondike.features.message_box.actions import HideMessageBoxAction
from analyst_klondike.state.app_dispatch import app_dispatch


def _demo_file_path() -> str:
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_file_dir, "demo.yaml")


def start_demo_quiz():
    fpath = _demo_file_path()
    app_dispatch(SetOpenedFileAction(
        opened_file_name=os.path.basename(fpath),
        opened_file_path=fpath
    ))

    load_result = get_quiz_json(fpath)

    app_dispatch(InitAction(data=load_result))
    app_dispatch(RunAllCodeAction())
    app_dispatch(HideMessageBoxAction())
    send_event("start_demo_quiz", "/")
