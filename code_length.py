
import math


def code_line_count(func, user_funcs):
    func_code_lines = []
    func_code_line = []
    for char in user_funcs:
        if char != '\n':
            func_code_line.append(char)
        else:
            func_code_lines.append(''.join(func_code_line))
            func_code_line = []

    count = 0
    break_count = False
    for line in func_code_lines:
        if line:
            line = line.lstrip(' ')
            if func.__name__ in line:
                count = 0
                break_count = True
                continue
            if line[0] == '#':
                continue
            if len(line) > 1:
                line_count = math.ceil(len(line)/72)
                count += line_count
            if 'return' in line and break_count:
                count -= 1
                break

    return count
