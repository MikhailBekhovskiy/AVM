from system import *
from os import mkdir, listdir, getcwd
from os.path import isdir
import subprocess

PATH = getcwd()
PREAMBLE = '''\\documentclass[10pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[russian]{babel}
\\usepackage[OT1]{fontenc}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{graphicx}
\\usepackage{breqn}
\\begin{document}\n'''
FIN = '\\end{document}'

def batch_do_input():
    fnames = [fn[:-4] for fn in listdir('input/')]
    print('Found ', len(fnames), ' files in input directory.')
    for fname in fnames:
        if not isdir(f'output/{fname}'):
            mkdir(f'output/{fname}')
        OUTPATH = PATH + '/output/' + fname
        with open(f'output/{fname}/main.tex', 'w') as f:
            print('Trying ', fname)
            S = System(filename=fname + '.txt')
            f.write(PREAMBLE)
            f.write('Input system:\n\n')
            f.write(S.__str__(latex=True))
            S, R = S.insert_av(lib_na)
            # print(R)
            S.av_ders(R, lib_na)
            # S.canonize()
            f.write('=================\n\nResult:\n\n')
            f.write(S.__str__(latex=True))
            f.write(FIN)
        subprocess.run(f'pdflatex -output-directory={OUTPATH}  -synctex=1 -interaction=batchmode {OUTPATH}/main.tex', shell=True, executable="/bin/bash")
        print(fname, ' has been processed.')

def print_lib(path: str=PATH+'/library_print'):
    systs = library_RHS_na
    naming = library_names_na
    with open(f'{path}/main.tex', 'w') as f:
        f.write(PREAMBLE)
        for i in range(len(systs)):
            s = System(desc=systs[i])
            funcs = get_ext_names(i, naming)
            f.write('\\textbf{Library system #' + str(i+1) + '}\n\n')
            f.write('\\textit{Function definitions:}\n\n')
            for func in funcs:
                if funcs[func][1] == 0:
                    pars = []
                elif funcs[func][1] == 1:
                    pars = ['p']
                else:
                    pars = [f'p{j}' for j in range(1, funcs[func][1] + 1)]
                if funcs[func][2] == 0:
                    args = []
                elif funcs[func][2] == 1:
                    args = ['t']
                else:
                    args = [f't{j}' for j in range(1, funcs[func][2] + 1)]
                f.write('$' + func_name2latex(func, pars, args) + ' = ' + var_name2latex(funcs[func][0]) + '$,')
            f.write('\n\n')
            f.write(s.__str__(True))
            f.write('\n')
        f.write(FIN)
    subprocess.run(f'pdflatex -output-directory={path} -synctex=1 -interaction=batchmode {path}/main.tex', shell=True, executable='/bin/bash')

if __name__ == "__main__":
    print_lib()
    batch_do_input()