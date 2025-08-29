from __future__ import annotations
from os.path import basename
from typing import Any

from textual import on
from textual.message import Message
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import (
    Header,
    Footer
)
from textual.binding import Binding

# message box
from analyst_klondike.features.app.open_file_action import open_file
from analyst_klondike.features.code.selector import has_failed_cases
from analyst_klondike.features.code_import.ui_actions.import_task_from_code import (
    import_task_action
)
from analyst_klondike.features.code_import.ui_actions.selectors import select_is_in_teacher_mode
from analyst_klondike.features.data_context.data_state import PythonQuizState, PythonTaskState
from analyst_klondike.features.events.event_hook import send_event
from analyst_klondike.features.message_box.ui.mb_screen import MessageBoxScreen

# dispatch and state
from analyst_klondike.features.data_context.set_opened_file_action import SetOpenedFileAction
from analyst_klondike.features.update.display_has_later_version import display_message_if_outdated
from analyst_klondike.state.app_dispatch import app_dispatch
from analyst_klondike.state.app_state import (
    AppState,
    get_state,
    select)

# selectors
from analyst_klondike.features.current.selectors import (
    select_current_quiz,
    select_current_task,
    select_has_file_openned
)

# actions
from analyst_klondike.features.app.actions import EditorScreenReadyAction
from analyst_klondike.features.code.actions import (
    RunCodeAndSetResultsAction,
    UpdateCodeAction)
from analyst_klondike.features.current.actions import (
    MakeQuizCurrentAction,
    MakeTaskCurrentAction
)
from analyst_klondike.features.code_explorer.code_explorer_reducer import (
    QuizNodeCollapseAction,
    QuizNodeExpandAction
)
from analyst_klondike.features.data_context.save_action import save_to_yaml

from analyst_klondike.features.message_box.actions import (
    DisplayMessageBoxAction,
    HideMessageBoxAction)


# components
from analyst_klondike.state.selectors import select_task_by_id
from analyst_klondike.ui.editor_screen.components.code_editor import CodeEditor
from analyst_klondike.ui.editor_screen.components.current_task import CurrentTaskInfo
from analyst_klondike.ui.editor_screen.components.explorer import Explorer
from analyst_klondike.ui.editor_screen.components.quiz_description import QuizDescription
from analyst_klondike.ui.editor_screen.components.test_results import TestResults
from analyst_klondike.ui.file_screen.open_file_screen import OpenFileScreen

# other
from analyst_klondike.features.wellcome_message import get_wellcome_message_text


_WELLCOME_MESSAGE = get_wellcome_message_text()


class EditorScreen(Screen[Any]):
    CSS_PATH = "editor.tcss"

    open_file_binding = Binding(id="open_file",
                                key='ctrl+o',
                                action='open_quiz_file',
                                description="Открыть тест",
                                tooltip="Открыть файл с задачами. " +
                                "Вам нужно будет написать код, который пройдет все тесты")

    run_code_binding = Binding(id="run_code",
                               key='f5, ctrl+r',
                               action='run_btn_click',
                               description="Запустить код")

    save_file_binding = Binding(id="save_file",
                                key="ctrl+s",
                                action="save_quiz_to_file",
                                description="Сохранить")

    display_help_binding = Binding(id="display_help",
                                   key="f1",
                                   action="display_help",
                                   description="Справка",
                                   tooltip="Отобразить справку")

    import_tasks_binding = Binding(
        id="import_tasks_from_code",
        key="f2",
        action="import_tasks_from_code",
        description="Импортировать задачи",
        tooltip="Создать новый файл с задачами и поместить его в текущий каталог"
    )

    MSG_BOX_SCREEN_ID = "message_box_screen"

    BINDINGS = [
        display_help_binding,
        open_file_binding,
        save_file_binding,
        run_code_binding,
        import_tasks_binding
    ]

    class UpdateAppTitleMessage(Message):
        def __init__(self, title: str, subtitle: str) -> None:
            super().__init__()
            self.title = title
            self.subtitle = subtitle

    class RequestOpenFileScreen(Message):
        pass

    def _notify_opened(self, fname: str | None) -> None:
        if fname is None:
            return
        self.app.notify(
            "Загружено",
            title=fname,
            severity="information",
            timeout=1
        )

    async def on_mount(self) -> None:
        app_dispatch(EditorScreenReadyAction())
        app_dispatch(DisplayMessageBoxAction(_WELLCOME_MESSAGE))
        open_file(self._notify_opened)
        send_event("app_opened", "/")
        display_message_if_outdated()

    def update_view(self, new_state: AppState):
        if not new_state.is_editor_screen_ready:
            return
        explorer = self.query_one("Explorer", Explorer)
        code_editor = self.query_one("CodeEditor", CodeEditor)
        task_info = self.query_one("CurrentTaskInfo", CurrentTaskInfo)
        test_results = self.query_one("TestResults", TestResults)
        quiz_description = self.query_one("QuizDescription", QuizDescription)

        explorer.state = new_state
        code_editor.state = new_state
        task_info.state = new_state
        test_results.update_view(new_state)
        quiz_description.state = new_state

        # send message to update title and subtitle
        self.post_message(EditorScreen.UpdateAppTitleMessage(
            new_state.current.app_title,
            new_state.current.app_subtitle
        ))
        # update component visibility
        if new_state.current.object_name == "task":
            code_editor.remove_class("component-hidden")
            quiz_description.add_class("component-hidden")
        elif new_state.current.object_name == "quiz":
            code_editor.add_class("component-hidden")
            quiz_description.remove_class("component-hidden")
        elif new_state.current.object_name == "account":
            pass

        self._display_message_box(new_state)
        # refresh visibility/enable status for footer buttons
        self.refresh_bindings()

    def _display_message_box(self, state: AppState) -> None:
        current_screen_id = self.app.screen_stack[-1].id

        # display message box:
        if state.message_box.is_visible:
            if current_screen_id != EditorScreen.MSG_BOX_SCREEN_ID:
                self.app.push_screen(
                    MessageBoxScreen(
                        id=EditorScreen.MSG_BOX_SCREEN_ID),
                    EditorScreen._on_message_box_close
                )
        else:
            if current_screen_id == EditorScreen.MSG_BOX_SCREEN_ID:
                self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="left_panel"):
            yield Explorer()
            yield CurrentTaskInfo()
        with Vertical(id="right_panel"):
            yield CodeEditor()
            yield QuizDescription(classes="component-hidden")
            yield TestResults()

    @on(Explorer.TaskSelected)
    def on_python_task_selected(self, ev: Explorer.TaskSelected) -> None:
        if isinstance(ev.task_id, int):
            app_dispatch(MakeTaskCurrentAction(ev.task_id))
            selected_task = select_task_by_id(get_state(), ev.task_id)
            send_event("python_task_selected", "/",
                       event_json={
                           'id': str(ev.task_id),
                           'title': selected_task.title
                       })

    @on(Explorer.QuizSelected)
    def on_quiz_selected(self, ev: Explorer.QuizSelected) -> None:
        app_dispatch(MakeQuizCurrentAction(quiz_id=ev.quiz_id))

    @on(Explorer.QuizNodeExpandedOrCollapsed)
    def on_quiz_node_expanded_collapsed(self, ev: Explorer.QuizNodeExpandedOrCollapsed) -> None:
        if ev.action_type == "expanded":
            app_dispatch(QuizNodeExpandAction(quiz_id=ev.quiz_id))
        elif ev.action_type == "collapsed":
            app_dispatch(QuizNodeCollapseAction(quiz_id=ev.quiz_id))

    @on(CodeEditor.CodeUpdated)
    def on_editor_code_updated(self, ev: CodeEditor.CodeUpdated) -> None:
        app_dispatch(UpdateCodeAction(ev.code))

    def action_run_btn_click(self) -> None:
        app_dispatch(RunCodeAndSetResultsAction())
        is_failed = select(has_failed_cases)
        selected_task: PythonTaskState = select(select_current_task)
        send_event("run_code", "/", event_json={
            'is_passed': not is_failed,
            'task_id': selected_task.id,
            'task_title': selected_task.title
        })

    def action_open_quiz_file(self) -> None:
        def _on_file_selected(file_path: str | None) -> None:
            if not isinstance(self.app.screen, EditorScreen):
                return
            if file_path is None or file_path == '':
                return

            app_dispatch(SetOpenedFileAction(
                opened_file_name=basename(file_path),
                opened_file_path=file_path
            ))
            open_file(self._notify_opened)

        self.app.push_screen(OpenFileScreen(), _on_file_selected)

    def action_save_quiz_to_file(self) -> None:
        state = get_state()
        save_to_yaml(state, self.app)

    def action_display_help(self) -> None:
        app_dispatch(DisplayMessageBoxAction(_WELLCOME_MESSAGE))

    def action_import_tasks_from_code(self) -> None:
        curr_quiz = select(select_current_quiz)

        def _on_file_selected(file_path: str | None) -> None:
            if file_path is None:
                return
            if curr_quiz is None:
                self.app.notify(
                    "Необходимо выбрать тест для импортирования",
                    title="Импортирование",
                    severity="error",
                    timeout=1
                )
            assert isinstance(curr_quiz, PythonQuizState)
            import_task_action(curr_quiz.id, file_path)
        if curr_quiz is not None:
            self.app.push_screen(OpenFileScreen(), _on_file_selected)
        else:
            app_dispatch(DisplayMessageBoxAction(
                message="Необходимо выбрать тест куда импортировать задачи"))

    def check_action(self, action: str, parameters: tuple[object, ...]):
        if action == EditorScreen.run_code_binding.action:
            curr_task = select(select_current_task)
            if curr_task is not None:
                return True
            return None
        if action == EditorScreen.save_file_binding.action:
            has_file = select(select_has_file_openned)
            if has_file:
                return True
            return None
        if action == EditorScreen.import_tasks_binding.action:
            is_teacher_mode = select(select_is_in_teacher_mode)
            if not is_teacher_mode:
                return False
            curr_quiz = select(select_current_quiz)
            if curr_quiz is not None:
                return True
            return None
        return True

    @staticmethod
    def _on_message_box_close(_: bool | None) -> None:
        app_dispatch(HideMessageBoxAction())
