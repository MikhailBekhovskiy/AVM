from polynom import Var, parse_poly
from parse import parse_name

# TODO The proper library loading mechanism
from library import library, global_var_dict

# TODO
# this is a function to get functions with polynomial arguments from an expression
def get_candidates(rhs: str) -> set:
    pass

# TODO testing; factorize
# function for filling dictionary with new AV by function symbolic description
def introduce_av(f: str, lib: tuple[dict], avs: list[str], 
                 global_var_dict: dict[str:Var]):
    fname, j = parse_name(f, 0)
    args, j = parse_name(f, j+1, stop_symbols={']'})

    ext = lib[0][fname][0]

    polyargs = args.split(';')
    for i in range(len(polyargs)):
        polyargs[i] = parse_poly(polyargs[i])[0]
    
    # name all new AVs
    cor_table = dict()
    for v in lib[1][ext]:
        name = f'q{len(avs)}'
        avs.append(name)
        cor_table[v] = name
        global_var_dict[name] = Var(name, dict(), polyargs)

    # get dependencies using assigned names
    for v in lib[1][ext]:
        for i_v in lib[1][ext][v]:
            name = cor_table[v]
            rhs = lib[1][ext][v][i_v]
            for v1 in lib[1][ext]:
                if v1 in rhs:
                    rhs = rhs.replace(v1, cor_table[v1])
            global_var_dict[name].var_deps[i_v] = parse_poly(rhs, global_var_dict)[0]


# TODO 
# puts AV in user system
def putin_av(phi: Var, system):
    pass

# for testing
if __name__ == "__main__":
    pass