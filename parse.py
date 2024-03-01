from polynom import *
# TODO 
# read all basic variables from input system;
# import regex and implement func finding
# connections to global_var_dict 


def parse_num(st: str, start: int) -> tuple[float, int]:
    res = ''
    i = start
    while st[i] != '*' and st[i] != ' ' and i < len(st):
        res += st[i]
        i += 1
    return float(res), i

def parse_name(st: str, start: int, global_var_dict: dict) -> tuple[str, int]:
    res = st[start]
    i = start
    while st[i] != '^' and st[i] != '*' and st[i] != ' ' and i < len(st):
        res += st[i]
        i += 1
    if res not in global_var_dict:
        global_var_dict[res] = Var(global_var_dict, res)
    return res, i

def parse_mon(st: str, start: int, is_positive: bool) -> tuple[Monomial, int]:
    i = start
    var_pow_list = []
    # read coefficient; if substring begins NOT with a number, then coefficient was omitted, thus 1
    if st[start] > '9' or st[start] < '0':
        coef = 1.
    else:
        res = parse_num(st, start)
        coef = res[0]
        i = res[1]
    # the sign is read between the monomials
    if not is_positive:
        coef *= -1
    # read variables part; monomial ends with space
    while st[i] != ' ':
        i += 1
        res = parse_name(st, i)
        name = res[0]
        i = res[1]
        # if power is not specified, then it's 1
        if st[i] != '^': 
            power = 1
        else:
            i += 1
            res = parse_num(st, i)
            power = res[0]
            i = res[1]
        var_pow_list.append((name, power))
    return Monomial(mon_coeff=coef, var_pow_list=var_pow_list), i

def parse_poly(st:str, start:int) -> Polynomial:
    mon_list = []
    is_positive = True
    i = start
    # monomial ends at EOS or as function argument
    while i < len(st) and st[i] != ']' and st[i] != ';':
        # move to beginning of monomial and remember minus
        while i < len(st) and (st[i] == '+' or st[i] == ' ' or st[i] == '-'):
            if st[i] == '-':
                is_positive = False
            i += 1
        res = parse_mon(st, i, is_positive=is_positive)
        mon_list.append(res[0])
        i = res[1]
        is_positive = True
    return Polynomial(mon_list)
