class PolyVar:
    def __init__(self,  cof=0, name='', power=0, ind = True):
        self.name = name
        self.power = power
        self.coeff = cof
        self.indie = ind
        self.zeroes = {}

    def derivative(self, var):
        if self.indie:
            if var == self.name:
                return (PolyVar(self.coeff * self.power, self.name, self.power - 1, True), 1)
            return 0
        if var not in self.zeroes:
            return (PolyVar(self.coeff * self.power, self.name, self.power - 1, False), PolyVar(1,f'd{self.name}/d{var}',1, False))
        
    def __str__(self):
        if self.coeff == 0:
            return str(0)
        if self.power == 0:
            return f'{self.coeff}'
        res = ''
        if self.coeff != 1:
            res += str(self.coeff)
        res += self.name
        if self.power != 1:
            res += str(self.power)
        return res
        

class Monomial:
    def __init__(self, vars = []):
        self.variables = vars
    
    def canonize(self):
        cof = 1
        res = []
        for var in self.variables:
            cof *= var.coeff
            var.coeff = 1
            res.append(var)
        res[0].coeff = cof
        return Monomial(res)

    def derivative(self, var):
        res = []
        vars = self.variables
        for i in range(len(vars)):
            der = vars[i].derivative(var)
            if der != 0:
                mnm = [der[0]]
                if der[1] != 1:
                    mnm.append(der[1])
                mnm += vars[:i] + vars[i+1:]
                res.append(Monomial(mnm))
        if res == []:
            return 0
        return res

    def __str__(self):
        if self.variables == []:
            return str(0)
        # tmp = self.canonize()
        res = ''
        for var in self.variables:
            res += var.__str__() + '*'
        res = res[:len(res) - 1]
        return res


class Polynomial:
    def __init__(self, monoms=[]):
        self.monomials = monoms
    
    def derivative(self, var):
        res = []
        for mon in self.monomials:
            der = mon.derivative(var)
            if der != 0:
                res += der
        if res == []:
            return 0
        return Polynomial(res)
    
    def __str__(self):
        if self.monomials == []:
            return str(0)
        res = ''
        for mon in self.monomials:
            res += mon.__str__() + '+'
        res = res[:len(res) - 1]
        return res

x = PolyVar(3, 'x', 5)
# x = x.derivative('x')
y = PolyVar(2, 'y', 3)
z = PolyVar(1, 'z', 6)
w = z.derivative('x')

mn = Monomial([x, y, z])
pn = Polynomial([mn])
pndx = pn.derivative('x')
pndy = pn.derivative('y')
pndz = pn.derivative('z')

print(pn)
print(pndx)
print(pndy)
print(pndz)
#print(mn)
#print(x)
#print(y)
#print(z)
#print(w)
