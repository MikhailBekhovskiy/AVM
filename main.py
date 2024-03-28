from avreader import find_simple_func, parse_func, introduce_av, put_in_sys_av
from library import library as sublib
from polynom import Var
from parse import read_input, parse_poly, printout_poly_de, printout_poly_func

def de_transform(system: dict, gvd: dict, ivs_num: int):
    avs = dict()
    for x in system:
        for t in system[x]:
            foo = find_simple_func(system[x][t])
            while foo != '':
                foo = parse_func(foo)
                navs = introduce_av(foo, sublib, avs, gvd, mode='DE', ivs_num=ivs_num)
                system = put_in_sys_av(navs, system, 'DE')
                foo = find_simple_func(system[x][t])
    for x in system:
        for t in system[x]:
            poly_rhs = parse_poly(system[x][t])[0]
            system[x][t] = poly_rhs
            gvd[x].var_deps[t] = poly_rhs
    return system, avs


def func_transform(funcs: dict, global_var_dict: dict):
    avs = dict()
    for f in funcs:
        foo = find_simple_func(funcs[f])
        while foo != '':
            foo = parse_func(foo)
            navs = introduce_av(foo, sublib, avs, global_var_dict,mode='F')
            funcs = put_in_sys_av(navs, funcs, 'F')
            foo = find_simple_func(funcs[f])
    for f in funcs:
        funcs[f] = parse_poly(funcs[f])[0]
    return funcs, avs

def av_derivatives(avs: dict, gvd: dict, ind_vars:list):
    res=dict()
    for av in avs:
        res[avs[av]] = dict()
        for iv in ind_vars:
            aVar = gvd[avs[av]]
            der = aVar.derivative(iv, gvd)
            gvd[aVar.name].var_deps[iv] = der
            res[avs[av]][iv] = der
    return res

# currently calculates all 1st order partial derivatives
def og_func_derivatives(sys: dict, ivs: list, gvd:dict) -> dict:
    res = dict()
    for f in sys:
        res[f] = dict()
        for iv in ivs:
            res[f][iv] = sys[f].derivative(iv, gvd)
    return res


if __name__=="__main__":
    # change this to the name of your file. it has to be stored in scrolls/'
    input_name = 'input_de_small.txt'


    m, ivs, sys, gvd = read_input(infname = input_name, debug=False)
    # print(sys)
    # for v in gvd:
    #   print(gvd[v].printout())
    if m == 'F':
        sys, avs = func_transform(sys, gvd)
        for av in avs:
            print(f'{avs[av]} = {av}')
        printout_poly_func(sys)
    else:
        sys, avs = de_transform(sys, gvd, ivs_num=len(ivs))
        for av in avs:
            print(f'{avs[av]} = {av}')
        printout_poly_de(sys)
    
    # print(avs)
    
    av_ders = av_derivatives(avs, gvd, ivs)
    printout_poly_de(av_ders)

    if m == 'F':
        jacobi = og_func_derivatives(sys, ivs, gvd)
        printout_poly_de(jacobi)