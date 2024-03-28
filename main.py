from avreader import find_simple_func, parse_func, introduce_av, put_in_sys_av
from library import library as sublib
from polynom import Var
from parse import read_input, parse_poly, printout_poly_de, printout_poly_func

def func_transform(funcs: dict, global_var_dict: dict):
    avs = dict()
    for f in funcs:
        foo = find_simple_func(funcs[f])
        while foo != '':
            foo = parse_func(foo)
            navs = introduce_av(foo, sublib, avs, global_var_dict)
            funcs = put_in_sys_av(navs, funcs)
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
    m, ivs, sys, gvd = read_input(infname = 'input_small.txt', debug=False)
    # print(sys)
    # for v in gvd:
    #   print(gvd[v].printout())
    sys, avs = func_transform(sys, gvd)
    for av in avs:
        print(f'{avs[av]} = {av}')
    printout_poly_func(sys)
    # print(avs)
    
    av_ders = av_derivatives(avs, gvd, ivs)
    printout_poly_de(av_ders)

    jacobi = og_func_derivatives(sys, ivs, gvd)
    printout_poly_de(jacobi)