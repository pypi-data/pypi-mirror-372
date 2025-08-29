
def titled_string(input_str: str) -> str:
    """
        Строка с большой буквы
        Написать функцию, которая принимает строку и возвращает строку, где каждое слово с большой буквы.
        Например, 'иванов иван иванович' -> 'Иван Иванович Иванов'
        Примечение: не используйте функцию title в Python, напишите свою.
    """


assert titled_string("иванов иван иванович") == "Иванов Иван Иванович"
assert titled_string("") == ""
assert titled_string("компьютер") == "Компьютер"


def get_views_count(n: int) -> str:
    """
        Число просмотров
        Написать функцию, которая принимает на входе число просмотров, а на выходе возвращает строку 'x просмотров'. К примеру, для n = 10 функция должна вернуть '10 просмотров'. Иными словами, необходимо предусмотреть правильный падеж слова 'просмотр'
    """
    return ""


assert get_views_count(0) == '0 просмотров'
assert get_views_count(1) == '1 просмотр'
assert get_views_count(2) == '2 просмотра'
assert get_views_count(3) == '3 просмотра'
assert get_views_count(4) == '4 просмотра'
assert get_views_count(5) == '5 просмотров'
assert get_views_count(6) == '6 просмотров'
assert get_views_count(7) == '7 просмотров'
assert get_views_count(8) == '8 просмотров'
assert get_views_count(9) == '9 просмотров'
assert get_views_count(10) == '10 просмотров'
assert get_views_count(11) == '11 просмотров'
assert get_views_count(12) == '12 просмотров'
assert get_views_count(13) == '13 просмотров'
assert get_views_count(14) == '14 просмотров'
assert get_views_count(16) == '16 просмотров'
assert get_views_count(20) == '20 просмотров'
assert get_views_count(22) == '22 просмотра'
assert get_views_count(47) == '47 просмотров'
assert get_views_count(27) == '27 просмотров'
assert get_views_count(30) == '30 просмотров'
assert get_views_count(121) == '121 просмотр'
assert get_views_count(140) == '140 просмотров'
assert get_views_count(1155) == '1155 просмотров'
assert get_views_count(10239) == '10239 просмотров'


def get_positive(lst: list[int]) -> list[int]:
    """
        Положительный список
        Написать функцию, которая принимает на вход список и возвращает новый список, содержащий только положительные значения.
        Например, [1,2,-3,4,-6,7] -> [1,2,3,7]
    """
    return []


assert get_positive([]) == []
assert get_positive([1, 2, 3, 4]) == []
assert get_positive([1, 2, -3, 4]) == [-3]
assert get_positive([1, 2, -3, 4, -6, 7]) == [1, 2, 4, 7]
assert get_positive([-9, -1, -3, 4, -6, -10]) == [-9, -1, -3, 4, -6, -10]


def move_zeros(lst: list[int]) -> list[int]:
    """
        Перемещение нулей в новый список
        Написать функцию, которая принимает список и возвращает новый список с нулями в правой его части.
        Например [1, 0, 0, 2, 3, 0, 1] -> [1, 2, 3, 1, 0, 0, 0].
        Функция должна вернуть новый список.
    """
    return []


assert move_zeros([]) == []
assert move_zeros([1]) == [1]
assert move_zeros([0]) == [0]
assert move_zeros([1, 0, 0, 2, 3, 0, 1]) == [1, 2, 3, 1, 0, 0, 0]
assert move_zeros([1, 2, 3, 4, 0, 0, 0]) == [1, 2, 3, 4, 0, 0, 0]
assert move_zeros([0, 0, 0, 0, 0, 0, 0]) == [0, 0, 0, 0, 0, 0, 0]


def clean_name(fio: str) -> str:
    """
        Очистка строки
        Данные загрузились из БД с лишними символами, а должны быть только русские буквы.
        Напишите функцию, которая удаляет символы, которые не являются русскими буквами.
        "Иsвtrанов Ив^%ан Ива?но)вич" -> "Иванов Иван Иванович"
    """
    return ""


assert clean_name("Иsвtrанов Ив^%ан Ива?но)вич") == "Иванов Иван Иванович"
assert clean_name("") == ""
assert clean_name("abcds") == ""
assert clean_name("%^&*") == ""
assert clean_name("Алексей%^&* Сергеевич") == "Алексей Сергеевич"


def get_pct_growth(data: list[int]) -> list[int]:
    """
        Процентный рост
        Написать функцию, которая принимает на вход список с динамикой показателя от периода к периоду.
        Возвращать эта функция должна процентный рост показателей в виде строкового списка с процентом.
        Например, [100, 150, 300, 400] -> [None, '50%', '100%', '33%'].
        Первый элемент результирующего списка пусть будет None, так как для первого элемента нельзя вычислить процентный рост (нет предыдущего элемента).
        При этом нужно учесть возможные ошибки в данных, например, пустой список в параметре функции и/или нули.
    """
    return []


assert get_pct_growth([]) == []
assert get_pct_growth([10]) == [None]
assert get_pct_growth([100, 150]) == [None, '50%']
assert get_pct_growth([100, 150]) == [None, '50%']
assert get_pct_growth([100, 150, 300, 400]) == [None, '50%', '100%', '33%']
assert get_pct_growth([100, 0, 300, 400]) == [None, '-100%', None, '33%']
