# module realizing computer symbolic algebra and differentiation for multivariate polynomials
import math
elementaries={'sin', 'cos', 'ch', 'sh', 'inv', 'ln', 'exp'}

# this class represents all variables, including dependent (additional)
# objects of this class contain known Polynomial derivatives, employing philosophy of AVM algorithms
# by having temporary libraries of their own
class Var():
    def __init__(self, var_name: str, var_deps=None, var_args=[], iv=None, f_def=None, params = None):
        # variable name is an identifier in global variable dictionary and symbolic handle in expressions
        self.name = var_name
        # dictionary with known derivatives; keys are either existing var_names or numeric for positional arguments (partial derivatives)
        self.deps = var_deps
        # list of Polynomial arguments; RECURSION; at lowest level Vars don't have polynomial arguments (original LHS functions and independent variables)
        self.args = var_args
        # initial value of a variable; numeric if given or variable represents elementary function; symbolic if variable represents special function
        self.iv = iv
        # which function is represented by variable; for initial values recalculation
        self.f_def = f_def
        # parameters for initial values recalculations
        self.params = params
        # if variable is dependent, derivative dictionary is initialized
        if var_args !=[] and var_deps is None:
            self.deps = dict()
        
        
    # 1. if var_names are same, return Polynomial 1
    # 2. if Var is independent (uninitialized deps dict), return Polynomial 0
    # 3. if Var is dependent and derivative has been calculated, return result from deps dict
    # 4. if Var is dependent with unknown variable, use chain rule; all lower level Polynomial derivatives must be known
    # this function is RECURSIVE, since it calls Polynomial arguments; lowest level Polynomials consist of Vars with no arguments;
    def derivative(self, var_name: str, global_var_dict: dict, debug=False):
        if self.name == var_name:
            if debug:
                print('Same names')
            return Polynomial([Monomial(mon_coeff=1.)])
        elif self.deps is None:
            if debug:
                print('Independent variable')
            return Polynomial()
        else:
            if var_name in self.deps:
                if debug:
                    print('Derivative previously calculated')
                return self.deps[var_name]
            else:
                if debug:
                    print('Chain rule')
                result = Polynomial()
                # chain rule for additional (dependent) variables
                for i in range(len(self.args)):
                    part_der = self.deps[i]
                    arg_der = self.args[i].derivative(var_name, global_var_dict)
                    plus = part_der.prod(arg_der)
                    if debug:
                        print(f'Pos Der is {part_der.printout()}')
                        print(f'Arg der is {arg_der.printout()}')
                        print(f'Addition is {plus.printout()}')
                    result = result.add(plus)
                    if debug:
                        print(f'Result is {result.printout()}')
                return result
        
    # utility function
    def printout(self):
        print(f'Variable {self.name}; dependent: {self.deps is not None}')
        if self.args != []:
            print(f'Arguments ({len(self.args)})')
            for arg in self.args:
                print(arg.printout())
            for dep in self.deps:
                if type(dep) is not str:
                    print(f'Derivative by positional argument {dep} is {self.deps[dep].printout()}')
                else:
                    print(f'Derivative by {dep} is {self.deps[dep].printout()}')
        print()
    
    # initial values recalculation
    def evaluate(self, gvd:dict, symb=True, library=None):
        if self.iv is not None:
            return self.iv
        elif self.args != []:
            arg = self.args[0].evaluate(gvd, symb, library)
            if self.f_def in elementaries and type(arg) is float:
                f = self.f_def
                if f == 'sin':
                    self.iv = math.sin(arg)
                    return self.iv
                if f == 'cos':
                    self.iv = math.cos(arg)
                    return self.iv
                if f == 'sh':
                    self.iv = math.sinh(arg)
                    return self.iv
                if f == 'ch':
                    self.iv = math.cosh(arg)
                    return self.iv
                if f == 'inv':
                    self.iv = 1 / arg
                    return self.iv
                if f == 'ln':
                    self.iv = math.log(arg)
                    return self.iv
                if f == 'exp':
                    self.iv = math.exp(arg)
                    return self.iv
            else:
                if self.params != '':
                    paramstr = self.params + ';'
                else:
                    paramstr = ''
                res = self.f_def + '[' + paramstr + str(arg) + ','
                for i in range(1, len(self.args)):
                    res += str(self.args[i].evaluate(gvd=gvd, symb=symb, library=library)) + ','
                res = res[:len(res) - 1] + ']'
                if symb:
                    self.iv = res
                    return res
                else:
                    pass
        else:
            print(f'Impossible to evaluate var {self.name}')
    
# Monomial is a set of powered variables with numeric coefficient
class Monomial():
    def __init__(self, mon_coeff=0., var_pow_list=None):
        # numerical coefficient
        self.coef = mon_coeff
        # dictionary of (var_name: integer power) pairs
        self.vars = dict()
        # string representation of monomial for quick algebra
        self.signature = ''
        if self.coef != 0. and var_pow_list is not None:
            var_pow_list.sort(key=lambda x:x[0])
            for var in var_pow_list:
                self.signature += str(var[0]) + str(var[1])
                self.vars[var[0]] = var[1]

    # update signature after substitution
    def recalc_signature(self):
        self.signature = ''
        var_pow_list = list(self.vars.items())
        if self.coef != 0. and var_pow_list != []:
            var_pow_list.sort(key=lambda x:x[0])
            for var in var_pow_list:
                self.signature += str(var[0]) + str(var[1])

    # create a deep copy of object for algebra
    def copy(self):
        coef = self.coef
        vars = None
        if len(self.vars) > 0:
            vars = []
            for var in self.vars:
                vars.append((var, self.vars[var]))
        return Monomial(coef, vars)

    # utility function for substitution
    def remove_var(self, var_name, debug=False):
        res = self.copy()
        if var_name in res.vars:
            del res.vars[var_name]
            res.recalc_signature()
        else:
            if debug:
                print('No such variable in monomial')
        return res

    # normalize Poly during algebra or differentiation
    def add_similar(self, mon):
        new_coef = self.coef + mon.coef
        if len(self.vars) == 0 :
            varlist = None
        else:
            varlist = list(self.vars.items())
        return Monomial(mon_coeff=new_coef, var_pow_list=varlist)
    
    # algebra
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
    
    # substitute Polynomial instead of var_name; RECURSIVE
    def subs_poly(self, var_name: str, poly, debug = False):
        res = Polynomial()
        if var_name in self.vars:
            res = Polynomial(mon_list=[self.remove_var(var_name, debug=debug)])
            res = res.prod(poly.power(int(self.vars[var_name])))
        return res

    # COMPLETE derivative calculated using chain rule
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

    # utility for initial values recalculation        
    def evaluate(self, gvd:dict, symb=True, library=None):
        if self.coef == 0:
            return 0.
        num_part = self.coef
        symb_part = ''
        for var in self.vars:
            if var in gvd:
                var_val = gvd[var].evaluate(gvd=gvd, symb=symb, library=library)
                if type(var_val) is float:
                    num_part *= var_val ** self.vars[var]
                else:
                    symb_part += var_val
                    if self.vars[var] > 1:
                        symb_part += '^' + str(self.vars[var])
                    symb_part += '*'
            else:
                symb_part += var
                if self.vars[var] > 1:
                    symb_part += '^' + str(self.vars[var])
                symb_part += '*'
        if symb_part == '' or num_part == 0.:
            return num_part
        else:
            if symb:
                symb_part = symb_part[:len(symb_part) - 1]
                if num_part != 1.:
                    num_part = str(num_part)
                    return num_part + '*' + symb_part
                else:
                    return symb_part
            else:
                pass

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

# Polynomial is a dictionary of (monomial_sign: Monomial) with methods
class Polynomial():
    def __init__(self, mon_list=None):
        # specific dictionary structure simplifies algebra
        self.mons = dict()
        if mon_list is not None:
            for mon in mon_list:
                self.mons[mon.signature] = mon.copy()
    
    # deep copy for algebra
    def copy(self):
        mon_list = None
        if self.mons is not None:
            mon_list = []
            for mon in self.mons:
                mon_list.append(self.mons[mon].copy())
        return Polynomial(mon_list)
    
    # algebra
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

    # substitute Polynomial instead of variable; for non-autonomous systems support
    def subs_poly(self, var_name, poly, debug=False):
        res = self.copy()
        for m in self.mons:
            if var_name in m:
                p = self.mons[m].subs_poly(var_name, poly, debug=debug)
                del res.mons[m]
                res = res.add(p)
        return res

    # derivative of a polynomial is simply the sum of it's monomial's derivatives
    # RECURSIVE 
    def derivative(self, var_name: str, global_var_dict: dict):
        result = Polynomial()
        for mon in self.mons:
            result = result.add(self.mons[mon].derivative(var_name, global_var_dict))
        return result

    # initial values calculation (additional variables have polynomial arguments)
    def evaluate(self, gvd: dict, symb=True, library=None):
        num_part = 0.
        symb_part = ''
        for mon in self.mons:
            mon_val = self.mons[mon].evaluate(gvd=gvd, symb=symb, library=library)
            if type(mon_val) is float:
                num_part += mon_val
            elif mon_val[0] == '-':
                symb_part += mon_val
            else:
                symb_part += '+' + mon_val
        if symb_part == '':
            return num_part
        elif symb_part[0] == '+':
            symb_part = symb_part[1:]
        if num_part == 0.:
            return symb_part
        return symb_part + '+' + str(num_part)

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
    