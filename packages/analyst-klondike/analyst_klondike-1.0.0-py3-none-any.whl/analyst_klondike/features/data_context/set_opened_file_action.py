from dataclasses import dataclass
from analyst_klondike.state.base_action import BaseAction


@dataclass
class SetOpenedFileAction(BaseAction):
    opened_file_name: str
    opened_file_path: str
    type = "SET_FILE_NAME_FROM_COMMAND_LINE"
