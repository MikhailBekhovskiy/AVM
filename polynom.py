class Monom():
    def __init__(self, vardegs: dict(), coeff=1.):
        self.vars = vardegs
        self.coef = coeff

    def __str__(self):
        res = ''
        if self.coef == -1.:
            res += '-'
        elif self.coef != 1.:
            res += str(self.coef)
            res += '*'
        for var in self.vars:
            res += var
            if self.vars[var] != 1:
                res += f'^{self.vars[var]}'
            res += '*'
        res = res[:len(res)-1]
        return res
    

def isSimilar(m1: Monom, m2: Monom):
    for var in m1.vars:
        if var not in m2.vars or m2.vars[var] != m1.vars[var]:
            return False
    return True

def multiplyM(m1:Monom, m2:Monom):
    m3 = Monom(coeff = m1.coef * m2.coef, vardegs=dict())
    for var in m1.vars:
        m3.vars[var] = m1.vars[var]
    for var in m2.vars:
        if var in m3.vars:
            m3.vars[var] += m2.vars[var]
        else:
            m3.vars[var] = m2.vars[var]
    return m3

def parseM(inp: str()) -> Monom:
    i = 0
    coef = ''
    if inp[i] == '-':
        coef += '-'
        i += 1
    if inp[i] < 'A':
        while i < len(inp) and inp[i] != '*':
            coef += inp[i]
            i += 1
        i += 1
        m = Monom(coeff=float(coef), vardegs=dict())
        if i >= len(inp):
            return m
    else:
        m = Monom(coeff=1., vardegs=dict())
        if coef == '-':
            m.coef = -1.
    while i < len(inp):
        varname = ''
        deg = ''
        while i < len(inp) and inp[i] != '^' and inp[i] != '*':
            varname += inp[i]
            i += 1
        if i >= len(inp):
            if varname in m.vars:
                m.vars[varname] += 1
            else:
                m.vars[varname] = 1
            return m
        if inp[i] == '*':
            if varname in m.vars:
                m.vars[varname] += 1
            else:
                m.vars[varname] = 1
            i += 1
        if inp[i] == '^':
            i += 1
            while i < len(inp) and inp[i] != '*':
                deg += inp[i]
                i += 1
            i += 1
            if varname in m.vars:
                m.vars[varname] += int(deg)
            else:
                m.vars[varname] = int(deg)
    return m

class Polynom():
    def __init__(self, monoms: list()):
        self.mons = monoms


    def __str__(self):
        res = ''
        for m in self.mons:
            if m.coef > 0.:
                res += '+'
            res += str(m)
        if res[0] == '+':
            res = res[1:]
        return res


    def simplify(self):
        p1 = Polynom(monoms=[])
        for m in self.mons:
            added = False
            for j in range(len(p1.mons)):
                if isSimilar(m, p1.mons[j]):
                    p1.mons[j].coef += m.coef
                    added = True
            if not added:
                p1.mons.append(m)
        return p1


def multiplyP(p1: Polynom, p2: Polynom):
    p3 = Polynom(monoms=[])
    for m1 in p1:
        for m2 in p2:
            p3.mons.append(multiplyM(m1,m2))
    return p3.simplify()
    

def parseP(inp: str())->Polynom:
    i = 0
    p = Polynom(monoms=[])
    while i < len(inp):
        buf = ''
        if inp[i] == '-':
            buf += '-'
            i += 1
        if inp[i] == '+':
            i += 1
        while i < len(inp) and inp[i] != '+' and inp[i] != '-':
            if inp[i] != ' ':
                buf += inp[i]
            i += 1
        p.mons.append(parseM(buf))
    return p


ex = 'x*y^10*z^6 + x^5*z'

p = parseP(ex)
print(p)
