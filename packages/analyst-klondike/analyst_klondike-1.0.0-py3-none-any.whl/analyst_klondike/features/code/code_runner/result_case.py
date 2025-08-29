from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterator


class RunResult:

    def __init__(self,
                 all_cases: list[ResultCase],
                 printed_lines: list[str],
                 errors: list[str] | None = None) -> None:
        self._all_cases = all_cases
        self.printed_lines = printed_lines
        self.errors = errors or []

    @staticmethod
    def create_error_result(errors: list[str]) -> RunResult:
        return RunResult([], [], errors)

    @property
    def all_cases(self) -> list[ResultCase]:
        return self._all_cases

    @property
    def passed_cases(self) -> Iterator[ResultCase]:
        return (c for c in self._all_cases if c.passed)

    @property
    def failed_cases(self) -> Iterator[ResultCase]:
        return (c for c in self._all_cases if not c.passed)


@dataclass
class ResultCase:
    func_params: dict[str, Any]
    expected: Any
    actual: Any
    passed: bool
    printed_lines: list[str]
    exception: str | None = None

    def __str__(self) -> str:
        return "OK" if self.passed else self._not_ok()

    def __repr__(self) -> str:
        return self.__str__()

    def _not_ok(self) -> str:
        return f"Failed: expected = {self.expected}, but having {self.actual}"
