# this is a third iteration of polynomial representation;
# evaluation tree as common in other symbolic packages
# because earlier realization has proven to be quite discombobulating when it came to parsing
# Node is a token of several possible origins: dependent variable (with children and dependencies)
# independent variable (without children and dependencies, i.e. all its derivatives are 0, might be numeric or a parameter)
# n-nary operation (functions to be replaced by additional variables, +, *, - to stay)
from proto_parse import *

class Node():
    def __init__(self, name=None, val=None, children=[], deps=dict(), params=[]):
        if name == None:
            self.name = 'num'
            if val == None:
                self.value = 0.
            else:
                self.value = val
        else:
            self.name = name
            self.value = val
        self.kids = children
        self.dependencies = deps
        self.parameters = params

    def __str__(self):
        if self.name == 'num':
            return str(self.value)
        elif len(self.kids) == 0:
            return self.name
        elif self.name in binary_ops and len(self.kids) == 2:
            l = self.kids[0].__str__()
            if type(self.kids[0]) is Node and self.kids[0].name in priorities and priorities[self.name] > priorities[self.kids[0].name]:
                l = '(' + l + ')'
            r = self.kids[1].__str__()
            if type(self.kids[1])is Node and self.kids[1].name in priorities and (priorities[self.name] > priorities[self.kids[1].name] or (self.name == '-' and priorities[self.name] >= priorities[self.kids[1].name])):
                r = '(' + r + ')'
            return l + ' ' + self.name + ' ' + r
        elif self.name in unary_ops and len(self.kids) == 1:
            s = self.kids[0].__str__()
            if self.name == 'u-':
                nam = '-'
            else:
                nam = self.name
            if type(self.kids[0]) is Node and self.kids[0].name in priorities and priorities[self.name] >= priorities[self.kids[0].name]:
                s = '(' + s + ')'
            return nam + s
        else:
            res = self.name + '['
            if self.parameters != []:
                for p in self.parameters:
                    res += p.__str__() + ', '
                res = res[:-2] + '; '
            for k in self.kids:
                res += k.__str__() + ', '
            res = res[:len(res)-2]
            return res + ']'
        
    def is_poly(self, funcs: dict):
        if self.name in funcs or self.name == '/' or (self.name == '^' and self.kids[1].name != 'num'):
            return False
        elif len(self.kids) == 0:
            return True
        else:
            for k in self.kids:
                if not k.is_poly(funcs):
                    return False
            return True
        
    def __eq__(self, b):
        if self.name != b.name or len(self.kids) != len(b.kids):
            return False
        elif self.name == b.name and len(self.kids) == 0 and len(b.kids) == 0:
            return True
        else:
            for i in range(len(self.kids)):
                if not self.kids[i].__eq__(b.kids[i]):
                    return False
            for i in range(len(self.parameters)):
                if not self.parameters[i].__eq__(b.parameters[i]):
                    return False
            return True
        
    def __neg__(self):
        if self.name == 'num':
            return Node(val = -self.value)
        else:
            return Node(name='u-', children = [self])   

    def __add__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value + b.value)
        elif self.name == 'num' and self.value == 0.:
            return b
        elif b.name == 'num' and b.value == 0.:
            return self
        elif self == b:
            return Node(name='*', children=[Node(val=2.), self])
        else:
            return Node(name='+', children=[self, b])

    def __sub__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value - b.value)
        elif self.name == 'num' and self.value == 0.:
            return Node(name='u-', children=[b])
        elif b.name == 'num' and b.value == 0.:
            return self
        elif self == b:
            return Node(val = 0.)
        else:
            return Node(name='-', children=[self, b])

    def __mul__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value*b.value)
        elif self.name == 'num' and self.value == 0. or b.name == 'num' and b.value == 0.:
            return Node(val = 0.)
        elif self.name == 'num' and self.value == 1.:
            return b
        elif b.name == 'num' and b.value == 1.:
            return self
        elif self == b:
            return Node(name='^', children=[self, Node(val=2.)])
        else:
            return Node(name='*', children=[self, b])    
    
    def __truediv__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value / b.value)
        elif self.name == 'num' and self.value == 0.:
            return Node(val=0.)
        elif b.name == 'num' and b.value == 1.:
            return self
        else:
            return Node(name='/', children=[self, b])

    def __pow__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value ** b.value)
        elif self.name == 'num' and self.value == 0.:
            return Node(val=0.)
        elif self.name == 'num' and self.value == 1.:
            return Node(val=1.)
        elif b.name == 'num' and b.value == 0.:
            return Node(val=1.)
        elif b.name == 'num' and b.value == 1.:
            return self
        else:
            return Node(name='^', children=[self, b])

    def poly_derivative(self, var):
        if len(self.kids) == 0:
            if self.name == var:
                return Node(val=1.)
            elif var not in self.dependencies or self.name == 'num':
                return Node(val=0.)
            else:
                return self.dependencies[var]
        else:
            k_ders = [None] * len(self.kids)
            for i in range(len(self.kids)):
                k_ders[i] = self.kids[i].poly_derivative(var)
            if self.name == '+':
                return k_ders[0] + k_ders[1]
            elif self.name == '-':
                return k_ders[0] - k_ders[1]
            elif self.name == 'u-':
                return -k_ders[0]
            elif self.name == '*':
                return k_ders[0] * self.kids[1] + k_ders[1] * self.kids[0]
            elif self.name == '^' and self.kids[1].name == 'num':
                k_der = k_ders[0]
                return Node(val=self.kids[1].value) * self.kids[0] ** Node(val = self.kids[1].value - 1) * k_der
            else:
                print('Unforeseen complications')
                return None

    def find_poly_func(self, funcs: dict, cands=[]):
        if len(self.kids) == 0:
            return cands
        else:
            if self.name in funcs:
                cand = True
                for k in self.kids:
                    if not k.is_poly(funcs):
                        cand = False
                        break
                if cand == True:
                    return cands + [self]
            for k in self.kids:
                cands = k.find_poly_func(funcs, cands)
            return cands
        
    def substitute(self, exp_old, exp_new):
        if self == exp_old:
            return exp_new
        else:
            for i in range(len(self.kids)):
                self.kids[i] = self.kids[i].substitute(exp_old, exp_new)
        return self

    def bulk_substitute(self, exp_olds, exp_news):
        for i in range(len(exp_olds)):
            self = self.substitute(exp_olds[i], exp_news[i])
        return self

    def open_parenth(self):
        if len(self.kids) == 0:
            return self
        elif self.name == '*' and self.kids[0].name in {'+', '-'}:
            l = self.kids[1] * self.kids[0].kids[0]
            r = self.kids[1] * self.kids[0].kids[1]
            if self.kids[0].name == '+':
                self = l + r
            else:    
                self = l - r
            return self.open_parenth()
        elif self.name == '*' and self.kids[1].name in {'+', '-'}:
            l = self.kids[0] * self.kids[1].kids[0]
            r = self.kids[0] * self.kids[1].kids[1]
            if self.kids[1].name == '+':
                self = l + r
            else:
                self = l - r
            return self.open_parenth()
        elif self.name == '^' and self.kids[1].name == 'num':
            i = self.kids[1].value
            base = self.kids[0]
            res = base
            while i > 1:
                res = Node(name = '*', children=[res, base])
                res = res.open_parenth()
                i -= 1
            return res.open_parenth()
        else:
            for i in range(len(self.kids)):
                self.kids[i] = self.kids[i].open_parenth()
            return self

    def find_monomials(self, res=[]):
        if self.name == '*' or len(self.kids) == 0:
            res.append(self)
        else:
            for k in self.kids:
                k.find_monomials(res)
        return res

    def get_mon_desc(self, desc=dict(), coef=1.):
        if len(self.kids) == 0:
            if self.name == 'num':
                coef *= self.value
            else:
                if self.name in desc:
                    desc[self.name] += 1
                else:
                    desc[self.name] = 1
        else:
            for k in self.kids:
                desc, coef = k.get_mon_desc(desc, coef)
        return desc, coef

    # should be FIXED to account for the library
    def polynomize(self, funcs):
        sub = dict()
        i = 0
        while not self.is_poly(funcs):
            cands = self.find_poly_func(funcs)
            self = self.substitute(cands[0], Node(name=f's{i}'))
            sub[f's{i}'] = cands[0]
            i += 1
        return self, sub

def get_mon_descs(mons: list[Node]) -> list[list]:
    res = [None] * len(mons)
    for i in range(len(mons)):
        res[i] = [dict(), 1.]
        res[i][0], res[i][1] = mons[i].get_mon_desc(res[i][0], res[i][1])
    return res

def simplify_by_descs(mons: list[list]) -> list[dict]:
    pairs = 0
    for i in range(len(mons)):
        for j in range(i+1, len(mons)):
            if mons[i] != None and mons[j] != None and mons[i][0] == mons[j][0]:
                mons[i][1] += mons[j][1]
                mons[j] = None
                pairs += 1
    res = [None] * (len(mons) - pairs)
    i = 0
    for m in mons:
        if m != None:
            res[i] = m
            i += 1
    return res

def node_by_desc(desc: list) -> Node:
    res = None
    for v in desc[0]:
        nod = Node(name=v) ** Node(val=desc[0][v])
        if not type(res) is Node:
            res = nod
        else:
            res *= nod
    return Node(val=desc[1]) * res

def node_by_descs(descs: list) -> Node:
    res = None
    for m in descs:
        if not type(res) is Node:
            res = node_by_desc(m)
        else:
            res += node_by_desc(m)
    return res

def post2node(p: list, funcs: dict, debug=False) -> Node:
    stack = []
    for token in p:
        if not(token in funcs or token in binary_ops or token == 'u-'):
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

def s2node(inp: str, funcs=dict()) -> Node:
    pol, funcs = inf2post(inp, funcs)
    n = post2node(pol, funcs)
    return n, funcs

if __name__ == "__main__":
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