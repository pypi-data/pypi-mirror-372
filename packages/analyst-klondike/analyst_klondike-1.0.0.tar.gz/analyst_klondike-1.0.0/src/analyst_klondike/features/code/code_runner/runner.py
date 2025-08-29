# pylint: disable=W0122

from types import CodeType
from copy import copy
import textwrap
from typing import Any, Callable, Iterator

from analyst_klondike.features.code.code_runner.result_case import ResultCase, RunResult
from analyst_klondike.features.data_context.data_state import TestCaseState, VariableState


class CodeRunner:

    class SolutionFuncError(Exception):
        pass

    def __init__(self, function_name: str = "solution") -> None:
        self._function_name = function_name
        self._printed_lines: list[str] = []

    def run_code(self,
                 cases: list[TestCaseState],
                 code: str) -> RunResult:
        printed_lines: list[Any] = []

        cleaned_code = textwrap.dedent(code)
        try:
            compiled_code = CodeRunner._try_compile(cleaned_code,)
            function_to_run = self._try_get_solution_func(
                compiled_code
            )
        except (SyntaxError, NameError) as synt_err:
            return RunResult.create_error_result([str(synt_err)])
        except CodeRunner.SolutionFuncError as func_err:
            return RunResult.create_error_result([str(func_err)])

        result_cases = list(self._run_test_cases(cases, function_to_run))
        distinct_errors = list(
            set(c.exception for c in result_cases if c.exception is not None))

        return RunResult(
            all_cases=result_cases,
            printed_lines=printed_lines,
            errors=distinct_errors)

    def _try_get_solution_func(self,
                               compiled_code: CodeType | None
                               ) -> Callable[..., Any]:
        if compiled_code is None:
            raise ValueError("No code to run")
        loc: dict[str, object] = {}
        exec_globals = copy(globals())
        exec_globals.update({
            'print': self._print
        })
        exec(compiled_code, exec_globals, loc)
        if self._function_name not in loc:
            raise CodeRunner.SolutionFuncError(
                f"No function {self._function_name} in code. You may have accidentally deleted it.")
        function_to_run = loc[self._function_name]
        if not callable(function_to_run):
            raise CodeRunner.SolutionFuncError(
                f"Function {self._function_name} not recognized")
        return function_to_run

    @staticmethod
    def _try_compile(code: str) -> CodeType:
        compile_result = compile(code, '<string>', "exec")
        return compile_result

    def _run_test_cases(self,
                        cases: list[TestCaseState],
                        func: Callable[..., Any]) -> Iterator[ResultCase]:
        for c in cases:
            params = dict(
                (inp.param_name, self._cast(inp))
                for inp in c.inputs if inp.param_name != "expected"
            )

            exp = self._cast(c.expected)
            try:
                self._printed_lines.clear()
                actual = func(**params)
                result_case = ResultCase(
                    func_params=params,
                    expected=exp,
                    actual=actual,
                    passed=str(exp) == str(actual),
                    printed_lines=self._printed_lines[:]
                )
                self._printed_lines.clear()
                yield result_case
            except Exception as ex:
                yield ResultCase(
                    func_params=params,
                    expected=exp,
                    actual=None,
                    passed=False,
                    exception=str(ex),
                    printed_lines=[]
                )

    def _print(self, *args: Any) -> None:
        self._printed_lines.append(" ".join(str(a) for a in args))

    def _cast(self, p: VariableState) -> Any:
        if p.param_type == "int":
            return int(p.param_value)
        if p.param_type == "float":
            return float(p.param_value)
        if p.param_type == "list":
            return p.param_value
        return str(p.param_value)
