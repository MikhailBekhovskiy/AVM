# this is a reworked polynomial module
# storing variables by names and separating them from power in polynomials, thus
# reducing redundancy;
# power derivative calculation is at monomial level, chaining with variable derivatives stored in memory;
# variable derivatives are either taken from input system
# or calculated at introducing additional variables step using stored library info;
# independent variable derivative is 1 or 0
# dependent variable derivative is stored as dependency and is simply read
from parse import parse_name,parse_num
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
        elif self.var_args == []:
            if debug:
                print('Independent variable')
            return Polynomial()
        else:
            if var_name in self.var_deps:
                if debug:
                    print('Der previously calculated')
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
        print(f'Variable {self.name}; dependent: {self.var_args != []}')
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

    def copy(self):
        coef = self.coef
        vars = None
        if len(self.vars) > 0:
            vars = []
            for var in self.vars:
                vars.append((var, self.vars[var]))
        return Monomial(coef, vars)

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
                for var in self.vars:
                    var_pow_list = []
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
    

    # returns Poly
    # complete derivative calculated using chain rule
    def derivative(self, var_name: str, global_var_dict: dict):
        result = Polynomial()
        if len(self.vars) == 0:
            return result
        else:
            for var in self.vars:
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

    def prod(self, poly):
        result = Polynomial()
        for mon1 in self.mons:
            for mon2 in poly.mons:
                new_mon = self.mons[mon1].prod(poly.mons[mon2])
                result = result.add(Polynomial([new_mon]))
        return result

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
        i += 1
    # the sign is read between the monomials
    if not is_positive:
        coef *= -1
    # read variables part; monomial ends with space
    while i < len(st) and st[i] != ' ':
        if st[i] == '*':
            i += 1
        res = parse_name(st, i)
        name = res[0]
        i = res[1]
        # if power is not specified, then it's 1
        if i >= len(st) or st[i] != '^': 
            power = 1.
        else:
            i += 1
            res = parse_num(st, i)
            power = res[0]
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

# for testing purposes
if __name__ == "__main__":
    # testing modes:
    # 0 - production of polynomials passed as strings in scrolls/input.txt
    # 1 - derivative of composite functions using preloaded library and var_dict

    mode = 0
    if mode == 0:
        global_var_dict = dict()
        with open('scrolls/input.txt', 'r') as f:
            strings = f.readlines()

        for i in range(len(strings)):
            strings[i] = strings[i].strip('\n')

        polynoms = [None] * len(strings)
        mass_prod = ''
        for i in range(len(strings)):
            P = parse_poly(strings[i])[0]
            polynoms[i] = P
            mass_prod += f'({P.printout()})'
        mass_res = polynoms[0]
        for i in range(1, len(polynoms)):
            mass_res = mass_res.prod(polynoms[i])

        print(mass_prod,'=',mass_res.printout())

    elif mode == 1:
        global_var_dict = {
        'x1': Var('x1'),
        'x2': Var('x2'),
        'q1': Var('q1',
                {0: Polynomial([Monomial(1.,[('q2', 1)])])},
                [Polynomial([Monomial(1., [('x2',1)])])] ),
        'q2': Var('q2',
                {0: Polynomial([Monomial(-1.,[('q1', 1)])])},
                [Polynomial([Monomial(1., [('x2',1)])])] )
        }

        def polyfy_var(a: Var) -> Polynomial:
            mon = Monomial(1., [(a.name, 1)])
            return Polynomial([mon])

        q1 = global_var_dict['q1']
        dq1_dx1 = q1.derivative('x1', global_var_dict)
        dq1_dx2 = q1.derivative('x2', global_var_dict)
        print(dq1_dx1.printout())
        print(dq1_dx2.printout())