from textwrap import dedent

from analyst_klondike.features.code.wrap_func import inline_code


def test_inline_function():
    code_func = """\
        def solution(s: str) -> str:
            return "".join(reversed(s.split()))
    """
    expected_res = dedent("""\
        def solution_wrapper():

            def solution(s: str) -> str:
                return "".join(reversed(s.split()))
            
            return solution
        """)
    print("Expected:")
    print(expected_res)
    actual_res = inline_code(code_func)
    print("Actual")
    print(actual_res)
    assert actual_res == expected_res
