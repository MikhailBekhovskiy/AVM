from polynom import Var, Monomial, Polynomial

# get a number from string
def parse_num(st: str, start: int) -> tuple[float, int]:
    res = ''
    i = start
    while i < len(st) and ((st[i] >= '0' and st[i] <= '9') or st[i] == '.'):
        res += st[i]
        i += 1
    return float(res), i

# get a word from string from start index to stop symbol
def parse_name(st: str, start: int, stop_symbols={'^', '[', ']', ' ', '*'},
               backwards=False) -> tuple[str, int]:
    res = ''
    i = start
    while i < len(st) and st[i] not in stop_symbols:
        if backwards:
            res = st[i] + res
            if i > 0:
                i -= 1
            else:
                break
        else:
            res += st[i]
            i += 1
    return res, i

# check whether string contains function definitions
# function definitions must be followed by []
# (for checking arguments polynomiality)
def poly_check(expr: str) -> bool:
    if '[' in expr:
        return False
    return True

# returns string containing full function expression (with [] and arguments)
def find_simple_func(expr: str, start=0)->str:
    i = start
    func = ''
    while i < len(expr) and expr[i] != '[':
        i += 1
    if i < len(expr) and expr[i] == '[':
        args = parse_name(expr, i+1, stop_symbols={']'})
        if poly_check(args[0]):
            func = parse_name(expr, i-1, stop_symbols={' ', '*', '['}, backwards=True)[0]
            func += '[' + args[0] + ']'
        else:
            args = parse_name(expr, args[1] - 1, stop_symbols={'['}, backwards=True)
            func = parse_name(expr, args[1] - 1, stop_symbols={' ', '*', '['}, backwards=True)[0]
            func += '[' + args[0] + ']'
    return func

# returns tuple (func_name, func_args)
def parse_func(func: str) -> tuple[str, str]:
    fname, i = parse_name(func, 0, stop_symbols={'['})
    args = parse_name(func, i + 1, stop_symbols={']'})[0]
    return (fname, args)

def parse_mon(st: str, start: int, is_positive: bool, stop_symbs={' ', '+', '-'}) -> tuple[Monomial, int]:
    i = start
    var_pow_list = []
    # read coefficient; if substring begins NOT with a number, then coefficient was omitted, thus 1
    if st[start] > '9' or st[start] < '0':
        coef = 1.
    else:
        res = parse_num(st, start)
        coef = res[0]
        i = res[1]
        i += 1
    # the sign is read between the monomials
    if not is_positive:
        coef *= -1
    # read variables part; monomial ends with space
    while i < len(st) and st[i] not in stop_symbs:
        if st[i] == '*':
            i += 1
        res = parse_name(st, i)
        name = res[0]
        i = res[1]
        # if power is not specified, then it's 1
        if i >= len(st) or st[i] != '^': 
            power = 1
        else:
            i += 1
            res = parse_num(st, i)
            power = int(res[0])
            i = res[1]
        var_pow_list.append((name, power))
    return Monomial(coef, var_pow_list), i    

def parse_poly(st:str, start=0) -> tuple[Polynomial, int]:
    mon_list = []
    is_positive = True
    i = start
    # polynomial ends at EOS or as function argument
    while i < len(st) and st[i] != ']' and st[i] != ';':
        # move to beginning of monomial and remember minus
        while i < len(st) and (st[i] == ' ' or st[i] == '+' or st[i] == '-'):
            if st[i] == '-':
                is_positive = False
            i += 1
        if i < len(st):
            res = parse_mon(st, i, is_positive=is_positive)
            mon_list.append(res[0])
            i = res[1]
            is_positive = True
    return Polynomial(mon_list), i

def read_input(infname='input.txt', debug=False)->tuple[str,list,dict,dict]:
    global_var_dict = dict()
    with open(f'scrolls/{infname}','r') as f:
        lines = f.readlines()
    mode = lines[0].split(':')[1].strip()
    ind_vars = lines[1].split(':')[1].split(';')
    ind_vars[len(ind_vars) - 1]=ind_vars[len(ind_vars) - 1].strip()
    if mode == 'DE':
        ivs = dict()
        iv_line = lines[2].split(':')[1]
        iv_line = iv_line.split(';')
        for iv in iv_line:
            iv = iv.strip()
            iv = iv.split('=')
            ivs[iv[0]] = float(iv[1])
            # print(iv)
    for i in range(len(ind_vars)):
        ind_vars[i] = ind_vars[i].strip(' ')
        # print(v)
        global_var_dict[ind_vars[i]] = Var(var_name=ind_vars[i], iv=ivs[ind_vars[i]])
    exprs = dict()
    if debug:
        print(f'Mode is {mode}')
        print(f'Independent variables are {ind_vars}')
        print(f'Initial values: {ivs}')        
    if mode == 'F':
        for i in range(2, len(lines)):
            line = lines[i].split('=')
            f_id = line[0].strip()
            # f_args = []
            # for v in ind_vars:
            #    f_args.append(global_var_dict[v])
            # global_var_dict[f_id] = Var(f_id, var_args = f_args)
            f_rhs = line[1][1:len(line[1])-1]
            exprs[f_id] = f_rhs
        if debug:
            print('System of functions')
            for f in exprs:
                print(f'{f} = {exprs[f]}')
    else:
        for i in range(3, len(lines)):
            line = lines[i].split('=')
            lhs = line[0].strip().split('/')
            x_i = lhs[0][1:]
            if x_i not in global_var_dict:
                global_var_dict[x_i] = Var(var_name=x_i, var_deps=dict(), iv=ivs[x_i])
            t_j = lhs[1][1:]
            rhs = line[1][1:len(line[1])-1]
            if x_i not in exprs:
                exprs[x_i] = dict()
            exprs[x_i][t_j] = rhs
        if debug:
            print('System of equations')
            for x in exprs:
                for t in exprs[x]:
                    print(f'd{x}/d{t} = {exprs[x][t]}')

    return mode, ind_vars, exprs, global_var_dict

def read_input_polytest(infname='test_poly_subs.txt', debug=False):
    with open(f'scrolls/{infname}','r') as f:
        lines = f.readlines()
    og = parse_poly(lines[0].split(':')[1].strip())[0]
    var = lines[1].split(':')[1].split('=')[0].strip()
    poly = parse_poly(lines[1].split(':')[1].split('=')[1].strip())[0]
    if debug:
        print(og.printout())
        print(var)
        print(poly.printout())
    new = og.subs_poly(var, poly)
    if debug:
        print(new.printout())
    return new

# DE system is 2 level dictionary
def printout_poly_de(sys: dict):
    for f in sys:
        for x in sys[f]:
            print(f'd{f}/d{x} = {sys[f][x].printout()}')

# func system is 1 level dictionary
def printout_poly_func(sys: dict):
    for f in sys:
        print(f'{f} = {sys[f].printout()}')


if __name__ == "__main__":
    # m,iv,e,gvd = read_input(infname = 'input_de_small.txt',debug=True)
    # print(gvd)
    read_input_polytest(debug=True)