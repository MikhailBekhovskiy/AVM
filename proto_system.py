# class for system description
from proto_tree import *

# dxi/dti = f(x)
def str2eq(inp: str, funcs=dict()) -> tuple[str, str, Node, dict]:
    i = 0
    while i < len(inp) and (inp[i] == ' ' or inp[i] == 'd'):
        i += 1
    main_var = ''
    while i < len(inp) and inp[i] != ' ' and inp[i] != '/':
        main_var += inp[i]
        i += 1
    while i < len(inp) and (inp[i] == ' ' or inp[i] == 'd' or inp[i] == '/'):
        i += 1
    sec_var = ''
    while i < len(inp) and inp[i] != ' ' and inp[i] != '=':
        sec_var += inp[i]
        i += 1
    while i < len(inp) and (inp[i] == ' ' or inp[i] == '='):
        i += 1
    rhs = inp[i:]
    rhs = s2node(rhs, funcs)
    return main_var, sec_var, rhs[0], rhs[1]

def file_scanner(filename='scrolls/input.txt') -> list:
    with open(filename, 'r') as f:
        res = f.readlines()
    for i in range(len(res)):
        if res[i] == '':
            res = res[:i] + res[i+1:]
        elif res[i][-1] == '\n':
            res[i] = res[i][:-1]
    return res

class System():
    def __init__(self, desc: list):
        self.dep_vars = set()
        self.ind_vars = set()
        self.eqs = dict()
        self.funcs = dict()
        for eq in desc:
            mv, sv, rhs, self.funcs = str2eq(eq, self.funcs)
            if mv not in self.eqs:
                self.eqs[mv] = dict()
            self.eqs[mv][sv] = rhs
            if mv not in self.dep_vars:
                self.dep_vars.add(mv)
            if sv not in self.ind_vars:
                self.ind_vars.add(sv)
        for mv in self.dep_vars:
            if mv not in self.eqs:
                self.eqs[mv] = dict()
            for sv in self.ind_vars:
                if sv not in self.eqs[mv]:
                    self.eqs[mv][sv] = Node(val=0.)

    def __str__(self):
        res = 'Dependent variables:\n' + str(self.dep_vars) + '\n'
        res += 'Independent variables:\n' + str(self.ind_vars) + '\n'
        res += 'Detected functions:\n' + str(self.funcs) + '\n'
        for mv in self.eqs:
            for sv in self.eqs[mv]:
                res += f'd{mv}/d{sv} = ' + str(self.eqs[mv][sv]) + '\n'
        return res[:-1]




if __name__ == "__main__":
    desc = file_scanner()
    S = System(desc)
    print(S)