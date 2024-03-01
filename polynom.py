# this is a reworked polynomial module
# storing variables by names and separating them from power in polynomials, thus
# reducing redundancy;
# power derivative calculation is at monomial level, chaining with variable derivatives stored in memory;
# variable derivatives are either taken from input system
# or calculated at introducing additional variables step using stored library info;
# independent variable derivative is 1 or 0
# dependent variable derivative is stored as dependency and is simply read
from parse import *
class Var():
    # variable is denoted by:
    # name (for output purposes); name MUST be always given
    # dependencies dict (derivative substitutions for chain-rule calculations); might be empty if variable is independent;
    # global_var_dict MUST be supplied; after creation variable is stored there keyed by name;
    # global_var_dict is used for output and MOST IMPORTANTLY for derivative calculations on polynomial and monomial levels
    # this allows to avoid storing multiple instances of the same variable
    def __init__(self, global_var_dict: dict, var_name: str, var_deps=dict(), var_args=[]):
        self.name = var_name
        # dictionary which contains polynomial derivatives by independent variables 
        # in case of additional variables it contains polynomial derivatives ONLY
        # (which get calculated with respect to the system at substitution step)
        # in case of input system variables it contains RHS strings which get replaced 
        # by Polynomials as algorithm transforms them
        if var_args != []:
            self.isDep = True 
            self.args = var_args
        else:
            self.isDep = False
        self.deps = var_deps
        global_var_dict[var_name] = self
        
    # TODO function for library variables to expand their dependencies dict after substitution
    # calculate the complete derivative by independent variable with respect to system
    # var_name MUST be name of system variable (either original or introduced at previous steps)
    # global_var_dict and sublibrary dict MUST be supplied
    def derivative(self, var_name: str, global_var_dict: dict):
        if self.isDep:
            if var_name not in self.deps:
                result = Polynomial()
                for i in range(len(self.args)):
                    result.add(self.deps[i].prod(self.args[i].derivative(var_name, global_var_dict)))
                self.deps[var_name] = result
                return result
            else:
                return self.deps[var_name]
        elif self.name == var_name:
            return 1
        return 0


class Monomial():
    # monomial is denoted by:
    # coefficient (single real number)
    # vars dict (dictionary keyed by var_names with powers as values) for hierarchical calculations using Var subclass
    # signature (string containing sorted var names and their powers; for fast similarity check during arithmetics)
    def __init__(self, mon_coeff=0., var_pow_list=[]):
        self.coef = mon_coeff
        self.vars = dict()
        self.signature = ''
        if self.coeff != 0:
            var_pow_list.sort(key=lambda x:x[0])
            for var in var_pow_list:
                self.signature += str(var[0]) + str(var[1])
                self.vars[var[0]] = var[1]


    # called when normalizing poly after arithmetic or differentiation
    def add_similar(self, mon):
        if self.signature == mon.signature:
            new_coef = self.coef + mon.coef
            return Monomial(mon_coeff=new_coef, var_pow_list=self.vars.copy())
        else:
            return 'Bug. This addition shouldn\'t have happened'
        
    def scalar_prod(self, a: float):
        coef = a * self.coef
        var_pow_list = list(self.vars.items())
        return Monomial(coef, var_pow_list)
    
    def prod(self, mon):
        new_coef = self.coef * mon.coef
        var_pow_list = []
        if new_coef != 0:
            for var in self.vars:
                var_pow = self.vars[var]
                if var in mon.vars:
                    var_pow += mon.vars[var]
                var_pow_list.append((var, var_pow))
            for var in mon.vars:
                if var not in self.vars:
                    var_pow_list.append((var, mon.vars[var]))
        return Monomial(new_coef, var_pow_list)
    

    # should return Poly or 0
    # it is a COMPLETE derivative with respect to input system 
    # and their derivatives. compatibility stems from Var class support
    # for introducing temporary variables instead of yet untransformed RHSs
    def derivative(self, var_name: str, global_var_dict: dict):
        result = Polynomial()
        for var in self.vars:
            var_der = global_var_dict[var].derivative(var_name)
            # var_der is either Poly or 0; 0 is ignored, Poly case added to result
            if var_der != 0:
                # create Poly from remaining Mono part
                rem_var_pow_list = []
                rem_coef = 1
                if self.vars[var] > 1:
                    rem_var_pow_list.append((var, self.vars[var] - 1))
                    rem_coef = self.vars[var]
                for var1 in self.vars:
                    if var1 != var:
                        rem_var_pow_list.append((var1, self.vars[var1]))
                
                rem = Polynomial([Monomial(mon_coeff=rem_coef, var_pow_list=rem_var_pow_list)])
                # add to the result production of variable derivative and remainder of monomial
                result = result.add(var_der.prod(rem))
        if len(result.mons) > 0:
            return result.scalar_prod(self.coef)
        return result
    
    # for output
    def printout(self):
        result = f'{self.coef} * '
        for var in self.vars:
            power = self.vars[var]
            result += f'{var}^{power} * '
        return result[:len(result) - 2]


def parse_mon(st: str, start: int, is_positive: bool, global_var_dict: dict) -> tuple[Monomial, int]:
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
        if name not in global_var_dict:
            global_var_dict[name] = Var(global_var_dict, name)
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
    return Monomial(coef, var_pow_list), i


class Polynomial():
    # Polynomial is simply a list of monomials (so its always normalized)
    # denoted by dict keyed by monomials signatures (for arithmetic purposes) with Monomial values
    # normalization occurs during substitution immediately
    def __init__(self, mon_list=[]):
        self.mons = dict()
        for mon in mon_list:
            if type(mon) is Monomial:
                self.mons[mon.signature] = mon
            else:
                print('Bug, monomial was not read')

    # multivariate polynomial arithmetics
    # returns normalized polynomial
    def add(self, poly):
        if poly.mons == []:
            return self
        else:
            mon_list = []
            for mon in self.mons:
                if mon in poly.mons:
                    mon_list.append(self.mons[mon].add_similar(poly.mons[mon]))
                else:
                    mon_list.append(self.mons[mon])
            for mon in poly.mons:
                if mon not in self.mons:
                    mon_list.append(poly.mons[mon])
            return Polynomial(mon_list)
    
    def scalar_prod(self, a: float):
        mon_list = []
        for mon in self.mons:
            mon_list.append(self.mons[mon].scalar_prod(a))
        return Polynomial(mon_list)

    def prod(self, poly):
        result = Polynomial()
        for mon1 in self.mons:
            for mon2 in poly.mons:
                new_mon = self.mons[mon1].prod(poly.mons[mon2])
                new_sign = new_mon.signature
                if new_sign in result.mons:
                    result.mons[new_sign] = result.mons[new_sign].add_similar(new_mon)
                else:
                    result.mons[new_sign] = new_mon
        return result

    # derivative of a polynomial is simply the sum of it's monomial's derivatives
    def derivative(self, var_name: str, global_var_dict: dict):
        result = Polynomial()
        for mon in self.mons:
            result = result.add(self.mons[mon].derivative(var_name, global_var_dict))
        return result

    # output
    def printout(self, global_var_dict: dict):
        result = ''
        for mon in self.mons:
            mono = self.mons[mon]
            if mono.coef > 0:
                result += '+'
            result += mono.printout(global_var_dict)
        if result[0] == '+':
            return result[1:]
        return result
    

def parse_poly(st:str, start:int) -> tuple[Polynomial, int]:
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
    return Polynomial(mon_list), i
