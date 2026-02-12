# this is a third iteration of polynomial representation;
# evaluation tree as common in other symbolic packages
# because earlier realization has proven to be quite discombobulating when it came to parsing
# Node is a token of several possible origins: dependent variable (with children and dependencies)
# independent variable (without children and dependencies, i.e. all its derivatives are 0, might be numeric or a parameter)
# n-nary operation (functions to be replaced by additional variables, +, *, - to stay)
from proto_parse import *

def factorial(n):
    if n >= 0:
        if n == 0 or n == 1:
            return 1
        else:
            res = 2
            for i in range(3, n + 1):
                res *= i
            return res

def Cnk(n, k):
    if k >= 0 and n >= k:
        return factorial(n) / factorial(k) / factorial(n-k)

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
        elif self.name == 'u-':
            return self.kids[0].copy()
        else:
            return Node(name='u-', children = [self.copy()])   

    def __add__(self, b):
        if self.name == 'num' and b.name == 'num':
            return Node(val=self.value + b.value)
        elif self.name == 'num' and self.value == 0.:
            return b
        elif b.name == 'num' and b.value == 0.:
            return self.copy()
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
        if type(b) is float or type(b) is int:
            return self ** Node(val=b)
        elif self.name == 'num' and b.name == 'num':
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
            for i in range(len(self.kids)):
                print(f'Kid #{i}: {self.kids[i]}')
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

    def is_mono(self):
        if len(self.kids) == 0:
            return True
        elif self.name not in {'*', '^'}:
            return False
        else:
            for k in self.kids:
                if not k.is_mono():
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

    def mon_dec(self):
        if self.is_mono():
            if len(self.kids) == 0 or self.name == '^':
                return [self]
            else:
                return self.kids[0].mon_dec() + self.kids[1].mon_dec()

    def get_mon_decs(self):
        if self.is_mono():
            return [self.mon_dec()]
        else:
            return self.kids[0].get_mon_decs() + self.kids[1].get_mon_decs()

    def is_balanceable(self, debug=False):
        if (self.name == '^' and self.kids[0].name in {'^', '*', '+', '-', 'u-'}):
            if debug:
                print(f'Unbalance at:')
                self.det_nod_print()
            return True
        if self.name == '*' and (self.kids[0].name in {'+', '-', 'u-'} or self.kids[1].name in {'+', '-', 'u-'}):
            if debug:
                print(f'Unbalance at:')
                self.det_nod_print()
            return True
        for k in self.kids:
            if k.is_balanceable(debug=debug):
                return True
        return False

    def balance_power(self):
        if len(self.kids) == 0 or len(self.kids[0].kids) == 0:
            return self.copy()
        elif self.name == '^':
            n = int(self.kids[1].value)
            if self.kids[0].name == '*':
                a = self.kids[0].kids[0].copy()
                b = self.kids[0].kids[1].copy()
                res = a ** n * b ** n
            elif self.kids[0].name == '+':
                res = Node(val=0)
                a = self.kids[0].kids[0].copy()
                b = self.kids[0].kids[1].copy()
                for k in range(n + 1):
                    res += Node(val=Cnk(n, k)) * a ** (n-k) * b ** k
            elif self.kids[0].name == '-':
                res = Node(val=0)
                a = self.kids[0].kids[0].copy()
                b = -self.kids[0].kids[1].copy()
                for k in range(n + 1):
                    res += Node(val=Cnk(n, k)) * a ** (n-k) * b ** k
            elif self.kids[0].name == 'u-':
                a = self.kids[0].kids[0].copy()
                if int(self.kids[1].value) % 2 == 0:
                    res = a ** n
                else:
                    res = -a ** n
            elif self.kids[0].name == '^':
                m = int(self.kids[0].kids[1].value)
                a = self.kids[0].kids[0].copy()
                res = a ** (m*n)
                res = res.balance_power()
            else:
                res = self.copy()
        else:
            res = self.copy()
        for i in range(len(res.kids)):
            res.kids[i] = res.kids[i].balance_power()
        return res

    def balance_mult(self):
        if len(self.kids) == 0:
            return self.copy()
        elif self.name == '*':
            if self.kids[0].name == 'u-':
                a = self.kids[0].kids[0].copy()
                b = self.kids[1].copy()
                res = -(a * b)
            elif self.kids[1].name == 'u-':
                a = self.kids[0].copy()
                b = self.kids[1].kids[0].copy()
                res = -(a * b)
            elif self.kids[0].name == '+':
                a = self.kids[0].kids[0].copy()
                b = self.kids[0].kids[1].copy()
                c = self.kids[1].copy()
                res = a * c + b * c
            elif self.kids[1].name == '+':
                a = self.kids[1].kids[0].copy()
                b = self.kids[1].kids[1].copy()
                c = self.kids[0].copy()
                res = a * c + b * c
            elif self.kids[0].name == '-':
                a = self.kids[0].kids[0].copy()
                b = self.kids[0].kids[1].copy()
                c = self.kids[1].copy()
                res = a * c - b * c
            elif self.kids[1].name == '-':
                a = self.kids[1].kids[0].copy()
                b = self.kids[1].kids[1].copy()
                c = self.kids[0].copy()
                res = a * c - b * c
            else:
                res = self.copy()
        else:
            res = self.copy()
        for i in range(len(res.kids)):
            res.kids[i] = res.kids[i].balance_mult()
        return res

    def balance_min(self):
        if len(self.kids) == 0:
            return self.copy()
        elif self.name == '-':
            a = self.kids[0].copy()
            b = -self.kids[1].copy()
            res = a + b
        elif self.name == 'u-':
            if self.kids[0].is_mono():
                return Node(val=-1) * self.kids[0].copy()
            elif self.kids[0].name == 'u-':
                res = self.kids[0].kids[0].copy()
            else:
                a = -self.kids[0].kids[0].copy()
                b = -self.kids[0].kids[1].copy()
                res = Node(name=self.kids[0].name, children = [a, b])
        else:
            res = self.copy()
        for i in range(len(res.kids)):
            res.kids[i] = res.kids[i].balance_min()
        return res
    
    # normalize expression 
    def balance(self):
        r = self.copy()
        r = r.balance_power()
        while r.is_balanceable():
            r = r.balance_mult()
        r = r.balance_min()
        return r
            

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

def mon_dec_norm(monoms):
    for i in range(len(monoms)):
        m = monoms[i]
        d = {'coef': 1}
        for v in m:
            if v.name == 'num':
                d['coef'] *= v.value
            elif v.name == '^':
                if v.kids[0].name not in d:
                    d[v.kids[0].name] = v.kids[1].value
                else:
                    d[v.kids[0].name] += v.kids[1].value
            else:
                if v.name not in d:
                    d[v.name] = 1
                else:
                    d[v.name] += 1
        monoms[i] = d
    return monoms

def mon_eq(m1, m2):
    if len(m1) != len(m2):
        return False
    for v in m1:
        if v != 'coef':
            if v not in m2 or m1[v] != m2[v]:
                return False
    return True

def simplify(mons):
    for i in range(len(mons)):
        if mons[i]['coef'] != 0:
            for j in range(i + 1, len(mons)):
                if mons[j]['coef'] != 0 and mon_eq(mons[i], mons[j]):
                    mons[i]['coef'] += mons[j]['coef']
                    mons[j]['coef'] = 0
    res = []
    for m in mons:
        if m['coef'] != 0:
            res.append(m)
    return res

def gen_mon(mon):
    res = Node(val=mon['coef'])
    for v in mon:
        if v != 'coef':
            res *= Node(name=v) ** mon[v]
    return res

def gen_poly(mons):
    if len(mons) == 0:
        return Node(val=0)
    else:
        res = gen_mon(mons[0])
        for i in range(1, len(mons)):
            res += gen_mon(mons[i])
        return res

def normalize_poly(P):
    P = P.balance()
    P = P.get_mon_decs()
    P = mon_dec_norm(P)
    P = simplify(P)
    return gen_poly(P)

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
    e, f = s2node(inp='(-s5) * (-s4) * 2.0 * s1 * s2 * a')
    e = normalize_poly(e)
    print(e)
    