# this is a third iteration of polynomial representation;
# evaluation tree as common in other symbolic packages
# because earlier realization has proven to be quite discombobulating when it came to parsing
# Node is a token of several possible origins: dependent variable (with children and dependencies)
# independent variable (without children and dependencies, i.e. all its derivatives are 0, might be numeric or a parameter)
# n-nary operation (functions to be replaced by additional variables, +, *, - to stay)
from parse import *
type monodesc = dict[str, float]

def var_name2latex(v: str) -> str:
    res = v[0]
    if len(v) > 1:
        res += '_{' + v[1:] + '}'
    return res

def factorial(n: int) -> int:
    if n >= 0:
        if n == 0 or n == 1:
            return 1
        else:
            res = 2
            for i in range(3, n + 1):
                res *= i
            return res
    else:
        return -1

def Cnk(n: int, k: int) -> int:
    if k >= 0 and n >= k:
        return factorial(n) // factorial(k) // factorial(n-k)
    return -1

def merge_descriptors(L: dict[str, float], R: dict[str, float]) -> dict[str, float]:
    res = {'coef': L['coef'] * R['coef']}
    for var in L:
        if var != 'coef':
            res[var] = L[var]
    for var in R:
        if var != 'coef':
            if var in res:
                res[var] += R[var]
            else:
                res[var] = R[var]
    return res

def descriptor_comparator(L: monodesc, R: monodesc) -> bool:
    for v in L:
        if v != 'coef':
            if v not in R or R[v] != L[v]:
                return False
    for v in R:
        if v !='coef':
            if v not in L or R[v] != L[v]:
                return False
    return True

def descriptor_adder(L: monodesc, R:monodesc) -> monodesc:
    if descriptor_comparator(L, R):
        L['coef'] += R['coef']
        return L
    else:
        print('Different monos. Returning first unchanged.')
        return L

def desc_copy(L:monodesc) -> monodesc:
    res: monodesc = dict()
    for v in L:
        res[v] = L[v]
    return res

def descriptor_squash(M: list[monodesc]) -> list[monodesc]:
    res: list[monodesc] = []
    for i in range(len(M)):
        r = {'coef': 0.}
        if 'checked' not in M[i]:
            r = desc_copy(M[i])
            for j in range(i+1, len(M)):
                if 'checked' not in M[j] and descriptor_comparator(M[i], M[j]):
                    r['coef'] += M[j]['coef']
                    M[j]['checked'] = 1.
        if r['coef'] != 0.:
            res.append(r)
    return res

def mono_power(m: monodesc) -> float:
    res = 0.
    for x in m:
        if x != 'coef':
            res += m[x]
    return res

def mlm(L: monodesc, R: monodesc) -> bool:
    lp = mono_power(L)
    rp = mono_power(R)
    if lp < rp:
        return True
    else:
        return False

def monosort(M: list[monodesc]):
    for i in range(len(M)):
        for j in range(len(M)-i-1):
            if mlm(M[j], M[j+1]):
                M[j], M[j+1] = M[j+1], M[j]
 
    

class Node():
    name: str
    value: float
    children: list["Node"]
    params: list["Node"]
    # initialize by name or numeric value; parametres are stored for function nodes
    def __init__(self, name: str='num', val: float=0., children:list["Node"]=[], params:list["Node"]=[]):
        self.name = name
        self.value = val
        self.kids = children
        self.parameters = params

    def __str__(self, latex=False):
        if latex:
            leftp = '\\left('
            rightp = '\\right)'
        else:
            leftp = '('
            rightp = ')'
        if self.name == 'num':
            n = self.value
            if n - float(int(n)) > 0.:
                res =  str(self.value)
            else:
                res = str(int(n))
            if n < 0:
                res = leftp + res + rightp
            return res
        elif self.name == 'inv' and latex:
            return '\\frac{1}{' + self.kids[0].__str__(latex) + '}'
        elif self.name == 'isqrt' and latex:
            return '\\frac{1}{\\sqrt{' + self.kids[0].__str__(latex) + '}}'
        elif len(self.kids) == 0:
            if not latex:
                name = self.name
            else:
                name = var_name2latex(self.name)
            return name
        elif self.name in binary_ops and len(self.kids) == 2:
            l = self.kids[0].__str__(latex)
            if type(self.kids[0]) is Node and self.kids[0].name in priorities and priorities[self.name] > priorities[self.kids[0].name]:
                l = leftp + l + rightp
            r = self.kids[1].__str__(latex)
            if type(self.kids[1]) is Node and self.kids[1].name in priorities and (priorities[self.name] > priorities[self.kids[1].name] or (self.name == '-' and priorities[self.name] >= priorities[self.kids[1].name]) or self.kids[1].name == 'u-'):
                r = leftp + r + rightp
            if self.name == '^' and self.kids[1].name == 'num' and latex:
                if self.kids[0].name not in binary_ops.union(unary_ops.union({'isqrt', 'inv'})) and len(self.kids[0].kids) > 0:
                    funcname = self.kids[0].name
                    power = self.kids[1].__str__(latex)
                    params = ''
                    if self.kids[0].parameters != []:
                        for p in self.kids[0].parameters:
                            params += p.__str__(latex) + ', '
                        params = params[:-2] + '; '
                    args = ''
                    for k in self.kids[0].kids:
                        args += k.__str__(latex) + ', '
                        args = args[:-2]
                    return '\\text{' + funcname + '}^{' + power + '}' + leftp + params + args + rightp
                else:
                    r = '{' + r + '}'
                if latex and self.kids[0].name in {'inv', 'isqrt'}:
                    l = leftp + l + rightp
            if self.name == '*' and latex:
                name = ''
            else:
                name = self.name
            return l + ' ' + name + ' ' + r
        elif self.name in unary_ops and len(self.kids) == 1:
            s = self.kids[0].__str__(latex)
            if self.name == 'u-':
                nam = '-'
            else:
                nam = self.name
            if type(self.kids[0]) is Node and self.kids[0].name in priorities and priorities[self.name] >= priorities[self.kids[0].name]:
                s = leftp + s + rightp
            return nam + s
        else:
            if latex:
                parl = leftp
                parr = rightp
                name = '\\text{' + self.name + '}'
            else:
                parl = '['
                parr = ']'
                name = self.name
            res = name + parl
            if self.parameters != []:
                for p in self.parameters:
                    res += p.__str__(latex) + ', '
                res = res[:-2] + '; '
            for k in self.kids:
                res += k.__str__(latex) + ', '
            res = res[:len(res)-2]
            return res + parr
        
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
            return Node(name='*', children = [Node(val=-1.), self.copy()])   

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
    def is_poly(self, funcs: dict[str, tuple[int, int]]) -> bool:
        if self.name in funcs or self.name == '/' or (self.name == '^' and self.kids[1].name != 'num'):
            return False
        elif len(self.kids) == 0:
            return True
        else:
            for k in self.kids:
                if not k.is_poly(funcs):
                    return False
            return True

    def is_mono(self) -> bool:
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
    def poly_derivative(self, var:str, system:dict[str, dict[str, "Node"]] = dict()) -> "Node":
        if len(self.kids) == 0:
            if self.name == var:
                return Node(val=1.)
            elif self.name in system and var in system[self.name]:
                return system[self.name][var]
            else:
                return Node(val=0.)
        # composite function differentiation
        else:
            k_ders = [Node()] * len(self.kids)
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
                return Node()

    # find functions with polynomial arguments; finds all candidates
    def find_poly_funcs(self, funcs: funcssign, cands:list["Node"]=[]) -> list["Node"]:
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
    def substitute(self, exp_old: "Node", exp_new: "Node") -> "Node":
        neu = self.copy()
        if neu == exp_old:
            return exp_new.copy()
        else:
            for i in range(len(self.kids)):
                neu.kids[i] = neu.kids[i].substitute(exp_old, exp_new)
        return neu

    # substitute several expressions (used in additional variables insertion step)
    # return NEW instance
    def bulk_substitute(self, exps_old: list["Node"], exps_new: list["Node"]) -> "Node":
        neu = self.copy()
        for i in range(len(exps_old)):
            neu = neu.substitute(exps_old[i], exps_new[i])
        return neu

    # top-level (root) parenthesis opener and minus eliminator
    def open_parenthesis(self) -> "Node":
        #(g + h)*f case
        if self.name == '*' and self.kids[0].name == '+':
            f = self.kids[1].copy()
            g = self.kids[0].kids[0].copy()
            h = self.kids[0].kids[1].copy()
            return f * g + f * h
        # f * (g+h) case
        if self.name == '*' and self.kids[1].name == '+':
            f = self.kids[0].copy()
            g = self.kids[1].kids[0].copy()
            h = self.kids[1].kids[1].copy()
            return f * g + f * h
        #(g - h)*f case
        if self.name == '*' and self.kids[0].name == '-':
            f = self.kids[1].copy()
            g = self.kids[0].kids[0].copy()
            h = self.kids[0].kids[1].copy()
            return f * g - f * h
        # f * (g - h) case
        if self.name == '*' and self.kids[1].name == '-':
            f = self.kids[0].copy()
            g = self.kids[1].kids[0].copy()
            h = self.kids[1].kids[1].copy()
            return f * g - f * h
        # (f*g) ^ n case
        if self.name == '^' and self.kids[0].name == '*':
            f = self.kids[0].kids[0].copy()
            g = self.kids[0].kids[1].copy()
            n = self.kids[1].copy()
            return (f ** n) * (g ** n)
        # (f + g) ^ n case
        if self.name == '^' and self.kids[0].name == '+':
            f = self.kids[0].kids[0].copy()
            g = self.kids[0].kids[1].copy()
            n = self.kids[1].copy()
            result = Node()
            for k in range(int(n.value) + 1):
                cf = Cnk(int(n.value), k)
                result += Node(val=float(cf)) * (f ** Node(val=n.value - k)) * (g ** Node(val=float(k)))
            return result
        # (f - g) ^ n case
        if self.name == '^' and self.kids[0].name == '-':
            f = self.kids[0].kids[0].copy()
            g = self.kids[0].kids[1].copy()
            n = self.kids[1].copy()
            result = Node()
            for k in range(int(n.value) + 1):
                cf = Cnk(int(n.value), k)
                result += Node(val=float((-1)**k)) * Node(val=float(cf)) * (f ** Node(val=n.value - k)) * (g ** Node(val=float(k)))
            return result
        # u- conversion for simplicity
        if self.name == 'u-':
            f = self.kids[0].copy()
            return -f
        # f - g = f + (-1) * g conversion for simplicity
        if self.name == '-':
            f = self.kids[0].copy()
            g = self.kids[1].copy()
            return f + (-g)
        else:
            print('Unknown simplification')
            return self

    # stops at first one or two parentheses occurences;
    # fires a flag if a change has occurred
    def shallow_opener(self) -> tuple["Node", bool]:
        if len(self.kids) == 0:
            return self.copy(), False
        if self.name == '*' and (self.kids[0].name in {'+', '-'} or self.kids[1].name in {'+', '-'}) or \
            self.name == '^' and (self.kids[0].name in {'*', '+', '-'}) or\
            self.name in {'u-', '-'}:
            return self.open_parenthesis(), True
        else:
            self.kids[0], l = self.kids[0].shallow_opener()
            self.kids[1], r = self.kids[1].shallow_opener()
            return self.copy(), l or r

    def deep_opener(self) -> "Node":
        still = True
        while still:
            self, still = self.shallow_opener()
        return self.copy()

    def monomial_descriptor(self) -> dict[str, float]:
        if self.name == 'num':
            descriptor = {'coef': self.value}
            return descriptor
        if self.name == '^':
            if self.kids[0].name == 'num':
                descriptor = {'coef': self.kids[0].value ** self.kids[1].value}
                return descriptor
            descriptor = {'coef': 1., self.kids[0].name: self.kids[1].value}
            return descriptor
        if self.name == '*':
            L = self.kids[0].monomial_descriptor()
            R = self.kids[1].monomial_descriptor()
            return merge_descriptors(L, R)
        if self.name != '+':
            return {'coef': 1., self.name: 1.}
        else:
            print('Not a monomial')
            return {'undefined': -1}

    def get_all_mono_descs(self) -> list[dict[str, float]]:
        if self.name != '+':
            return [self.monomial_descriptor()]
        else:
            return self.kids[0].get_all_mono_descs() + self.kids[1].get_all_mono_descs()

    # deep recursive copy
    def copy(self) -> "Node":
        if len(self.kids) == 0:
            return Node(name=self.name, val=self.value)
        else:
            return Node(name=self.name, val=self.value, params=self.parameters, children=[k.copy() for k in self.kids])
    
    # detect variables in expression recursively
    def var_detector(self) -> set[str]:
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
    def polynomize(self, funcs: funcssign) -> tuple["Node", dict[str, "Node"]]:
        sub: dict[str, "Node"] = dict()
        i = 0
        while not self.is_poly(funcs):
            cands = self.find_poly_funcs(funcs)
            self = self.substitute(cands[0], Node(name=f's{i}'))
            sub[f's{i}'] = cands[0]
            i += 1
        return self, sub

def mono2exp(m: monodesc) -> Node:
    res = Node(val=m['coef'])
    for v in m:
        if v != 'coef':
            res *= Node(name=v) ** Node(val=m[v])
    return res

def monos2exp(M:list[monodesc]) -> Node:
    if len(M) > 0:
        res = mono2exp(M[0])
        for i in range(1, len(M)):
            res += mono2exp(M[i])
        return res
    return Node()

def canonize(e: Node, f: funcssign, debug=False) -> Node:
    if debug:
        neu, sub = e.polynomize(f)
        for s in sub:
            print(s, ' = ', sub[s])
    else:
        neu = e.copy()
    if neu.is_poly(f):
        neu = neu.deep_opener()
        D = neu.get_all_mono_descs()
        D = descriptor_squash(D)
        monosort(D)
        neu = monos2exp(D)
    else:
        print('cannot canonize')
    return neu


# get expression from postfix notation
def post2node(p: list[str], funcs: dict[str, tuple[int, int]]) -> Node:
    stack:list[Node] = []
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
                operands = [Node()] * args
                params = [Node()] * pars
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
def s2node(inp: str, funcs:funcssign=dict()) -> tuple[Node, funcssign]:
    pol, funcs = inf2post(inp, funcs)
    n = post2node(pol, funcs)
    return n, funcs

if __name__ == "__main__":
    e, f = s2node(inp='x')
    print(e)
    e = canonize(e, f, True)
    print(e)