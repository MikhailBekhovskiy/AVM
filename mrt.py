# начальные условия
iv = [1, -1]

# схема, описывающая уравнения.
# кортежи - коэффициент и порядковый номер монома.
# первый элемент - свободный член
eqs = [
    [-5, (1, 3), (1, 0)],
    [0, (1, 5), (4, 0)]
]

# схема, описывающая, мономы каких индексов при произведении дают нелинейный моном
# 0: первая переменная
# len(eqs) - 1: последняя переменная (в примере уравнений два, последняя переменная под индексом 1)
# старше - нелинейные мономы; только они входят в схему
# (0,0) - x1^2;
# (2,1) - x1^2*x2;
# (1,1) - x2^2;
# (4,1) - x2^3;
schema = [(0, 0), (2, 1), (1, 1), (4, 1)]
mons = ['x1', 'x2', 'x1^2', 'x1^2 * x2', 'x2^2', 'x2^3']


def calculate_coef(k:int, p:int, eq_schema: list, initial_values: list, mon_schema: list, taylors: list):
    # добавляем очередную ячейку в k-ое разложение
    taylors[k].append(0)
    # если обсчитывается нелинейный моном
    if k >= len(eq_schema):
        # выбираем мономы согласно схеме
        mons = mon_schema[k-len(eq_schema)]
        # перемножаем нужные степени из мономов разложения и суммируем
        for l in range(p+1):
            taylors[k][p] += taylors[mons[0]][l] * taylors[mons[1]][p-l]
    # если обсчитывается старший член линейного монома (фазовой переменной)
    elif p > 0:
        # выбираем уравнение
        equation = eq_schema[k]
        # начальное значение -- свободный член уравнения
        taylors[k][p] = equation[0]
        # считаем согласно диф. уравнению 
        for i in range(1, len(equation)):
            taylors[k][p] += equation[i][0] * taylors[equation[i][1]][p-1]
        taylors[k][p] /= p
    # нулевой коэффициент фазовой переменной - начальное условие
    else:
        taylors[k][p]=initial_values[k]

def get_series(order: int, initial_values: list, eq_schema: list, mon_schema: list) -> list:
    taylors = []
    for i in range(len(eq_schema) + len(mon_schema)):
        taylors.append([])
    for i in range(len(eq_schema)):
        calculate_coef(i, 0, eq_schema, initial_values, mon_schema, taylors)
    for i in range(order+1):
        for j in range(len(eq_schema), len(taylors)):
            calculate_coef(j, i, eq_schema, initial_values, mon_schema, taylors)
        for j in range(len(eq_schema)):
            calculate_coef(j, i+1, eq_schema, initial_values, mon_schema, taylors)
    return taylors

def taylor_printout(coefs: list):
    res = str(coefs[0])
    for i in range(1, len(coefs)):
        res += f' + {coefs[i]} * (t-t0)^{i}'
    return res


if __name__=="__main__":
    for p in range(11):
        print(f'Order {p+1} solution:')
        T = get_series(p, iv, eqs, schema)
        for i in range(len(mons)):
            print(f'{mons[i]} = ', taylor_printout(T[i]))
    
    