from polynom import *

global_var_dict = {
    'x1': Var('x1'),
    'x2': Var('x2')
}

library_names = {
    'sin': (1, 'f1'),
    'cos': (1, 'f2'),
    'ln': (2, 'f1'),
    'inv': (2, 'f2')
}

library_RHS = {
    1:{
        'f1': {
            1: 'f2'
        },
        'f2': {
            1: '-f1'
        }
    },
    2: {
        'f1': {
            1: 'f2'
        },
        'f2': {
            1: '-f2^2'
        }
    }
}





# Step 1. Get respective sections and library naming by function names
# assign to them arg lists
functions = {'sin[x2]','cos[x2]', 'ln[x1]'}
parsed1 = dict()
for f in functions:
    fname, j = parse_name(f, 0)
    args = []
    args, j = parse_name(f, j + 1, stop_symbols={']'})
    parsed1[library_names[fname]] = args

# print(parsed1)

# What to do for each function
avs = []
history = dict()
for f in parsed1:
    args = parsed1[f]
    extension = f[0]
    func_in_ext = f[1]
    if extension not in history:
        history[extension] = set()
    # continue processing only if same extension with same arguments haven't been processed before
    if args not in history[extension]:
        history[extension].add(args)
        polyargs = args.split(';')
        for i in range(len(polyargs)):
            polyargs[i] = parse_poly(polyargs[i], global_var_dict)[0]
        # create new additinal variables and place them in correspondence table so we can substitute
        corr_table = dict()
        for v in library_RHS[extension]:
            name = f'q{len(avs)+1}'
            corr_table[v] = name
            avs.append(name)
            global_var_dict[name] = Var(var_name=name, var_args=polyargs, var_deps=dict())
        # get dependencies
        for v in library_RHS[extension]:
            for ind_var in library_RHS[extension][v]:
                name = corr_table[v]
                rhs = library_RHS[extension][v][ind_var]
                # substitute all extension function names for new variables names
                for v1 in library_RHS[extension]:
                    if v1 in rhs:
                        rhs = rhs.replace(v1, corr_table[v1])
                        # print(v1, corr_table[v1], rhs)
                
                global_var_dict[name].var_deps[ind_var - 1] = parse_poly(rhs, global_var_dict)[0]

# print(avs)
# print(global_var_dict)
for v in global_var_dict:
    var = global_var_dict[v]
    if var.var_args != []:
        var.var_deps['x1'] = var.derivative('x1', global_var_dict)
        var.var_deps['x2'] = var.derivative('x2', global_var_dict)
    var.printout()



# Step 2. Clean duplicates (same section and list of arguments)

'''history = set()
to_kill = []
for f in parsed1:
    section = f[0]
    arguments = parsed1[f]
    if (section, arguments) in history:
        to_kill.append(f)
    else:
        history.add((section,arguments))

for f in to_kill:
    parsed1.pop(f)

print(parsed1)'''

# Step 3. For each function define additional variables