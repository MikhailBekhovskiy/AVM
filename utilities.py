def read_var(exp, ind):
    cof = 0
    if exp[ind] == '-':
        ind += 1
        cof = - int(exp[ind])
        ind += 1
    while exp[ind] != '*':
        cof = cof * 10 + int(exp[ind])
        ind += 1
    ind += 1
    name = ''
    while exp[ind] != '^':
        name += exp[ind]
        ind += 1
    ind += 2
    power = 0
    while exp[ind] != '}':
        power = power * 10 + int(exp[ind])
        ind += 1
    return (cof, name, power), ind + 1


def read_monom(exp, ind):
    vars = []
    while exp[ind] != ' ':
        vars.append(read_var(exp, ind)[0])
        ind = read_var(exp, ind)[1]
    return vars, ind + 3



e = '50*x^{228}'
i = 0
print(read_var(e, i))