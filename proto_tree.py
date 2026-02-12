# this is a third iteration of polynomial representation;
# evaluation tree as common in other symbolic packages
# because earlier realization has proven to be quite discombobulating when it came to parsing
# Node is a token of several possible origins: dependent variable (with children and dependencies)
# independent variable (without children and dependencies, i.e. all its derivatives are 0, might be numeric or a parameter)
# n-nary operation (functions to be replaced by additional variables, +, *, - to stay)
from proto_parse import *

class Node():
    # initialize by name or numeric value; parametres are stored for function nodes
    def __init__(self, name=None, val=None, children=[], params=[]):
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
            if type(self.kids[1]) is Node and self.kids[1].name in priorities and (priorities[self.name] > priorities[self.kids[1].name] or (self.name == '-' and priorities[self.name] >= priorities[self.kids[1].name]) or self.kids[1].name == 'u-'):
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
            return self.copy()
        elif self == b:
            return Node(name='*', children=[Node(val=2.), self.copy()])
        else:
            return Node(name='+', children=[self.copy(), b])

    def __sub__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value - b.value)
        elif self.name == 'num' and self.value == 0.:
            return -b
        elif b.name == 'num' and b.value == 0.:
            return self.copy()
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

    def det_nod_print(self):
        print(f'Node name: {self.name}')
        if self.value != None:
            print(f'Node value: {self.value}')
        if len(self.kids) > 0:
            print('Node kids:')
            for k in self.kids:
                print(k)
        if len(self.parameters) > 0:
            print('Node parameters:')
            for p in self.parameters:
                print(p)

    # check whether expression is polynomial (contains functions; functions are detected during parsing)  
    def is_poly(self, funcs: dict) -> bool:
        if self.name in funcs or self.name == '/' or (self.name == '^' and self.kids[1].name != 'num'):
            return False
        elif len(self.kids) == 0:
            return True
        else:
            for k in self.kids:
                if not k.is_poly(funcs):
                    return False
            return True

    # get derivative of polynomial expression accounting for polynomial de system
    # dictionary has depth 2 and Node instances as leaves
    def poly_derivative(self, var, system = dict()):
        if len(self.kids) == 0:
            if self.name == var:
                return Node(val=1.)
            elif self.name in system and var in system[self.name]:
                return system[self.name][var]
            else:
                return Node(val=0.)
        # composite function differentiation
        else:
            k_ders = [None] * len(self.kids)
            # recursively find derivatives of node children
            for i in range(len(self.kids)):
                k_ders[i] = self.kids[i].poly_derivative(var, system)
            # addition rule
            if self.name == '+':
                return k_ders[0] + k_ders[1]
            elif self.name == '-':
                return k_ders[0] - k_ders[1]
            elif self.name == 'u-':
                return -k_ders[0]
            # multiplication rule
            elif self.name == '*':
                return k_ders[0] * self.kids[1] + k_ders[1] * self.kids[0]
            # numeric power rule 
            elif self.name == '^' and self.kids[1].name == 'num':
                k_der = k_ders[0]
                return Node(val=self.kids[1].value) * self.kids[0] ** Node(val = self.kids[1].value - 1) * k_der
            else:
                print('Unforeseen complications')
                return None

    # find functions with polynomial arguments; finds all candidates
    def find_poly_funcs(self, funcs: dict, cands=[]):
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
                cands = k.find_poly_funcs(funcs, cands)
            return cands
    
    # substite expression; recursive; returns NEW instance
    def substitute(self, exp_old, exp_new):
        neu = self.copy()
        if neu == exp_old:
            return exp_new.copy()
        else:
            for i in range(len(self.kids)):
                neu.kids[i] = neu.kids[i].substitute(exp_old, exp_new)
        return neu

    # substitute several expressions (used in additional variables insertion step)
    # return NEW instance
    def bulk_substitute(self, exps_old: list, exps_new: list):
        neu = self.copy()
        for i in range(len(exps_old)):
            neu = neu.substitute(exps_old[i], exps_new[i])
        return neu

    def disempower(self):
        if len(self.kids) == 0:
            return self.copy()
        elif self.name == '^':
            p = int(self.kids[1].value)
            base = self.kids[0].copy()
            res = self.kids[0].copy()
            for _ in range(p):
                res = Node(name='*', children = [res, base])
            return res

    # open parentheses for normalization; 
    def balance(self):
        neu = self.copy()
        if len(neu.kids) == 0:
            return neu
        elif neu.name == '*' and neu.kids[1].name in {'+', '-'}:
            f = neu.kids[0]
            g = neu.kids[1].kids[0]
            h = neu.kids[1].kids[1]
            l = f * g
            r = f * h
            return Node(name=neu.kids[1].name, children=[l, r])
        elif neu.name == '*' and neu.kids[0].name in {'+', '-'}:
            f = neu.kids[1]
            g = neu.kids[0].kids[0]
            h = neu.kids[0].kids[1]
            l = f * g
            r = f * h
            return Node(name=neu.kids[0].name, children=[l, r])
        elif neu.name == '-' and neu.kids[1].name in {'+', '-'}:
            rev = {'+': '-', '-': '+'}
            f = neu.kids[0]
            g = neu.kids[1].kids[0]
            h = neu.kids[1].kids[1]
            l = f - g
            r = h
            return Node(name=rev[neu.kids[1].name], children=[l, r])
        elif neu.name == 'u-' and neu.kids[0].name in {'+', '-'}:
            rev = {'+': '-', '-': '+'}
            l = -neu.kids[0].kids[0]
            r = neu.kids[0].kids[1]
            return Node(name=rev[neu.kids[0].name], children=[l, r])
        elif neu.name == '*' and neu.kids[0].name == 'u-':
            f = neu.kids[0].kids[0]
            g = neu.kids[1]
            return -Node(name='*', children=[f, g])
        elif neu.name == '*' and neu.kids[1].name == 'u-':
            f = neu.kids[1].kids[0]
            g = neu.kids[0]
            return -Node(name='*', children=[f, g])
        elif neu.name in {'+', '-'} and neu.kids[1].name == 'u-':
            rev = {'+': '-', '-': '+'}
            f = neu.kids[0]
            g = neu.kids[1].kids[0]
            return Node(name=rev[neu.name], children=[f, g])
        elif neu.name == '+' and neu.kids[0].name == 'u-':
            f = neu.kids[0].kids[0]
            g = neu.kids[1]
            return g - f
        elif neu.name == '^' and len(neu.kids[0].kids) > 0:
            res = neu.copy()
            for _ in range(int(neu.kids[1].value)):
                res = Node(name='*', children=[neu, res])
            return res
        else:
            return Node(name=neu.name, children=[k.balance() for k in neu.kids])


    def open_parenth(self):
        neu = self.copy()
        r = neu.balance()
        while r != neu:
            neu = r.copy()
            r = neu.balance()
        return r        

    # find monomials IN POLYNOMIAL EXPRESSION WITHOUT PARENTHESES
    def find_monomials(self, res=[]) -> list:
        if self.name == '*' or len(self.kids) == 0:
            res.append(self)
        else:
            for k in self.kids:
                k.find_monomials(res)
        return res

    # generate monomial descriptor for normalization
    def get_mon_desc(self, desc=dict(), coef=1.) -> tuple[dict, float]:
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

    # deep recursive copy
    def copy(self):
        if len(self.kids) == 0:
            return Node(name=self.name, val=self.value)
        else:
            return Node(name=self.name, val=self.value, params=self.parameters, children=[k.copy() for k in self.kids])
    
    # detect variables in expression recursively
    def var_detector(self) -> set:
        if self.name == 'num':
            return set()
        elif len(self.kids) == 0:
            return {self.name}
        else:
            vars = set()
            for k in self.kids:
                vars = vars.union(k.var_detector())
            return vars
        
    # expression polynomization; 
    def polynomize(self, funcs):
        sub = dict()
        i = 0
        while not self.is_poly(funcs):
            cands = self.find_poly_funcs(funcs)
            self = self.substitute(cands[0], Node(name=f's{i}'))
            sub[f's{i}'] = cands[0]
            i += 1
        return self, sub

# get descriptors from UNFACTORIZED POLYNOMIAL
def get_mon_descs(mons: list[Node]) -> list[list]:
    res = [None] * len(mons)
    for i in range(len(mons)):
        res[i] = [dict(), 1.]
        res[i][0], res[i][1] = mons[i].get_mon_desc(res[i][0], res[i][1])
    return res

# get simplified descriptor
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

# generate monomial expression by descriptor;
def node_by_desc(desc: list) -> Node:
    res = None
    for v in desc[0]:
        nod = Node(name=v) ** Node(val=desc[0][v])
        if not type(res) is Node:
            res = nod
        else:
            res *= nod
    return Node(val=desc[1]) * res

# generate polynomial expression by descriptor
def node_by_descs(descs: list) -> Node:
    res = None
    for m in descs:
        if not type(res) is Node:
            res = node_by_desc(m)
        else:
            res += node_by_desc(m)
    return res

# get expression from postfix notation
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

# convert infix string to expression tree with function detection
def s2node(inp: str, funcs=dict()) -> tuple[Node, dict]:
    pol, funcs = inf2post(inp, funcs)
    n = post2node(pol, funcs)
    return n, funcs

if __name__ == "__main__":
    expression  = '(f1 + f2) ^ 10'
    e, f = s2node(expression)
    print(e)
    e = e.disempower()
    print(e)