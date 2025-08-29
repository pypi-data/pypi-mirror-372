from dataclasses import dataclass, field
from typing import Literal

PythonTaskResult = Literal["passed", "failed", "not_runned"]


@dataclass
class VariableState:
    param_name: str
    param_type: str
    param_value: str

    def __str__(self) -> str:
        return f"{self.param_name}={self.param_value}({self.param_type})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class TestCaseState:
    inputs: list[VariableState]
    expected: VariableState

    def __str__(self) -> str:
        inps = ",".join(str(s) for s in self.inputs)
        return f"{self.expected}, inputs = {inps}"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class PythonTaskState:
    id: int
    title: str
    description: str
    code_template: str
    code: str
    quiz_id: str
    test_cases: list[TestCaseState] = field(
        default_factory=list[TestCaseState]
    )
    is_passed: PythonTaskResult = "not_runned"


@dataclass
class PythonQuizState:
    id: str
    title: str
    is_node_expanded: bool


@dataclass
class DataState:
    quizes: dict[str, PythonQuizState] = field(
        default_factory=dict[str, PythonQuizState]
    )
    tasks: dict[int, PythonTaskState] = field(
        default_factory=dict[int, PythonTaskState]
    )
