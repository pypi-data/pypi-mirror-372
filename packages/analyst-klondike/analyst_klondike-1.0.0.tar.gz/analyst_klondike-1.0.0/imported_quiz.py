def sum_values(a: int, b: int) -> int:
    '''
        Сумма двух значений
        Написать функцию, которая суммирует два числа.
        При этом нужно использовать только стандартные конструкции Python.
    '''
    return 1


assert sum_values(1, 1) == 2
assert sum_values(10, 15) == 25
assert sum_values(-7, 3) == -4


def compare_lists(lst1: list[int], lst2: list[int]) -> bool:
    '''
        Сравнение двух списков
        Написать функцию, которая сравнивает два массива.
    '''
    return True


assert compare_lists([1, 2, 3], [1, 2, 3]) == True
assert compare_lists([1, 2, 3], [1, 2, 3]) == True
assert compare_lists([5, 6, 7], [5, 6, 7, 8]) == False
