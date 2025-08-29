from textwrap import dedent

from analyst_klondike.features.code_import.analysis.code_analysis import create_quiz_from_code


def test_code_analysis() -> None:
    code = dedent("""\
        def sum_values(a: int, b: int) -> int:
            '''
                Сумма двух значений
                Написать функцию, которая суммирует два числа.
                При этом нужно использовать только стандартные конструкции Python.
            '''
            return 1


        assert sum_values(1, 1) == 2
        assert sum_values(10, 15) == 25
        assert sum_values(-7, 3) == 4


        def compare_lists(lst1: list[int], lst2: list[int]) -> bool:
            '''
                Сравнение двух списков
                Написать функцию, которая сравнивает два массива.
            '''
            return True


        assert compare_lists([1, 2, 3], [1, 2, 3]) == True
        assert compare_lists([1, 2, 3], [1, 2, 3]) == True
        assert compare_lists([5, 6, 7], [5, 6, 7, 8]) == False
    """)
    quiz_state = create_quiz_from_code("python_quiz", code)
    print(quiz_state)


def test_negative_numbers_in_asserts():
    code = dedent("""\
        def sum_values(a: int, b: int) -> int:
            '''
                Сумма двух значений
                Написать функцию, которая суммирует два числа.
                При этом нужно использовать только стандартные конструкции Python.
            '''
            return 1
                          
        assert sum_values(-10, -15) == -25
        assert sum_values(1, 1) == 2
        assert sum_values(-7, 3) == 4
           
    """)
    quiz_state = create_quiz_from_code("python_quiz", code)
    print(quiz_state)


def test_false_in_asserts():
    code = dedent("""\
                 
        def compare_lists(lst1: list[int], lst2: list[int]) -> bool:
            '''
                Написать функцию, которая сравнивает два массива.
            '''
            return True

        assert compare_lists([1,2,3], [1,2,3,4]) == False      
        assert compare_lists([1,2,3], [1,2,3]) == True
           
    """)
    quiz_state = create_quiz_from_code("python_quiz", code)
    print(quiz_state)
