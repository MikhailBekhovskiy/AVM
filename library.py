# TODO module for handling loading library from external DB modifiable by user
# currently dictionary representations (preloaded so to speak) are stored here
library_names = {
    'sin': (1, 'f1'),
    'cos': (1, 'f2'),
    'ln': (2, 'f1'),
    'inv': (2, 'f2')
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

global_var_dict = dict()

library = (library_names, library_RHS)


# for testing purposes
if __name__ == "__main__":
    pass