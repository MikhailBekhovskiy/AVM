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

if __name__ == "__main__":
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
            S.canonize()
            f.write('=================\n\nResult:\n\n')
            f.write(S.__str__(latex=True))
            f.write(FIN)
        subprocess.run(f'pdflatex -output-directory={OUTPATH}  -synctex=1 -interaction=batchmode {OUTPATH}/main.tex', shell=True, executable="/bin/bash")
        print(fname, ' has been processed.')