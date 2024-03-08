from polynom import Var, parse_poly

# TODO The proper library loading mechanism
from library import library, get_ext_by_fname


# TODO
# this is a function to get functions with polynomial arguments from an expression
# for optimization; base version introduces avs based on first poly_func encounter
def get_candidates(rhs: str) -> set:
    pass

# TODO testing;
# function for filling dictionary with new AV by function symbolic description
def introduce_av(f: tuple[str,str], lib: tuple[dict, dict], avs: dict, 
                 global_var_dict: dict[str:Var]) -> dict:
    fnames = [f[0]]
    args = f[1]
    new_avs = dict()
    ext = get_ext_by_fname(fnames[0], lib)
    for fu in ext:
        fnames.append(fu)
    sec = lib[0][fnames[0]][0]

    polyargs = args.split(';')
    for i in range(len(polyargs)):
        polyargs[i] = parse_poly(polyargs[i])[0]
    
    # name all new AVs
    cor_table = dict()
    for fu in fnames:
        func = fu + '[' + args + ']'
        if func not in avs:
            name = f'q{len(avs)}'
            avs[func] = name
            cor_table[lib[0][fu][1]] = name
            global_var_dict[name] = Var(name, dict(), polyargs)
            new_avs[func] = name
        else:
            cor_table[lib[0][fu][1]] = avs[func]

    # get dependencies using assigned names
    for v in lib[1][sec]:
        for i_v in lib[1][sec][v]:
            name = cor_table[v]
            rhs = lib[1][sec][v][i_v]
            for v1 in lib[1][sec]:
                if v1 in rhs:
                    rhs = rhs.replace(v1, cor_table[v1])
            global_var_dict[name].var_deps[i_v] = parse_poly(rhs)[0]
    return new_avs

# TODO testing
# puts AV in user system
def put_in_av(new_avs: dict, expression: str):
    new_exp = expression
    for func in new_avs:
        if func in expression:
            new_exp = new_exp.replace(func, new_avs[func])
    return new_exp

# for testing
if __name__ == "__main__":
    # variables dictionaries; will be read from input system initially
    global_var_dict = {'x1': Var('x1'), 'x2': Var('x2')}
    avs = dict()
    foos = [('sin', 'x2'),('ln', 'x1')]
    expr = 'y2 = ln[x1]^3 + sin[x2]'
    ind = ['x1', 'x2']

    for f in foos:
        navs = introduce_av(f, library, avs, global_var_dict)
        expr = put_in_av(navs, expr)
    print(avs)
    print(expr)
    for iv in ind:
        for av in avs:
            aVar = global_var_dict[avs[av]]
            der = aVar.derivative(iv, global_var_dict)
            global_var_dict[aVar.name].var_deps[iv] = der
            res = f'd{aVar.name}/d{iv} = {der.printout()}'
            print(res)