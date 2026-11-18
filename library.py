# module containing example of pre-loaded library and functions for selecting only needed sections
type libsyst = list[list[str]]
type libnams = dict[str, tuple[int, str, list[str], int, int]]
type lib = tuple[libnams, libsyst]

# function to select needed systems from read section;
def expand_sub_lib(funcs: dict, lib: tuple[libnams, libsyst], sub_names:libnams=dict(), sub_syst:libsyst=[]) -> lib:
    names = lib[0]
    systems = lib[1]
    for f in funcs:
        if f not in sub_names:
            ext = names[f][2]
            num = names[f][0]
            new_num = len(sub_syst)
            sub_names[f] = (new_num, names[f][1], names[f][2], names[f][3], names[f][4])
            for e in ext:
                sub_names[e] = (new_num, names[e][1], names[e][2], names[e][3], names[e][4])
            sub_syst.append(systems[num])
    return (sub_names, sub_syst)

def get_ext_names(sysind: int, naming: libnams) -> dict[str, tuple[str, int, int]]:
    res = dict()
    for f in naming:
        if naming[f][0] == sysind:
            res[f] = (naming[f][1], naming[f][3], naming[f][4])
    return res

# example of read (pre-loaded; pre-selected) non_autonomous library section;
# non-autonomous system examples are sections 4-6
library_names_na:libnams = {
    'sin': (0, 'f1', ['cos'], 0, 1),
    'cos': (0, 'f2', ['sin'], 0, 1),
    'ln': (1, 'f1', ['inv'], 0, 1),
    'inv': (1, 'f2', [], 0, 1),
    'sh': (2, 'f1', ['ch'], 0, 1),
    'ch': (2, 'f2', ['sh'], 0, 1),
    'EK': (3, 'f1', ['EKs', 'EKc', 'EKi'], 0,2),
    'EKs': (3, 'f2', ['EKc', 'EKi'], 0, 2),
    'EKc': (3, 'f3', ['EKs', 'EKi'], 0, 2),
    'EKi': (3, 'f4', ['EKs', 'EKc'], 0, 2),
    'DV': (4, 'f2', ['Dv'], 3, 1),
    'Dv': (4, 'f1', ['DV'], 3, 1),
    'Hb': (5, 'f1', ['Hbi'], 0, 3),
    'Hbi': (5, 'f2', ['Hb'], 0, 3),
    'sqrt': (6, 'f1', ['isqrt'], 0, 1),
    'isqrt': (6, 'f2', [], 0, 1)
}

library_RHS_na:libsyst = [
    [
        'df1/dt = f2',
        'df2/dt = -f1'
    ],
    [
        'df1/dt = f2',
        'df2/dt = -f2^2'
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

lib_na: lib = (library_names_na, library_RHS_na)
# for testing purposes
if __name__ == "__main__":
    pass