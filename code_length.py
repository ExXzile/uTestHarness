
import math

'''
- only lines between (def "your_function_name") and (return 'answer') will be counted
  however, it will still count towards the score if "return" line
  is longer than 72 chars.

- lines beginning with '#' will be ignored

- blank lines will be ignored

- 1 char lines will be ignored.. e.g. to account for closing/opening brackets
  or parenthesises

- lines longer than 72 characters will add up as up-rounded multiples of that number
  to the rating score.. 'cause PEP8
'''


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
