# this is a third iteration of polynomial representation;
# evaluation tree as common in other symbolic packages
# because earlier realization has proven to be quite discombobulating when it came to parsing
# Node is a token of several possible origins: dependent variable (with children and dependencies)
# independent variable (without children and dependencies, i.e. all its derivatives are 0, might be numeric or a parameter)
# n-nary operation (functions to be replaced by additional variables, +, *, - to stay)
binary_ops = {'+', '-', '*', '/', '^'}
unary_ops = {'u-'}
priorities = {
    '+': 0,
    '-': 0,
    'u-': 1,
    '*': 2,
    '/': 2,
    '^': 3
}

class Node():
    def __init__(self, name=None, val=None, children=[], deps=dict()):
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
            for k in self.kids:
                res += k.__str__() + '; '
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


if __name__ == "__main__":
    pass