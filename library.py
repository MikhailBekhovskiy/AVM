# module containing loaded library of functions with corresponding polynomial de systems
# currently hardcoded
# TODO implement db loading mechanism

# utility; convenient handling for improved code readability
def get_ext_by_fname(fname: str, lib: dict) -> list:
    return lib[0][fname][2]

def expand_sub_lib(funcs: list, lib: tuple, sub_names=dict(), sub_syst=dict()) -> tuple:
    names = lib[0]
    systems = lib[1]
    for f in funcs:
        if f not in sub_names:
            ext = names[f][2]
            num = names[f][0]
            new_num = len(sub_syst) + 1
            sub_names[f] = (new_num, names[f][1], names[f][2], names[f][3])
            for e in ext:
                sub_names[e] = (new_num, names[f][1], names[f][2], names[f][3])
            sub_syst[new_num] = systems[num]
    return sub_names, sub_syst

library_names = {
    'sin': (1, 'f1', ['cos']),
    'cos': (1, 'f2', ['sin']),
    'ln': (2, 'f1', ['inv']),
    'inv': (2, 'f2', []),
    'sh': (3, 'f1', ['ch']),
    'ch': (3, 'f2', ['sh']),
    'EK': (4, 'f1', ['EKs', 'EKc', 'EKi', 'EKp1', 'EKp2']),
    'EKs': (4, 'f2', ['EKc', 'EKi', 'EKp1', 'EKp2']),
    'EKc': (4, 'f3', ['EKs', 'EKi', 'EKp1', 'EKp2']),
    'EKi': (4, 'f4', ['EKs', 'EKc', 'EKp1', 'EKp2']),
    'EKp1': (4, 'f5', ['EKp2']),
    'EKp2': (4, 'f6', ['EKp1']),
    'DV': (5, 'f2', ['Dv', 'dvp']),
    'Dv': (5, 'f1', ['DV', 'dvp']),
    'dvp': (5, 'f3', []),
    'Hb': (6, 'f1', ['Hbi','hbp2','hbp3']),
    'Hbi': (6, 'f2', ['Hb', 'hbp2', 'hbp3']),
    'hbp2': (6, 'f3', []),
    'hbp3': (6, 'f4', [])
}

# autonomous library; first version for testing
library_RHS = {
    1:{
        'f1': {
            0: 'f2'
        },
        'f2': {
            0: '-f1'
        }
    },
    2: {
        'f1': {
            0: 'f2'
        },
        'f2': {
            0: '-f2^2'
        }
    },
    3: {
        'f1': {
            0: 'f2'
        },
        'f2': {
            0: 'f1'
        }
    },
    4: {
        'f1': {
            0: 'f2*f4',
            1: 'f4'
        },
        'f2': {
            0: 'f2*f3*f4',
            1: 'f3*f4'
        },
        'f3': {
            0: '-f2^2*f4',
            1: '-f2*f4'
        },
        'f4': {
            0: 'f3*f4^2 - f5*f2^2*f4^3',
            1: '-f5*f4^3*f2'
        },
        'f5': {
            0: '1',
            1: '0'
        },
        'f6': {
            0: '0',
            1: '1'
        }
    },
    5: {
        'f1':{
            0: 'f2'
        },
        'f2':{
            0: '-f3^2*f1 - f3*f1 - f1'
        },
        'f3':{
            0: '1'
        }
    },
    6: {
        'f1':{
            0: '-f1*f2',
            1: '-f1^2*f2',
            2: '-f1^3*f2'
        },
        'f2':{
            0:'42*f1^6*f2^3 + 6*f4*f1^2*f2^3 + 2*f3*f1*f2^3 - f2^2',
            1:'42*f1^7*f2^3 + 6*f4*f1^3*f2^3 + 2*f3*f1^2*f2^3 - 2*f1*f2^2',
            2:'42*f1^8*f2^3 + 6*f4*f1^4*f2^3 + 2*f3*f1^3*f2^3 - 3*f1^2*f2^2'
        },
        'f3':{
            0:'0',
            1:'1',
            2:'0'
        },
        'f4':{
            0:'0',
            1:'0',
            2:'1'
        }
    }
}

library = (library_names, library_RHS)

# non_autonomous library; SUPPORTED, should be preferred
# positional arguments are represented by pi, where i is int id of independent variable (p0, p1 and so on)
# non-autonomous system examples are sections 4-6
library_names_na = {
    'sin': (1, 'f1', ['cos'], 0),
    'cos': (1, 'f2', ['sin'], 0),
    'ln': (2, 'f1', ['inv'], 0),
    'inv': (2, 'f2', [], 0),
    'sh': (3, 'f1', ['ch'], 0),
    'ch': (3, 'f2', ['sh'], 0),
    'EK': (4, 'f1', ['EKs', 'EKc', 'EKi'], 0),
    'EKs': (4, 'f2', ['EKc', 'EKi'], 0),
    'EKc': (4, 'f3', ['EKs', 'EKi'], 0),
    'EKi': (4, 'f4', ['EKs', 'EKc'], 0),
    'DV': (5, 'f2', ['Dv'], 3),
    'Dv': (5, 'f1', ['DV'], 3),
    'Hb': (6, 'f1', ['Hbi'], 0),
    'Hbi': (6, 'f2', ['Hb'], 0),
    'sqrt': (7, 'f1', ['isqrt'], 0),
    'isqrt': (7, 'f2', [], 0)
}

library_RHS_na = {
    1:{
        'f1': {
            0: 'f2'
        },
        'f2': {
            0: '-f1'
        }
    },
    2: {
        'f1': {
            0: 'f2'
        },
        'f2': {
            0: '-f2^2'
        }
    },
    3: {
        'f1': {
            0: 'f2'
        },
        'f2': {
            0: 'f1'
        }
    },
    4: {
        'f1': {
            0: 'f2*f4',
            1: 'f4'
        },
        'f2': {
            0: 'f2*f3*f4',
            1: 'f3*f4'
        },
        'f3': {
            0: '-f2^2*f4',
            1: '-f2*f4'
        },
        'f4': {
            0: 'f3*f4^2 - p0*f2^2*f4^3',
            1: '-p0*f4^3*f2'
        }
    },
    5: {
        'f1':{
            0: 'f2'
        },
        'f2':{
            0: '-(s0*p0^2 + s1*p0 + s2)*f1'
        }
    },
    6: {
        'f1':{
            0: '-f1*f2',
            1: '-f1^2*f2',
            2: '-f1^3*f2'
        },
        'f2':{
            0:'(42*f1^5 + 6*p2*f1 + 2*p1)*f1*f2^3 - f2^2',
            1:'(42*f1^5 + 6*p2*f1 + 2*p1)*f1^2*f2^3 - f1*f2^2',
            2:'(42*f1^5 + 6*p2*f1 + 2*p1)*f1^3*f2^3 - 2*f1^2*f2^2'
        }
    },
    7: {
        'f1':{
            0: '0.5*f2'
        },
        'f2':{
            0: '-0.5*f2^3'
        }
    }
}

lib_na = (library_names_na, library_RHS_na)
# for testing purposes
if __name__ == "__main__":
    pass