from dataclasses import dataclass
from analyst_klondike.state.base_action import BaseAction


@dataclass
class ChangeThemeAction(BaseAction):
    type = "CHANGE_THEME_ACTION"
    theme: str
    is_dark: bool


@dataclass
class EditorScreenReadyAction(BaseAction):
    type = "EDITOR_SCREEN_READY_ACTION"


@dataclass
class ChangeAppTitleAction(BaseAction):
    type = "CHANGE_APP_TITLE_ACTION"
    title: str
    sub_title: str
