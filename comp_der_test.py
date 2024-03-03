from polynom import *

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

