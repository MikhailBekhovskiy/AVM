# this is a reworked polynomial module
# storing variables by names and separating them from power in polynomials, thus
# reducing redundancy;
# power derivative calculation is at monomial level, chaining with variable derivatives stored in memory;
# variable derivatives are either taken from input system
# or calculated at introducing additional variables step using stored library info;
# independent variable derivative is 1 or 0
# dependent variable derivative is stored as dependency and is simply read
class Var():
    # variable is denoted by:
    # name (for output purposes); name MUST be always given
    # dependencies dict (derivative substitutions for chain-rule calculations); might be empty if variable is independent;
    def __init__(self, var_name: str, var_deps=None, var_args=[]):
        self.name = var_name
        # dictionary which contains only polynomial derivatives by independent variables 
        # and positional arguments (in case of additional variable)
        # polynomial derivatives contain variables ALREADY present in global_var_dictionary
        # this will be handled at preprocessing step and during introduction of AVs
        self.var_deps = var_deps
        self.var_args = var_args
        if var_args !=[] and var_deps is None:
            self.var_deps = dict()
        
        
    # TODO testing
    def derivative(self, var_name: str, global_var_dict: dict, debug=False):
        if self.name == var_name:
            if debug:
                print('Same names')
            return Polynomial([Monomial(mon_coeff=1.)])
        elif self.var_deps is None:
            if debug:
                print('Independent variable')
            return Polynomial()
        else:
            if var_name in self.var_deps:
                if debug:
                    print('Derivative previously calculated')
                return self.var_deps[var_name]
            else:
                if debug:
                    print('Chain rule')
                result = Polynomial()
                # chain rule for additional (dependent) variables
                for i in range(len(self.var_args)):
                    part_der = self.var_deps[i]
                    arg_der = self.var_args[i].derivative(var_name, global_var_dict)
                    plus = part_der.prod(arg_der)
                    if debug:
                        print(f'Pos Der is {part_der.printout()}')
                        print(f'Arg der is {arg_der.printout()}')
                        print(f'Addition is {plus.printout()}')
                    result = result.add(plus)
                    if debug:
                        print(f'Result is {result.printout()}')
                return result
        

    def printout(self):
        print(f'Variable {self.name}; dependent: {self.var_deps is not None}')
        if self.var_args != []:
            print(f'Arguments ({len(self.var_args)})')
            for arg in self.var_args:
                print(arg.printout())
            for dep in self.var_deps:
                if type(dep) is not str:
                    print(f'Derivative by positional argument {dep} is {self.var_deps[dep].printout()}')
                else:
                    print(f'Derivative by {dep} is {self.var_deps[dep].printout()}')
        print()
class Monomial():
    # monomial is denoted by:
    # coefficient (single real number)
    # vars dict (dictionary keyed by var_names with powers as values) for hierarchical calculations using Var subclass
    # signature (string containing sorted var names and their powers; for fast similarity check during arithmetics)
    def __init__(self, mon_coeff=0., var_pow_list=None):
        self.coef = mon_coeff
        self.vars = dict()
        self.signature = ''
        if self.coef != 0. and var_pow_list is not None:
            var_pow_list.sort(key=lambda x:x[0])
            for var in var_pow_list:
                self.signature += str(var[0]) + str(var[1])
                self.vars[var[0]] = var[1]

    def recalc_signature(self):
        self.signature = ''
        var_pow_list = list(self.vars.items())
        if self.coef != 0. and var_pow_list != []:
            var_pow_list.sort(key=lambda x:x[0])
            for var in var_pow_list:
                self.signature += str(var[0]) + str(var[1])

    def copy(self):
        coef = self.coef
        vars = None
        if len(self.vars) > 0:
            vars = []
            for var in self.vars:
                vars.append((var, self.vars[var]))
        return Monomial(coef, vars)

    def remove_var(self, var_name, debug=False):
        res = self.copy()
        if var_name in res.vars:
            del res.vars[var_name]
            res.recalc_signature()
        else:
            if debug:
                print('No such variable in monomial')
        return res

    # called when normalizing poly after arithmetic or differentiation
    def add_similar(self, mon):
        new_coef = self.coef + mon.coef
        if len(self.vars) == 0 :
            varlist = None
        else:
            varlist = list(self.vars.items())
        return Monomial(mon_coeff=new_coef, var_pow_list=varlist)
    
    def scalar_prod(self, a: float):
        coef = a * self.coef
        if len(self.vars) >0:
            var_pow_list = list(self.vars.items())
        else:
            var_pow_list = None
        return Monomial(coef, var_pow_list)
    
    def prod(self, mon):
        if len(self.vars) == 0:
            return mon.scalar_prod(self.coef)
        elif len(mon.vars) == 0:
            return self.scalar_prod(mon.coef)
        else:
            new_coef = self.coef * mon.coef
            var_pow_list = None
            if new_coef != 0.:
                var_pow_list = []
                for var in self.vars:
                    var_pow = self.vars[var]
                    if var in mon.vars:
                        var_pow += mon.vars[var]
                    var_pow_list.append((var, var_pow))
                for var in mon.vars:
                    if var_pow_list is None:
                        var_pow_list = []
                    if var not in self.vars:
                        var_pow_list.append((var, mon.vars[var]))
            return Monomial(new_coef, var_pow_list)
    
    def subs_poly(self, var_name: str, poly, debug = False):
        res = Polynomial()
        if var_name in self.vars:
            res = Polynomial(mon_list=[self.remove_var(var_name, debug=debug)])
            res = res.prod(poly.power(int(self.vars[var_name])))
        return res

    # returns Poly
    # complete derivative calculated using chain rule
    def derivative(self, var_name: str, global_var_dict: dict):
        result = Polynomial()
        if len(self.vars) == 0:
            return result
        else:
            for var in self.vars:
                if var in global_var_dict:
                    var_der = global_var_dict[var].derivative(var_name, global_var_dict)
                    if len(var_der.mons) > 0:
                        rem_var_pow_list = []
                        rem_coef = 1.
                        if self.vars[var] > 1:
                            rem_var_pow_list.append((var, self.vars[var] - 1))
                            rem_coef = self.vars[var]
                        for var1 in self.vars:
                            if var1 != var:
                                rem_var_pow_list.append((var1, self.vars[var1]))
                        rem = Polynomial([Monomial(mon_coeff=rem_coef, var_pow_list=rem_var_pow_list)])
                        result = result.add(var_der.prod(rem))
                else:
                    continue
            return result.scalar_prod(self.coef)
            
    
    # for output
    def printout(self):
        result = ''
        if self.coef == 0.:
            return result
        if len(self.vars) == 0:
            result += f'{self.coef}'
            return result
        else:
            if self.coef != 1. and self.coef != -1.:
                result += f'{self.coef}*'
            elif self.coef == -1.:
                result += '-'
            for var in self.vars:
                power = self.vars[var]
                if power != 1.:
                    result += f'{var}^{power}*'
                else:
                    result += f'{var}*'
            return result[:len(result) - 1]

class Polynomial():
    # Polynomial is simply a list of monomials (so its always normalized)
    # denoted by dict keyed by monomials signatures (for arithmetic purposes) with Monomial values
    # normalization occurs during substitution immediately
    def __init__(self, mon_list=None):
        self.mons = dict()
        if mon_list is not None:
            for mon in mon_list:
                self.mons[mon.signature] = mon.copy()
    
    def copy(self):
        mon_list = None
        if self.mons is not None:
            mon_list = []
            for mon in self.mons:
                mon_list.append(self.mons[mon].copy())
        return Polynomial(mon_list)
    
    # multivariate polynomial arithmetics
    # returns normalized polynomial
    def add(self, poly):
        if len(poly.mons) == 0:
            return self.copy()
        elif len(self.mons) == 0:
            return poly.copy()
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
        if len(self.mons) == 0:
            return Polynomial()
        else:
            for mon in self.mons:
                mon_list.append(self.mons[mon].scalar_prod(a))
            return Polynomial(mon_list)

    def prod(self, poly, debug=False):
        result = Polynomial()
        for mon1 in self.mons:
            if debug:
                print(self.mons[mon1].printout())
            for mon2 in poly.mons:
                if debug:
                    print(poly.mons[mon2].printout())
                new_mon = self.mons[mon1].prod(poly.mons[mon2])
                #if debug:
                   # print(new_mon.printout())
                result = result.add(Polynomial([new_mon]))
                if debug:
                    print(result)
        return result

    def power(self, power: int):
        res = self.copy()
        for i in range(1, power):
            res = res.prod(self)
        return res

    def subs_poly(self, var_name, poly, debug=False):
        res = self.copy()
        for m in self.mons:
            if var_name in m:
                p = self.mons[m].subs_poly(var_name, poly, debug=debug)
                del res.mons[m]
                res = res.add(p)
        return res

    # derivative of a polynomial is simply the sum of it's monomial's derivatives
    def derivative(self, var_name: str, global_var_dict: dict):
        result = Polynomial()
        for mon in self.mons:
            result = result.add(self.mons[mon].derivative(var_name, global_var_dict))
        return result

    # output
    def printout(self):
        result = ''
        if len(self.mons) == 0:
            return '0'
        else:
            for mon in self.mons:
                mono = self.mons[mon]
                if mono.coef > 0:
                    result += '+'
                result += mono.printout()
            if len(result) > 0 and result[0] == '+':
                return result[1:]
            if result == '':
                return '0'
            return result
    