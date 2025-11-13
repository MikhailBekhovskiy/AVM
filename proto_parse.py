# new version of parsing base on notations and tree
from proto_tree import Node

bin_ops = {'*', '+', '-', '/', '^'}
delim = ';'
parenth = {'(', ')', '[', ']'}
priorities = {
    '+': 0,
    '-': 0,
    'u-': 1,
    '*': 2,
    '/': 2,
    '^': 3
}


def get_token(inp:str, i:int):
    while i < len(inp) and inp[i] == ' ':
        i += 1
    t = ''
    if i < len(inp) and (inp[i] in bin_ops or inp[i] == ';' or inp[i] in parenth):
        return inp[i], i+1
    else:
        while i < len(inp) and not(inp[i] in bin_ops or inp[i] == ';' or inp[i] == ' ' or inp[i] in parenth):
            t += inp[i]
            i += 1
        return t, i

def calc_args(inp: str, i: int):
    res = 0
    while i < len(inp) and inp[i] != ']':
        if inp[i] == '[':
            while i < len(inp) and inp[i] != ']':
                i += 1
        if i < len(inp) and inp[i] == ';':
            res += 1
        i += 1
    return res + 1

def inf2post(inp: str):
    i = 0
    stack = []
    res = []
    funcs = dict()
    while i < len(inp):
        token, i = get_token(inp, i)
        if not(token in bin_ops or token == delim or token in parenth or (i < len(inp) and inp[i] == '[')):
            res.append(token)
        elif token == '-' and (i == 1 or inp[i-2] in {'(', '[', ';'}):
            stack.append('u-')
        elif i < len(inp) and inp[i] == '[':
            stack.append(token)
            if token not in funcs:
                funcs[token] = calc_args(inp, i + 1)
        elif token == delim:
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
    while len(stack) > 0:
        res.append(stack.pop())
    return res, funcs

def post2node(p: list, funcs: dict, debug=False):
    stack = []
    for token in p:
        if not(token in funcs or token in bin_ops or token == 'u-'):
            n = Node(name=token, children=[])
            # if debug:
            #    print('Variable node')
            #    print(n.name)
            stack.append(n)
        else:
            n = Node(name=token, children=[])
            if token in funcs:
                args = funcs[token]
            elif token in bin_ops:
                args = 2
            else:
                args = 1
            n.kids = [None] * args
            if debug:
                print('Creation check')
                print(n.name, [kid for kid in n.kids])
                print('Arguments: ', args)
            for i in range(args):
                n.kids[args - 1 - i] = stack.pop()
                n.kids[args - 1 - i].parent = n
            stack.append(n)
            if debug:
                print('Operation node')
                print(n.name, [kid.name for kid in n.kids])
    return stack[0]



if __name__=="__main__":
    expression = 'a*x*(x - L)*inv[N + x]'
    expression, funcs = inf2post(expression)
    print('Found functions:\n', funcs)
    print('RPN\n', expression)
    expression = post2node(expression, funcs, debug=False)
    print('Reverse parsing:\n', expression)