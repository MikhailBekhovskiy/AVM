###################
# loaded sublibrary
###################
funcs = {
    'sin': (1,1),
    'cos': (1,2),
    'ln': (2,1),
    'inv': (2,2)
}
rhs = {
    1: {
        1: {
            1: 'q2'
        },
        2: {
            1: '-q1'
        }
    },
    2: {
        1: {
            1:'q2'
        },
        2: {
            1:'-q2^2'
        }        
    }
}
####################
# input system
####################
system = {
    'y1': 'x1^5*sin[x2]',
    'y2': '(ln[x1])^3*cos[x2]'
}

####################
# additional variables arguments should be as follows
# (rhs from library are read at the moment of AV creation)
####################
'''
adds _args= {
    'x3': [Poly('x2')],             # sin
    'x4': [Poly('x2')],             # cos
    'x5': [Poly('x1')],             # ln
    'x6': [Poly('x1')]              # inv
}
'''
#############################
# variable dependencies should be as follows
#############################
# for independent
#############################
'''
x1.deps = {
    'x1': Poly(1)
}
x2.deps = {
    'x2': Poly(1)
}
'''
#############################
# for dependent (pre-differentiation)
#############################
'''
x3.deps = {
    'arg1': Poly('x4'),
    'x3' : Poly(1)
}
x4.deps = {
    'arg1': Poly('-x3'),
    'x4': Poly(1)
}
x5.deps = {
    'arg1': Poly('x6'),
    'x5': Poly(1)
}
x6.deps = {
    'arg1': Poly('-x6^2'),
    'x6': Poly(1)
}
'''