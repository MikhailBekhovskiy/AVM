# class for system description; currently only DE systems are supported
from proto_tree import *
from library import *

# Independent variables: comma separated values
def str2vars(inp: str, ind: bool) -> set:
    if ind:
        # set pointer after 'independent variables:'
        i = len('independent variables:')
    else:
        # set pointer after 'dependent variables:'
        i = len('dependent variables:')
    vars = set()
    while i < len(inp) and inp[i] != '\n':
        while inp[i] == ' ' or inp[i] == ',':
            i += 1
        var = ''
        while i < len(inp) and inp[i] != ' ' and inp[i] != ',' and inp[i] != '\n':
            var += inp[i]
            i += 1
        if var not in vars:
            vars.add(var)
    return vars

# str2eq and str2f return lhs varnames as well
# dxi/dti = f(x)
def str2eq(inp: str, funcs=dict()) -> tuple[str, str, Node, dict]:
    i = 0
    while i < len(inp) and (inp[i] == ' ' or inp[i] == 'd'):
        i += 1
    main_var = ''
    while i < len(inp) and inp[i] != ' ' and inp[i] != '/' and inp[i] != '=':
        main_var += inp[i]
        i += 1
    while i < len(inp) and (inp[i] == ' ' or inp[i] == 'd' or inp[i] == '/'):
        i += 1
    sec_var = ''
    if inp[i] != '=':
        while i < len(inp) and inp[i] != ' ' and inp[i] != '=':
            sec_var += inp[i]
            i += 1
    while i < len(inp) and (inp[i] == ' ' or inp[i] == '='):
        i += 1
    rhs = inp[i:]
    rhs = s2node(rhs, funcs)
    return main_var, sec_var, rhs[0], rhs[1]

# yi = f(x)
def str2f(inp: str, funcs=dict()) -> tuple[str, Node, dict]:
    i = 0
    while i < len(inp) and inp[i] == ' ':
        i += 1
    mainvar = ''
    while i < len(inp) and inp[i] != ' ' and inp[i] != '=':
        mainvar += inp[i]
        i += 1
    while i < len(inp) and (inp[i] == ' ' or inp[i] == '='):
        i += 1
    rhs = inp[i:]
    rhs = s2node(rhs, funcs)
    return mainvar, rhs[0], rhs[1]

# generate mixed system by text description
def file_scanner(filename='scrolls/input.txt') -> list:
    with open(filename, 'r') as f:
        F = f.readlines()
    res = []
    for i in range(len(F)):
        if F[i] == '' or F[i] == '\n':
            continue
        elif F[i][-1] == '\n':
            res.append(F[i][:-1])
        else:
            res.append(F[i])
    return res

class System():
    # constructor optionally takes filename
    # lhs varnames from parser methods are added if they werent accounted for in variable rows
    # d{depvar}/d{indvar} = eqrhs
    # {depvar} = frhs
    def __init__(self, desc=[], filename='scrolls/input.txt'):
        if desc == []:
            desc = file_scanner(filename)
        self.dep_vars = str2vars(desc[1], ind=False)
        self.ind_vars = str2vars(desc[0], ind=True)
        self.eqs = dict()
        # multivariate function to be analyzed
        self.fs = dict()
        # func names storage
        self.funcs = dict()
        for i in range(2, len(desc)):
            # equation marker
            if '/' in desc[i]:
                mv, sv, rhs, self.funcs=str2eq(desc[i], self.funcs)
                if mv not in self.dep_vars:
                    self.dep_vars.add(mv)
                if sv not in self.ind_vars:
                    self.ind_vars.add(sv)
                if not mv in self.eqs:
                    self.eqs[mv] = dict()
                self.eqs[mv][sv] = rhs
            # else function
            else:
                mv, rhs, self.funcs = str2f(desc[i], self.funcs)
                if mv not in self.dep_vars:
                    self.dep_vars.add(mv)
                self.fs[mv] = rhs

    def __str__(self):
        res = 'Dependent variables:\n' + str(self.dep_vars) + '\n'
        res += 'Independent variables:\n' + str(self.ind_vars) + '\n'
        res += 'Detected functions:\n' + str(self.funcs) + '\n'
        for mv in self.fs:
            res += f'{mv} = ' + str(self.fs[mv]) + '\n'
        for mv in self.eqs:
            for sv in self.eqs[mv]:
                res += f'd{mv}/d{sv} = ' + str(self.eqs[mv][sv]) + '\n'
        return res[:-1]

    # check whether system is polynomial
    def is_poly(self):
        for mv in self.eqs:
            if type(self.eqs[mv]) is dict:
                for sv in self.eqs[mv]:
                    if not self.eqs[mv][sv].is_poly(self.funcs):
                        return False
            elif type(self.eqs[mv]) is Node and not self.eqs[mv].is_poly(self.funcs):
                    return False
        return True

    # add equation to the system
    def add_eq(self, mv, sv, rhs):
        if mv not in self.dep_vars:
            self.dep_vars.add(mv)
        if sv != '':
            if sv not in self.ind_vars:
                self.ind_vars.add(sv)
            self.eqs[mv][sv] = rhs
        else:
            self.eqs[mv] = rhs
        return self

    # systemwide substitution
    def substitute(self, old_exp, new_exp):
        for mv in self.eqs:
            if type(self.eqs[mv]) is dict:
                for sv in self.eqs[mv]:
                    self.eqs[mv][sv] = self.eqs[mv][sv].substitute(old_exp, new_exp)
            elif type(self.eqs[mv]) is Node:
                self.eqs[mv] = self.eqs[mv].substitute(old_exp, new_exp)
        return self

    # get right hand side with functions in it
    def get_non_poly_rhs(self):
        for mv in self.eqs:
            if type(self.eqs[mv]) is dict:
                for sv in self.eqs[mv]:
                    if not self.eqs[mv][sv].is_poly(self.funcs):
                        return self.eqs[mv][sv]
            elif type(self.eqs[mv]) is Node:
                if not self.eqs[mv].is_poly(self.funcs):
                    return self.eqs[mv]
        return None

    # system wide variable change
    def change_var_name(self, old_var, new_var):
        self.eqs[new_var] = dict()
        for mv in self.eqs:
            if type(self.eqs[mv]) is dict:
                for sv in self.eqs[mv]:
                    if mv == old_var:
                        self.eqs[new_var][sv] = self.eqs[mv][sv].substitute(Node(name=old_var), Node(name=new_var))
                    else:
                        self.eqs[mv][sv] = self.eqs[mv][sv].substitute(Node(name=old_var), Node(name=new_var))
            elif type(self.eqs[mv]) is Node:
                if mv == old_var:
                    self.eqs[new_var] = self.eqs[mv].substitute(Node(name=old_var), Node(name=new_var))
                else:
                    self.eqs[mv] = self.eqs[mv].substitute(Node(name=old_var), Node(name=new_var))
        del self.eqs[old_var]
        self.dep_vars.remove(old_var)
        self.dep_vars.add(new_var)
        return self

    # introduce and insert additional variables to polynomize systems
    # parametre insertion not supported yet
    def insert_av(self, loaded_lib):
        S = self
        L = loaded_lib
        replaced = []
        while not S.is_poly():
            E = S.get_non_poly_rhs()
            cand = [E.find_poly_func(S.funcs)[0]]
            ext = L[0][cand[0].name][2]
            syst = L[0][cand[0].name][0]
            cand += [None] * len(ext)
            for i in range(len(ext)):
                cand[i+1] = cand[0].copy()
                cand[i+1].name = ext[i]
            replaced.append((dict(), syst))
            for c in cand:
                vname = f's{len(S.dep_vars) + 1}'
                replaced[len(replaced)-1][0][vname] = c
                nmv = Node(name=vname)
                S = S.substitute(c, nmv)
                S.dep_vars.add(nmv.name)
        return S, replaced

    # calculate single additional variable extension derivatives
    def av_ders(self, ext: list, loaded_lib):
        pass

    # calculate all additional variable derivatives
    def av_ders(self, avs: list, loaded_lib):
        pass

# generate system from library descriptor
def load_lib_systems(lib):
    res = [None] * len(lib[1])
    for i in range(len(lib[1])):
        res[i] = System(desc=lib[1][i])
    return res

def print_av(replaced: tuple):
    for v in replaced[0]:
        print(v, ' = ', replaced[0][v], '; system number ', replaced[1])

def print_avs(replaced: list):
    print('Additional variables definition:')
    for i in range(len(replaced)):
        print(f'Extension #{i}:')
        print_av(replaced[i])

if __name__ == "__main__":
    S = System()
    print(S)