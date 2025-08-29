from os.path import exists
from typing import Callable

from analyst_klondike.features.code.actions import RunAllCodeAction
from analyst_klondike.features.data_context.init_action import InitAction, ReadFileAndAppVersion
from analyst_klondike.features.data_context.json_load.dc import get_quiz_json
from analyst_klondike.features.data_context.selectors import current_file_path, versions
from analyst_klondike.features.message_box.actions import DisplayMessageBoxAction
from analyst_klondike.state.app_dispatch import app_dispatch
from analyst_klondike.state.app_state import select


def open_file(on_opened: Callable[[str | None], None]) -> None:
    # display message if file is not compatible
    fpath, fname = select(current_file_path)
    if not exists(fpath):
        return
    try:
        json_data = get_quiz_json(fpath)
    except Exception:  # pylint: disable=W0718
        app_dispatch(DisplayMessageBoxAction(
            f"Ошибка при открытии файла {fname}"
        ))
        return

    app_dispatch(ReadFileAndAppVersion(json_data))
    v_info = select(versions)
    if v_info.is_file_compatible:
        app_dispatch(InitAction(data=json_data))
        app_dispatch(RunAllCodeAction())
        on_opened(fname)
    else:
        app_dispatch(DisplayMessageBoxAction(
            f"""\
                    Файл можно будет открыть только в приложении версии {v_info.version_in_file}.
                    У вас установлена версия {v_info.app_version}.
                    Закройте приложение и обновите его, написав команду: 
                    [on blue]uv tool upgrade analyst-klondike[on blue]
                """
        ))
