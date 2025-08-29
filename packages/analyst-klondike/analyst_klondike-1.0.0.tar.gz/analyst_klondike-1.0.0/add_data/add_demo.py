def get_palindroms(words: list[str]) -> list[list[str] | str]:
    """
        Группировка палиндромов
        Написать функцию, которая группирует слова-палиндромы вместе.
        Например для списка слов ['eat','tea','the','teh','hte','abc','edf'] функция должна вернуть
        [['eat','tea'], ['the','teh','hte'], 'abc','edf']
    """
    return []


assert get_palindroms(['eat', 'tea', 'the', 'teh', 'hte', 'abc', 'edf']) == [
    ['eat', 'tea'], ['the', 'teh', 'hte'], 'abc', 'edf']


def get_substrings(subs: str, long_string: str) -> list[int]:
    """
        Поиск подстрок
        Написать функцию, которая ищет позиции всех вхождений подстроки subs 
        в строке long_string. Номера позиций начинаются с нуля.
        Например подстрока "hello" встречается в строке "hello, world, all people hello"
        два раза: на позиции 0 (начало строки) и 25. Т.е. для этих параметров
        функция вернет спис
    """
    return []


assert get_substrings("abc", "_abc_abc") == [1, 5]
assert get_substrings("hello", "hello world hello") == [0, 12]
