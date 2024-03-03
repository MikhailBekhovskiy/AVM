from polynom import *

global_var_dict = dict()



with open('input.txt', 'r') as f:
    strings = f.readlines()

for i in range(len(strings)):
    strings[i] = strings[i].strip('\n')

polynoms = [None] * len(strings)
mass_prod = ''
for i in range(len(strings)):
    P = parse_poly(strings[i], global_var_dict)[0]
    polynoms[i] = P
    mass_prod += f'({P.printout()})'
mass_res = polynoms[0]
for i in range(1, len(polynoms)):
    mass_res = mass_res.prod(polynoms[i])

print(mass_prod,'=',mass_res.printout())
