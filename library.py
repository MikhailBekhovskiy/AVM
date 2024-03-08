# TODO module for handling loading library from external DB modifiable by user
# currently dictionary representations (preloaded so to speak) are stored here

def get_ext_by_fname(fname: str, lib: dict) -> list:
    return lib[0][fname][2]

library_names = {
    'sin': (1, 'f1', ['cos']),
    'cos': (1, 'f2', ['sin']),
    'ln': (2, 'f1', ['inv']),
    'inv': (2, 'f2', [])
}

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
    }
}

library = (library_names, library_RHS)


# for testing purposes
if __name__ == "__main__":
    pass