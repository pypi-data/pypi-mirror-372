# from analyst_klondike.features.code.code_runner.runner import CodeRunner


# _runner_cases: list[dict[str, object]] = [
#     {
#         "n": 1,
#         "expected": "1 просмотр"
#     },
#     {
#         "n": 2,
#         "expected": "2 просмотра"
#     },
#     {
#         "n": 2,
#         "expected": "2 просмотра"
#     },
#     {
#         "n": 3,
#         "expected": "3 просмотра"
#     },
#     {
#         "n": 10,
#         "expected": "10 просмотров"
#     },
#     {
#         "n": 21,
#         "expected": "21 просмотр"
#     }
# ]


# def test_run_code() -> None:
#     code = """\
# def solution(n: int) -> str:
#     view_dict = {
#         1: "1 просмотр",
#         2: "2 просмотра",
#         3: "3 просмотра",
#         4: "4 просмотра",
#     }
#     if n <= 4:
#         return view_dict[n]
#     return f"{n} просмотров"
#     """
#     result = CodeRunner().run_code(_runner_cases, code)
#     assert result is not None
#     assert len(list(result.all_cases)) > 0


# def test_overriding_print() -> None:
#     code = """\

# def solution(n: int) -> str:
#     view_dict = {
#         1: "1 просмотр",
#         2: "2 просмотра",
#         3: "3 просмотра",
#         4: "4 просмотра",
#     }
#     if n <= 4:
#         return view_dict[n]
#     print("hello")
#     print("world")
#     return f"{n} просмотров"
#     """
#     code_runner = CodeRunner()
#     result = code_runner.run_code(_runner_cases, code)
#     assert result is not None
#     assert "hello" in result.printed_lines
#     assert "world" in result.printed_lines


# def test_update_dict():
#     initial_dict = {
#         "a": 1,
#         "b": 2
#     }

#     initial_dict.update({
#         "c": 3,
#         "d": 4
#     })

#     assert "c" in initial_dict
