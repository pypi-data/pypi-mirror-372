
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ResultCaseState:
    func_params: dict[str, Any]
    expected: str
    actual: str
    passed: bool
    has_exception: bool
    printed_lines: list[str]
    exception_message: str | None


@dataclass
class RunCodeState:
    last_run_dt: datetime = datetime.now()
    last_code: str = ''
    result_cases: list[ResultCaseState] = field(
        default_factory=list["ResultCaseState"]
    )
    has_errors: bool = False
    errors: list[str] = field(default_factory=list[str])
