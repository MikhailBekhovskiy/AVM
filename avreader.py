from polynom import Polynomial, Var

# TODO The proper library loading mechanism
from library import library, get_ext_by_fname
from parse import find_simple_func, parse_func, parse_poly


# TODO testing;
# function for filling dictionary with new AV by function symbolic description
def introduce_av(f: tuple[str,str], lib: tuple[dict, dict], avs: dict, 
                 global_var_dict: dict[str:Var], mode='F', ivs_num=0, debug=False) -> dict:
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
            # name = f'q{len(avs)}'
            name = f'x{len(global_var_dict) + 1}'
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
            if debug:
                print(rhs)
    return new_avs

# TODO testing
# puts AV in user system
def put_in_av(new_avs: dict, expression: str)->str:
    new_exp = expression
    for func in new_avs:
        if func in expression:
            new_exp = new_exp.replace(func, new_avs[func])
    return new_exp

def put_in_sys_av(new_avs: dict, exprs: dict)->dict:
    new_exprs = dict()
    for e in exprs:
        new_exprs[e] = put_in_av(new_avs, exprs[e])
    return new_exprs

# for testing
if __name__ == "__main__":
    # examples input data
    '''
    # variables dictionaries; will be read from input system initially
    global_var_dict = {'x1': Var('x1'), 'x2': Var('x2')}
    avs = dict()
    exprs = ['x1^5*sin[x2]', 'ln[x1]^3*cos[x2]']
    ind = ['x1', 'x2']
    # calculate func derivatives
    poly_expr = dict()
    for i in range(len(exprs)):
        poly_expr[f'y{i}'] = parse_poly(exprs[i])[0]
    for poly in poly_expr:
        print(poly_expr[poly].printout())
    for foo in poly_expr:
        for iv in ind:
            der = poly_expr[foo].derivative(iv, global_var_dict)
            res = f'd{foo}/d{iv} = {der.printout()}'
            print(res)
    '''

    global_var_dict = {'x1': Var('x1'), 'x2': Var('x2'), 'x3': Var('x3')}
    avs = dict()
    exprs = {'y1':'x3^3*sin[cos[a*ln[x2]^2 + b*x3]] + x3^3*b*ln[x2]^4 + sin[a*ln[x2]^2 + b*x3]^5 + Dv[x1]',
             'y2':'sin[cos[a*ln[x2]^2 + b*x3]] + b*ln[x2]^4 + sin[a*ln[x2]^2 + b*x3]^5 + Dv[x1]',
             'y3':'x2^2*cos[sin[a*ln[x2]^2 + b*x3]] + cos[a*ln[x2]^2 + b*x3]^4 + EK[sin[sin[a*ln[x2]^2 + b*x3]];x1]^2',
             'y4':'x2^2*cos[sin[a*ln[x2]^2 + b*x3]] + cos[a*ln[x2]^2 + b*x3]^4 + EK[sin[sin[a*ln[x2]^2 + b*x3]];x1]',
             'y5':'x1^2*ch[a*ln[x2]^2 + b*x3]^2 + x1^2*sin[a*ln[x2]^2 + b*x3] + sh[a*ln[x2]^2 + b*x3]^5',
             'y6':'x1*ch[a*ln[x2]^2 + b*x3]^2 + x1*sin[a*ln[x2]^2 + b*x3] + sh[a*ln[x2]^2 + b*x3]^5'}
    ind = ['x1', 'x2', 'x3']


    # introduce av 
    for i in exprs:
        foo = find_simple_func(exprs[i])
        while foo != '':
        # print(foo)
            foo = parse_func(foo)
            navs = introduce_av(foo, library, avs, global_var_dict, debug=False)
            exprs = put_in_sys_av(navs, exprs)
            # print(exprs)
            foo = find_simple_func(exprs[i])
    # calculate av derivatives
    print(avs)
    poly_expr = dict()
    for i in exprs:
        poly_expr[i] = parse_poly(exprs[i])[0]
    for poly in poly_expr:
        print(poly, '=', poly_expr[poly].printout())
    
    for av in avs:
        for iv in ind:
            aVar = global_var_dict[avs[av]]
            der = aVar.derivative(iv, global_var_dict, debug=False)
            global_var_dict[aVar.name].var_deps[iv] = der
            res = f'd{aVar.name}/d{iv} = {der.printout()}'
            # print(res)
    
    for poly in poly_expr:
        for iv in ind:
            res = f'd{poly}/{iv}'
            der = poly_expr[poly].derivative(iv, global_var_dict)
            res += '=' + der.printout()
            print(res)