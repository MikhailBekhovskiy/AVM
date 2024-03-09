# get a number from string
def parse_num(st: str, start: int) -> tuple[float, int]:
    res = ''
    i = start
    while i < len(st) and ((st[i] >= '0' and st[i] <= '9') or st[i] == '.'):
        res += st[i]
        i += 1
    return float(res), i

# get a word from string from start index to stop symbol
def parse_name(st: str, start: int, stop_symbols={'^', '[', ']', ' ', '*'},
               backwards=False) -> tuple[str, int]:
    res = ''
    i = start
    while i < len(st) and st[i] not in stop_symbols:
        if backwards:
            res = st[i] + res
            if i > 0:
                i -= 1
            else:
                break
        else:
            res += st[i]
            i += 1
    return res, i

# check whether string contains function definitions
# function definitions must be followed by []
# (for checking arguments polynomiality)
def poly_check(expr: str) -> bool:
    if '[' in expr:
        return False
    return True

# returns string containing full function expression (with [] and arguments)
def find_simple_func(expr: str, start=0)->str:
    i = start
    func = ''
    while i < len(expr) and expr[i] != '[':
        i += 1
    if expr[i] == '[':
        args = parse_name(expr, i + 1, stop_symbols={']'})
        if poly_check(args[0]):
            func = parse_name(expr, i-1, stop_symbols={' ', '*', '['}, backwards=True)[0]
            func += '[' + args[0] + ']'
        else:
            args = parse_name(expr, args[1] - 1, stop_symbols={'['}, backwards=True)
            func = parse_name(expr, args[1] - 1, stop_symbols={' ', '*', '['}, backwards=True)[0]
            func += '[' + args[0] + ']'
    return func

# returns tuple (func_name, func_args)
def parse_func(func: str) -> tuple[str, str]:
    fname, i = parse_name(func, 0, stop_symbols={'['})
    args = parse_name(func, i + 1, stop_symbols={']'})[0]
    return (fname, args)


if __name__ == "__main__":
    expression = 'y = x1^5 * sin[x2; x3*x4^5 - cos[x3 * ln[x2;x5]]]'
    res = find_simple_func(expression)
    res = parse_func(res)
    print(res)