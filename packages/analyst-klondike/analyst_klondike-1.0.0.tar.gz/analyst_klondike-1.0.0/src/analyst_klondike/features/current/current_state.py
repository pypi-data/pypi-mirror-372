from dataclasses import dataclass
from typing import Literal


@dataclass
class CurrentState:
    task_id: int | None = None
    quiz_id: str | None = None
    app_title: str = "Клондайк аналитика"
    app_subtitle: str = ""
    # название выбранного объекта
    object_name: Literal["quiz", "task", "account"] | None = None
    # file full path
    opened_file_path: str = ""
    # just file name
    opened_file_name: str = ""
    # just opened file min required version
    opened_file_min_supported_app_version: str = ""
    app_version: str = ""
