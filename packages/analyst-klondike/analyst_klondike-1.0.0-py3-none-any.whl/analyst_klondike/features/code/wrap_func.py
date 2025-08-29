from textwrap import dedent


def inline_code(code_func: str) -> str:
    code_wrapper = """\
        def solution_wrapper():

            {code_func}

            return solution
        """
    # ко второй строке и далее долбавляем один таб
    code_func_lines = dedent(code_func).split('\n')
    code_wrapper_lines = dedent(code_wrapper).split('\n')
    res_lines: list[str] = []
    for line in code_wrapper_lines:
        if line.strip() == "{code_func}":
            for func_line in code_func_lines:
                res_lines.append("\t" + func_line)
        else:
            res_lines.append(line)

    return "\n".join(res_lines)
