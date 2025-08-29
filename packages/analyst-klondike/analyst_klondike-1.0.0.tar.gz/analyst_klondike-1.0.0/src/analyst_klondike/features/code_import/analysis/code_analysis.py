import ast
from ast import (
    Assert,
    Call,
    Compare,
    Constant,
    Expr,
    FunctionDef,
    List,
    Module,
    Name,
    Return,
    Subscript,
    USub,
    UnaryOp,
    arg,
    arguments,
    expr,
    stmt
)
from dataclasses import dataclass
from typing import Any

from analyst_klondike.features.data_context.data_state import (
    PythonTaskState,
    TestCaseState,
    VariableState
)


@dataclass
class ParsedFunctionInfo:
    title: str
    description: str
    params: dict[str, str]
    return_type: str
    template: str


@dataclass
class FuncTitleAndDesc:
    title: str
    descr: str


def create_quiz_from_code(quiz_id: str, code: str) -> list[PythonTaskState]:

    tree = ast.parse(code)
    functions: dict[str, ParsedFunctionInfo] = {}
    for b in tree.body:
        if isinstance(b, FunctionDef):
            function_name = _get_function_name(b)
            title_descr = _get_title_and_descr(b)
            p = _get_function_params(b)
            func_return_type = _get_function_return_type(b)
            func_template = _get_function_template(
                p, func_return_type
            )
            functions[function_name] = ParsedFunctionInfo(
                title=title_descr.title,
                description=title_descr.descr,
                params=p,
                return_type=func_return_type,
                template=func_template,
            )
    test_cases = _get_all_test_cases(tree, functions)

    python_tasks = _create_python_tasks(
        quiz_id, functions, test_cases
    )

    return python_tasks


def _create_python_tasks(quiz_id: str,
                         functions: dict[str, ParsedFunctionInfo],
                         test_cases: dict[str, list[TestCaseState]]) -> list[PythonTaskState]:
    python_tasks: list[PythonTaskState] = []
    last_task_id = 1
    for func_name, p in functions.items():
        python_task = PythonTaskState(
            id=last_task_id,
            title=p.title,
            description=p.description,
            code_template=p.template,
            code=p.template,
            quiz_id=quiz_id,
            test_cases=test_cases[func_name]
        )
        python_tasks.append(python_task)
        last_task_id += 1
    return python_tasks


def _get_function_template(func_params: dict[str, str], ret_type: str) -> str:

    def _get_return_value() -> Any:
        if ret_type == "list":
            return []
        if ret_type == "str":
            return ''
        if ret_type in ("int", "float"):
            return 0
        if ret_type == "bool":
            return True
        if ret_type == "dict":
            return {}
        return None

    func_body: list[stmt] = [
        Return(value=Constant(value=_get_return_value()))
    ]

    func_def = FunctionDef(
        name="solution",
        args=arguments(
            args=[arg(arg=pname,
                      annotation=Name(id=ptype)
                      )
                  for pname, ptype
                  in func_params.items()]
        ),
        body=func_body,
        lineno=1,
        col_offset=0)

    module = Module(body=[func_def])
    code = ast.unparse(module)
    code_with_tabs = code.replace("\n    ", "\n\t")
    return code_with_tabs


def _get_all_test_cases(tree: Module,
                        functions: dict[str, ParsedFunctionInfo]) -> dict[str, list[TestCaseState]]:
    res: dict[str, list[TestCaseState]] = {}
    for b in tree.body:
        if isinstance(b, Assert):
            assert_test_case = _get_test_case(b)
            func_name = assert_test_case.func_name
            func = functions[func_name]
            new_test_case = TestCaseState(
                inputs=[VariableState(
                    param_name=p_name,
                    param_value=p_value,
                    param_type=p_type
                ) for p_value, (p_name, p_type)
                    in zip(assert_test_case.params, func.params.items())],
                expected=VariableState(
                    param_name='expected',
                    param_type=func.return_type,
                    param_value=assert_test_case.expected_value))
            if func_name in res:
                res[func_name].append(new_test_case)
            else:
                res[func_name] = [new_test_case]
    return res


def _get_value(arg: Constant | UnaryOp | expr) -> Any:
    if isinstance(arg, Constant):
        return arg.value
    if isinstance(arg, UnaryOp):
        assert isinstance(arg.operand, Constant)
        assert isinstance(arg.operand.value, (int, float))
        if isinstance(arg.op, USub):
            return - arg.operand.value
        return arg.operand.value
    if isinstance(arg, List):
        res: list[Any] = []
        for e in arg.elts:
            res.append(_get_value(e))
        return res
    raise ValueError(f'Unknown assert call argument {arg}')


@dataclass
class TestCaseFromAssert:
    func_name: str
    expected_value: Any
    params: list[Any]


def _get_test_case(a: Assert) -> TestCaseFromAssert:
    assert isinstance(a.test, Compare)
    assert isinstance(a.test.left, Call)
    assert isinstance(a.test.left.func, Name)
    expected_value = _get_value(a.test.comparators[0])

    called_func = a.test.left.func.id
    func_pos_args = [_get_value(a) for a in a.test.left.args]
    # у нас есть еще и keywords
    return TestCaseFromAssert(
        called_func,
        expected_value,
        func_pos_args
    )


def _get_function_params(func_def: FunctionDef) -> dict[str, str]:
    def _get_type_from_annotation(ann: expr | None) -> str:
        if ann is None:
            return "Any"
        if isinstance(ann, Name):
            return ann.id
        if isinstance(ann, Subscript):
            if isinstance(ann.value, Name):
                return ann.value.id
        return "Any"

    params_dict = {
        arg.arg: _get_type_from_annotation(arg.annotation) for arg in func_def.args.args
    }
    return params_dict


def _get_title_and_descr(func_def: FunctionDef) -> FuncTitleAndDesc:
    def _remove_empty_and_clear(lines: list[str]) -> list[str]:
        return [l.strip() for l in lines if l.strip() != ""]

    doc_string = next(expr for expr in func_def.body)
    assert isinstance(doc_string, Expr)
    assert isinstance(doc_string.value, Constant)
    function_doc_string = doc_string.value
    assert isinstance(function_doc_string.value, str)
    doc_string_lines = _remove_empty_and_clear(
        function_doc_string.value.split('\n')
    )
    if len(doc_string_lines) < 2:
        return FuncTitleAndDesc("", function_doc_string.value)
    title = doc_string_lines[0]
    descr = "\n".join(doc_string_lines[1:])
    return FuncTitleAndDesc(title, descr)


def _get_function_name(func_def: FunctionDef) -> str:
    return func_def.name


def _get_function_return_type(func_def: FunctionDef) -> str:
    ret = func_def.returns
    if isinstance(ret, Subscript):
        if isinstance(ret.value, Name):
            return ret.value.id
    if isinstance(ret, Name):
        return ret.id
    raise ValueError(f'Unknown function return type {ret}')
