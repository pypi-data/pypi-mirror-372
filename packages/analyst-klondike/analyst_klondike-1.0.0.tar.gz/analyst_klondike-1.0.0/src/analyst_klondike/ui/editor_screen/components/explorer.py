from dataclasses import dataclass
from typing import Literal
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Tree
from textual.containers import Vertical
from textual.reactive import var

from analyst_klondike.features.code.actions import RunAllCodeAction, RunCodeAndSetResultsAction
from analyst_klondike.features.code_import.ui_actions.actions import ImportTasksAction
from analyst_klondike.state.app_state import INITIAL_STATE, AppState
from analyst_klondike.features.data_context.init_action import InitAction
from analyst_klondike.state.selectors import select_tasks_for_quiz


class Explorer(Vertical):

    DEFAULT_CSS = """
        Explorer {
            border: solid $primary;
            height: 1fr;

            Tree {
                background: $background;

                &:focus {
                    background: $background;
                }
            }
        }
    """

    state = var(INITIAL_STATE, init=False)

    @dataclass
    class ExpNodeData:
        node_type: Literal["root", "group", "quiz", "task"]
        object_id: int | str | None = None

    class TaskSelected(Message):
        """Invokes when task is selected, then display it in editor"""

        def __init__(self, task_id: int | str | None) -> None:
            super().__init__()
            self.task_id = task_id

    class QuizSelected(Message):
        """Invokes when quiz is selected"""

        def __init__(self, quiz_id: str) -> None:
            super().__init__()
            self.quiz_id = quiz_id

    class QuizNodeExpandedOrCollapsed(Message):

        def __init__(self,
                     quiz_id: str,
                     action_type: Literal["expanded", "collapsed"]) -> None:
            super().__init__()
            self.quiz_id = quiz_id
            self.action_type = action_type

    def __init__(self) -> None:
        super().__init__()
        self._is_tree_updated = False

    def on_mount(self) -> None:
        self.border_title = "Навигатор"

    def compose(self) -> ComposeResult:
        yield Tree(self.state.user_email, id="tasks")

    @on(Tree.NodeSelected)
    def on_node_selected(self, event: Tree.NodeSelected[ExpNodeData]) -> None:
        node_data = event.node.data
        if node_data is None:
            return
        if node_data.node_type == "task":
            self.post_message(Explorer.TaskSelected(node_data.object_id))
        elif node_data.node_type == "quiz":
            assert isinstance(node_data.object_id, str)
            self.post_message(Explorer.QuizSelected(node_data.object_id))

    def watch_state(self, new_state: AppState) -> None:
        if not new_state.last_action_type in (InitAction.type,
                                              RunCodeAndSetResultsAction.type,
                                              RunAllCodeAction.type,
                                              ImportTasksAction.type):
            return

        tree: Tree[Explorer.ExpNodeData] = self.query_one(  # type: ignore
            "Tree", Tree)
        tree.clear()
        tree.root.label = Text.from_markup(f":id: {new_state.user_email}")
        tree.root.data = Explorer.ExpNodeData(node_type="root")
        quiz_group_node = tree.root.add(Text.from_markup(":open_file_folder: Тесты"),
                                        expand=True,
                                        data=Explorer.ExpNodeData(node_type="group"))

        for quiz in new_state.data.quizes.values():
            quiz_node = quiz_group_node.add(
                label=Text.from_markup(f":books: {quiz.title}"),
                data=Explorer.ExpNodeData(
                    object_id=quiz.id,
                    node_type="quiz"
                ),
                expand=quiz.is_node_expanded)

            for task in select_tasks_for_quiz(new_state, quiz.id):
                task_node_text = self._get_node_text(new_state, task.id)
                quiz_node.add_leaf(task_node_text,
                                   data=Explorer.ExpNodeData(
                                       object_id=task.id,
                                       node_type="task"))

        tree.root.expand()
        self._is_tree_updated = True

    def _get_node_text(self, state: AppState, task_id: int) -> Text:
        task = state.data.tasks[task_id]
        task_run_result = task.is_passed
        if task_run_result == "not_runned":
            return Text.from_markup(f"{task.title}")
        if task_run_result == "passed":
            return Text.from_markup(f":green_circle: {task.title}")
        if task_run_result == "failed":
            return Text.from_markup(f":red_circle: {task.title}")
        return task_run_result.title

    @on(Tree.NodeExpanded)
    def on_tree_node_expanded(self, ev: Tree.NodeExpanded[ExpNodeData]):
        node_data = ev.node.data
        if node_data is None:
            return
        self._set_expanded_collapsed(node_data, "expanded")

    @on(Tree.NodeCollapsed)
    def on_tree_node_collapsed(self, ev: Tree.NodeCollapsed[ExpNodeData]):
        node_data = ev.node.data
        if node_data is None:
            return
        self._set_expanded_collapsed(node_data, "collapsed")

    def _set_expanded_collapsed(self,
                                node_data: ExpNodeData,
                                action: Literal["expanded", "collapsed"]):
        if node_data.node_type == "quiz" and isinstance(node_data.object_id, str):
            quiz_id = node_data.object_id
            self.post_message(Explorer.QuizNodeExpandedOrCollapsed(
                quiz_id=quiz_id,
                action_type=action
            ))
