
import math

'''
- small func to truncate long lines for reports:
'''


def rep_line_count(line):
    line = str(line)
    if len(line) > 84:
        return f'{line[:84]} <<truncated>>'
    else:
        return line


'''
- user submitted func lines count, returns merit report:

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


def code_line_count(func, user_funcs, merit):
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

    merit_report = (
        f'\n'
        f'\n      Code length: {count}'
        f'\nCode length Merit: {merit}'
        f'\n       Merit Pass: '
    )

    if count <= merit:
        merit_report += '✓'
    else:
        merit_report += '✗'

    return merit_report
