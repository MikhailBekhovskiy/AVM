# class for system description; currently only DE systems are supported
from proto_tree import *
from library import *

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

# generate mixed system by text description
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
    # constructor optionally takes filename
    def __init__(self, desc=[], filename='scrolls/input.txt'):
        if desc == []:
            desc = file_scanner(filename)
        self.dep_vars = set()
        self.ind_vars = set()
        self.eqs = dict()
        self.funcs = dict()
        for eq in desc:
            mv, sv, rhs, self.funcs = str2eq(eq, self.funcs)
            if mv not in self.eqs:
                self.eqs[mv] = dict()
            if sv != '':
                self.eqs[mv][sv] = rhs
                if sv not in self.ind_vars:
                    self.ind_vars.add(sv)
            else:
                self.eqs[mv] = rhs
            if mv not in self.dep_vars:
                self.dep_vars.add(mv)

    def __str__(self):
        res = 'Dependent variables:\n' + str(self.dep_vars) + '\n'
        res += 'Independent variables:\n' + str(self.ind_vars) + '\n'
        res += 'Detected functions:\n' + str(self.funcs) + '\n'
        for mv in self.eqs:
            if type(self.eqs[mv]) is dict:
                for sv in self.eqs[mv]:
                    res += f'd{mv}/d{sv} = ' + str(self.eqs[mv][sv]) + '\n'
            else:
                res += f'{mv} = ' + str(self.eqs[mv]) + '\n'
        return res[:-1]

    # check whether system is polynomial
    def is_poly(self):
        for mv in self.eqs:
            for sv in self.ind_vars:
                if mv in self.eqs and type(self.eqs[mv]) is dict and sv in self.eqs[mv]:
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
                for sv in self.ind_vars:
                    if mv in self.eqs and sv in self.eqs[mv]:
                        self.eqs[mv][sv] = self.eqs[mv][sv].substitute(old_exp, new_exp)
            elif type(self.eqs[mv]) is Node:
                self.eqs[mv] = self.eqs[mv].substitute(old_exp, new_exp)
        return self

    # get right hand side with functions in it
    def get_non_poly_rhs(self):
        for mv in self.eqs:
            if type(self.eqs[mv]) is dict:
                for sv in self.ind_vars:
                    if mv in self.eqs and sv in self.eqs[mv]:
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
            cand += [None] * len(ext)
            for i in range(len(ext)):
                cand[i+1] = cand[0].copy()
                cand[i+1].name = ext[i]
            for c in cand:
                vname = f's{len(S.dep_vars) + 1}'
                replaced.append((vname, c))
                lib_name = L[0][c.name][1]
                L[0][c.name][1] = vname
                L[1][L[0][c.name][0]] = L[1][L[0][c.name][0]].change_var_name(lib_name, vname)
                nmv = Node(name=vname)
                S = S.substitute(c, nmv)
                S.dep_vars.add(nmv.name)
        return S, L, replaced

    # calculate single additional variable derivative
    def av_der(self, sv: str, av: tuple, loaded_lib: tuple):
        avn = av[0]
        avf = av[1]
        lib_name = loaded_lib[0][avf.name]
        lib_sys = loaded_lib[1][lib_name[0]]
        args = avf.kids
        arg_ders = [a.poly_derivative(sv, self.eqs) for a in args]
        pos_ders = [None] * len(arg_ders)
        res = Node(val=0.)
        if len(avf.kids) == 1:
            pos_ders[0] = lib_sys.eqs[avn]['t'].substitute(Node(name='t'), avf.kids[0])
        else:
            lib_inds = [Node(name=f't{i+1}') for i in range(len(avf.kids))]
            for i in range(len(avf.kids)):
                pos_ders[i] = lib_sys.eqs[avn][f't{i+1}'].bulk_substitute(lib_inds, avf.kids)
        for i in range(len(avf.kids)):
            res += arg_ders[i] * pos_ders[i]
        return res

    # calculate all additional variable derivatives
    def av_ders(self, avs: list, loaded_lib: tuple):
        for av in avs:
            self.eqs[av[0]] = dict()
            for sv in self.ind_vars:
                self.eqs[av[0]][sv] = self.av_der(sv, av, loaded_lib)
        return self

# generate system from library descriptor
def load_lib_systems(lib: tuple):
    res = [None] * len(lib[1])
    for i in range(len(lib[1])):
        res[i] = System(desc=lib[1][i])
    return res




if __name__ == "__main__":
    S = System()
    L = expand_sub_lib(S.funcs, lib_na)
    L = L[0], load_lib_systems(L)
    # print(S)
    # print(S.is_poly())
    S, L, replaced = S.insert_av(L)
    S = S.av_ders(replaced, L)
    print(S)
    #print(L)
    print('Additional variables definition:')
    for r in replaced:
        print(r[0], ' = ', r[1])