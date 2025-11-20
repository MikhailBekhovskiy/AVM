# module containing example of pre-loaded library and functions for selecting only needed sections


# function to select needed systems from read section;
def expand_sub_lib(funcs: set, lib: tuple, sub_names=dict(), sub_syst=[]) -> tuple:
    names = lib[0]
    systems = lib[1]
    for f in funcs:
        if f not in sub_names:
            ext = names[f][2]
            num = names[f][0]
            new_num = len(sub_syst)
            sub_names[f] = [new_num, names[f][1], names[f][2], names[f][3]]
            for e in ext:
                sub_names[e] = [new_num, names[e][1], names[e][2], names[e][3]]
            sub_syst.append(systems[num])
    return sub_names, sub_syst



# example of read (pre-loaded; pre-selected) non_autonomous library section;
# non-autonomous system examples are sections 4-6
library_names_na = {
    'sin': [0, 'f1', ['cos'], 0],
    'cos': [0, 'f2', ['sin'], 0],
    'ln': [1, 'f1', ['inv'], 0],
    'inv': [1, 'f2', [], 0],
    'sh': [2, 'f1', ['ch'], 0],
    'ch': [2, 'f2', ['sh'], 0],
    'EK': [3, 'f1', ['EKs', 'EKc', 'EKi'], 0],
    'EKs': [3, 'f2', ['EKc', 'EKi'], 0],
    'EKc': [3, 'f3', ['EKs', 'EKi'], 0],
    'EKi': [3, 'f4', ['EKs', 'EKc'], 0],
    'DV': [4, 'f2', ['Dv'], 3],
    'Dv': [4, 'f1', ['DV'], 3],
    'Hb': [5, 'f1', ['Hbi'], 0],
    'Hbi': [5, 'f2', ['Hb'], 0],
    'sqrt': [6, 'f1', ['isqrt'], 0],
    'isqrt': [6, 'f2', [], 0]
}

library_RHS_na = [
    [
        'df1/dt = f2',
        'df2/dt = -f1'
    ],
    [
        'df1/dt = f2',
        'df2/dt = f2^2'
    ],
    [
        'df1/dt = f2',
        'df2/dt = f1'
    ],
    [
        'df1/dt1 = f2*f4',
        'df1/dt2 = f4',
        'df2/dt1 = f2*f3*f4', 
        'df2/dt2 = f3*f4',
        'df3/dt1 = -f2^2*f4', 
        'df3/dt2 = -f2*f4',
        'df4/dt1 = f3*f4^2 - t1*f2^2*f4^3', 
        'df4/dt2 = -t1*f4^3*f2'
    ],
    [
        'df1/dt = f2',
        'df2/dt = -(p1*t^2 + p2*t + p3)*f1'
    ],
    [
        'df1/dt1 = -f1*f2',
        'df1/dt2 = -f1^2*f2',
        'df1/dt3 = -f1^3*f2',
        'df2/dt1 = (42*f1^5 + 6*t3*f1 + 2*t2)*f1*f2^3 - f2^2',
        'df2/dt2 = (42*f1^5 + 6*t3*f1 + 2*t2)*f1^2*f2^3 - f1*f2^2',
        'df2/dt3 = (42*f1^5 + 6*t3*f1 + 2*t2)*f1^3*f2^3 - 2*f1^2*f2^2'
    ],
    [
        'df1/dt = 0.5*f2',
        'df2/dt = -0.5*f2^3'
    ]
]

lib_na = (library_names_na, library_RHS_na)
# for testing purposes
if __name__ == "__main__":
    pass