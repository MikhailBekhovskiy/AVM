# class for system description; currently only DE systems are supported
from proto_tree import *
from library import *

# Independent variables: comma separated values; obsolete
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
    # lhs varnames from parser methods are added
    # d{depvar}/d{indvar} = eqrhs
    # {depvar} = frhs
    # add vars stores definitions of additional variables
    def __init__(self, desc=[], filename='scrolls/input.txt'):
        if desc == []:
            desc = file_scanner(filename)
        self.dep_vars = set()
        self.ind_vars = set()
        self.add_vars = dict()
        self.eqs = dict()
        # multivariate function to be analyzed
        self.fs = dict()
        # func names storage
        self.funcs = dict()
        for i in range(len(desc)):
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
        for f in self.fs:
            vars = self.fs[f].var_detector()
            for v in vars:
                if v not in self.dep_vars and v not in self.ind_vars:
                    self.ind_vars.add(v)

    def __str__(self):
        res = 'Dependent variables:\n' + str(self.dep_vars) + '\n'
        res += 'Independent variables:\n' + str(self.ind_vars) + '\n'
        if len(self.add_vars) > 0:
            res += 'Additional variables:\n'
            for av in self.add_vars:
                res += f'{av}: {str(self.add_vars[av])}\n'
        if len(self.funcs) > 0:
            res += 'Detected functions:\n' + str(self.funcs) + '\n'
        for mv in self.fs:
            res += f'{mv} = ' + str(self.fs[mv]) + '\n'
        for mv in self.eqs:
            for sv in self.eqs[mv]:
                res += f'd{mv}/d{sv} = ' + str(self.eqs[mv][sv]) + '\n'
        return res[:-1]
    
    # automatic rhs var detector
    def var_detector(self):
        vars = set()
        for f in self.fs:
            vars = vars.union(self.fs[f].var_detector())
        for x in self.eqs:
            for t in self.eqs[x]:
                vars = vars.union(self.eqs[x][t].var_detector())
        for v in vars:
            if v not in self.ind_vars and v not in self.dep_vars:
                self.ind_vars.add(v)
        return vars
    
    # deep copy
    def copy(self):
        neu = System()
        neu.dep_vars = self.dep_vars.copy()
        neu.ind_vars = self.ind_vars.copy()
        neu.funcs = self.funcs.copy()
        neu.add_vars = dict()
        for av in self.add_vars:
            neu.add_vars[av] = self.add_vars[av].copy()
        neu.fs = dict()
        for f in self.fs:
            neu.fs[f] = self.fs[f].copy()
        neu.eqs = dict()
        for x in self.eqs:
            neu.eqs[x] = dict()
            for t in self.eqs[x]:
                neu.eqs[x][t] = self.eqs[x][t].copy()
        return neu

    # check whether system is polynomial
    def is_poly(self):
        for mv in self.eqs:
            for sv in self.eqs[mv]:
                if not self.eqs[mv][sv].is_poly(self.funcs):
                    return False
        for mv in self.fs:
            if not self.fs[mv].is_poly(self.funcs):
                return False
        return True

    # add polynomial equation to the system
    def add_eq(self, mv, sv, rhs):
        if mv not in self.dep_vars:
            self.dep_vars.add(mv)
            self.add_vars.add(mv)
        if sv not in self.ind_vars:
            self.ind_vars.add(sv)
        self.eqs[mv][sv] = rhs
        return self

    # add polynomial function to the system
    def add_f(self, mv, rhs):
        if mv not in self.dep_vars:
            self.dep_vars.add(mv)
            self.add_vars.add(mv)
        self.fs[mv] = rhs
        return self
    
    # system wide dependent variable change;
    def change_dep_var_name(self, old_var, new_var):
        neu = self.copy()
        neu.eqs[new_var] = dict()
        for mv in neu.eqs:
            for sv in neu.eqs[mv]:
                if mv == old_var:
                    neu.eqs[new_var][sv] = neu.eqs[mv][sv].substitute(Node(name=old_var), Node(name=new_var))
                else:
                    neu.eqs[mv][sv] = neu.eqs[mv][sv].substitute(Node(name=old_var), Node(name=new_var))
        for mv in neu.fs:
            if mv == old_var:
                neu.fs[new_var] = neu.fs[mv].substitute(Node(name=old_var), Node(name=new_var))
            else:
                neu.fs[mv] = neu.fs[mv].substitute(Node(name=old_var), Node(name=new_var))
        if old_var in neu.eqs:
            del neu.eqs[old_var]
        if old_var in neu.fs:
            del neu.fs[old_var]
        neu.dep_vars.remove(old_var)
        neu.dep_vars.add(new_var)
        if old_var in self.add_vars:
            neu.add_vars.remove(old_var)
            neu.add_vars.add(new_var)
        return neu

    # change set is a DICTIONARY
    def bulk_change_dep_var_name(self, vars: dict):
        neu = self.copy()
        for v in vars:
            neu = neu.change_dep_var_name(v, vars[v])
        return neu

    # systemwide substitution; returns NEW instance; doesnt update variables
    # var update explicitly handled on av insertion step
    def substitute(self, old_exp, new_exp):
        neu = self.copy()
        for mv in neu.eqs:
            for sv in neu.eqs[mv]:
                neu.eqs[mv][sv] = neu.eqs[mv][sv].substitute(old_exp, new_exp)
        for mv in neu.fs:
            neu.fs[mv] = neu.fs[mv].substitute(old_exp, new_exp)
        if new_exp.name != 'num' and len(new_exp.kids) == 0 and new_exp.name not in neu.dep_vars:
            neu.dep_vars.add(new_exp.name)
            neu.add_vars[new_exp.name] = old_exp
        return neu

    # get right hand side with functions in it
    def get_non_poly_rhs(self):
        for mv in self.eqs:
            for sv in self.eqs[mv]:
                if not self.eqs[mv][sv].is_poly(self.funcs):
                    return self.eqs[mv][sv]
        for mv in self.fs:
            if not self.fs[mv].is_poly(self.funcs):
                return self.fs[mv]
        return None

    # introduce and insert additional variables to polynomize systems
    # parametre insertion not supported yet
    def insert_av(self, loaded_lib):
        S = self.copy()
        L = loaded_lib
        replaced = []
        while not S.is_poly():
            E = S.get_non_poly_rhs()
            cand = [E.find_poly_funcs(S.funcs)[0]]
            ext = L[0][cand[0].name][2]
            syst = L[0][cand[0].name][0]
            cand += [None] * len(ext)
            for i in range(len(ext)):
                cand[i+1] = cand[0].copy()
                cand[i+1].name = ext[i]
            replaced.append((dict(), cand[0].kids, syst, cand[0].parameters))
            for c in cand:
                vname = f's{len(S.add_vars) + 1}'
                replaced[len(replaced)-1][0][vname] = c
                nmv = Node(name=vname)
                S = S.substitute(c, nmv)
        return S, replaced

    # calculate single additional variable extension derivatives
    def ext_ders(self, ext: tuple, loaded_lib):
        LS = System(desc = loaded_lib[1][ext[2]])
        E = ext[0]
        A = ext[1]
        arg_ders = [None] * len(A)
        i = 0
        for a in A:
            arg_ders[i] = dict()
            for t in S.ind_vars:
                arg_ders[i][t] = a.poly_derivative(t, self.eqs)
            i += 1
        exps_old = [None] * (len(E) + len(LS.ind_vars) + len(ext[3]))
        exps_new = [None] * (len(E) + len(LS.ind_vars) + len(ext[3]))
        i = 0
        for av in E:
            exps_new[i] = Node(name=av)
            exps_old[i] = Node(name=loaded_lib[0][E[av].name][1])
            i += 1
        for t in LS.ind_vars:
            exps_old[i] = Node(name=t)
            if t == 't':
                exps_new[i] = A[0]
            else:
                exps_new[i] = A[int(t[1:])-1]
            i += 1
        for j in range(i, len(exps_old)):
            exps_old[j] = Node(name=f'p{j-i+1}')
            exps_new[j] = ext[3][j-i]
        for i in range(len(E)):
            avname = exps_new[i].name
            self.eqs[avname] = dict()
            for t in self.ind_vars:
                self.eqs[avname][t] = Node(val=0)
                for j in range(len(E), len(E) + len(LS.ind_vars)):
                    self.eqs[avname][t] += LS.eqs[exps_old[i].name][exps_old[j].name].bulk_substitute(exps_old, exps_new) * arg_ders[j - len(E)][t]    

    # calculate all additional variable derivatives
    def av_ders(self, avs: list, loaded_lib):
        for ext in avs:
            S.ext_ders(ext, loaded_lib)

    # system-wide parentheses opener
    def open_parenth(self):
        for x in self.eqs:
            for t in self.eqs[x]:
                self.eqs[x][t] = self.eqs[x][t].open_parenth()
        for f in self.fs:
            self.fs[f] = self.fs[f].open_parenth()

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
    S, R = S.insert_av(lib_na)
    print(R)
    # print(R)
    S.av_ders(R, lib_na)
    # S.open_parenth()
    print(S)

