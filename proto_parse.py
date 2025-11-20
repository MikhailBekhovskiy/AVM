# new version of parsing base on notations and tree

binary_ops = {'*', '+', '-', '/', '^'}
unary_ops = {'u-'}
delim = {';', ','}
parenth = {'(', ')', '[', ']'}
priorities = {
    '+': 0,
    '-': 0,
    'u-': 1,
    '*': 2,
    '/': 2,
    '^': 3
}

# check if token is numeric
def check_num(token: str) -> bool:
    for l in token:
        if not (l >='0' and l <='9' or l == '.'):
            return False
    return True

# read token from input expression
def get_token(inp:str, i:int) -> tuple[str, int]:
    while i < len(inp) and inp[i] == ' ':
        i += 1
    t = ''
    if i < len(inp) and (inp[i] in binary_ops or inp[i] in delim or inp[i] in parenth):
        return inp[i], i+1
    else:
        while i < len(inp) and not(inp[i] in binary_ops or inp[i] in delim or inp[i] == ' ' or inp[i] in parenth):
            t += inp[i]
            i += 1
        return t, i

# calculate number of arguments and parametres of function token
def calc_args(inp: str, i: int) -> tuple[int, int]:
    args = 0
    pars = 0
    arg_switch = False
    while i < len(inp) and inp[i] != ']':
        if inp[i] == '[':
            while i < len(inp) and inp[i] != ']':
                i += 1
        if i < len(inp) and inp[i] == ';':
            arg_switch = True
        elif i < len(inp) and inp[i] == ',':
            if arg_switch:
                args += 1
            else:
                pars += 1
        i += 1
    if arg_switch:
        return pars + 1, args + 1
    else:
        return 0, pars + 1 

# convert infix input to postfix and detect functions
def inf2post(inp: str, funcs=dict()) -> tuple[list, dict]:
    i = 0
    stack = []
    res = []
    p_token = None
    while i < len(inp):
        token, i = get_token(inp, i)
        if not(token in binary_ops or token in delim or token in parenth or (i < len(inp) and inp[i] == '[')):
            res.append(token)
        elif token == '-' and (p_token is None or p_token in {';', '(', '[', ','}):
            stack.append('u-')
        elif i < len(inp) and inp[i] == '[':
            stack.append(token)
            if token not in funcs:
                funcs[token] = calc_args(inp, i + 1)
        elif token in delim:
            while stack[len(stack) - 1] != '[':
                res.append(stack.pop())
        elif token in binary_ops:
            while len(stack) > 0 and stack[len(stack)-1] in priorities and priorities[stack[len(stack)-1]] >= priorities[token]:
                res.append(stack.pop())
            stack.append(token)
        elif token in {'(', '['}:
            stack.append(token)
        elif token in {')', ']'}:
            while stack[len(stack)-1] not in {'(', '['}:
                res.append(stack.pop())
            p = stack.pop()
            if p == '[':
                res.append(stack.pop())
        p_token = token
    while len(stack) > 0:
        res.append(stack.pop())
    return res, funcs




if __name__=="__main__":
    pass