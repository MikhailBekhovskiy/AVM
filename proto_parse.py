# new version of parsing base on notations and tree
from proto_tree import *

bin_ops = {'*', '+', '-', '/', '^'}
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

def check_num(token):
    for l in token:
        if not (l >='0' and l <='9' or l == '.'):
            return False
    return True

def get_token(inp:str, i:int):
    while i < len(inp) and inp[i] == ' ':
        i += 1
    t = ''
    if i < len(inp) and (inp[i] in bin_ops or inp[i] in delim or inp[i] in parenth):
        return inp[i], i+1
    else:
        while i < len(inp) and not(inp[i] in bin_ops or inp[i] in delim or inp[i] == ' ' or inp[i] in parenth):
            t += inp[i]
            i += 1
        return t, i

def calc_args(inp: str, i: int):
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

def inf2post(inp: str):
    i = 0
    stack = []
    res = []
    funcs = dict()
    p_token = None
    while i < len(inp):
        token, i = get_token(inp, i)
        if not(token in bin_ops or token in delim or token in parenth or (i < len(inp) and inp[i] == '[')):
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
        elif token in bin_ops:
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

def post2node(p: list, funcs: dict, debug=False):
    stack = []
    for token in p:
        if not(token in funcs or token in bin_ops or token == 'u-'):
            if not check_num(token):
                n = Node(name=token, children=[])
            else:
                n = Node(val=float(token))
            stack.append(n)
        else:
            if token == 'u-':
                stack[len(stack)-1] = -stack[len(stack)-1]
            else:
                if token in funcs:
                    pars, args = funcs[token][0], funcs[token][1]
                else:
                    pars, args = 0, 2
                operands = [None] * args
                params = [None] * pars
                for i in range(args):
                    operands[args - 1 - i] = stack.pop()
                for i in range(pars):
                    params[pars - 1 - i] = stack.pop()
                if token == '+':
                    stack.append(operands[0] + operands[1])
                elif token == '-':
                    stack.append(operands[0] - operands[1])
                elif token == '*':
                    stack.append(operands[0] * operands[1])
                elif token == '^':
                    stack.append(operands[0] ** operands[1])
                elif token == '/':
                    stack.append(operands[0] / operands[1])
                else:
                    stack.append(Node(name=token, children=operands, params=params))
    return stack[0]

def s2node(inp: str):
    pol, funcs = inf2post(inp)
    n = post2node(pol, funcs)
    return n, funcs


if __name__=="__main__":
    expression = 'x3^3*sin[cos[a*ln[x2]^2 + b*x3]] + x3^3*b*ln[x2]^4 + sin[a*ln[x2]^2 + b*x3]^5 + Dv[g^2, 1, -1; x1]'
    e, f = s2node(expression)
    print('Original:\n', e)
    print('Found funcs:\n', f)
    if not e.is_poly(f):
        e, hist = e.polynomize(f)
        print('New expression:\n', e)
        print('Substitutes:')
        for s in hist:
            print(s, ' is ', hist[s])
    print('Unfactorized expression:')
    e = e.open_parenth()
    print(e)
    m = e.find_monomials()
    print(f'Found {len(m)} monomials!')
    m = get_mon_descs(m)
    m = simplify_by_descs(m)
    print(f'Simplified to {len(m)} monomials:')
    print(m)
    e = node_by_descs(m)
    print(f'Transformed expression:')
    print(e)