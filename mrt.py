from math import factorial

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
        taylors[k][p]=initial_values[k+1]

def get_series(order: int, initial_values: list, eq_schema: list, mon_schema: list) -> list:
    taylors = []
    for i in range(len(eq_schema) + len(mon_schema)):
        taylors.append([])
    # инициализация - подстановка начальных условий
    for i in range(len(eq_schema)):
        calculate_coef(i, 0, eq_schema, initial_values, mon_schema, taylors)
    # основной цикл делится на два шага;
    # a) посчитать коэффициенты того же порядка для нелинейных мономов;
    # б) посчитать коэффициенты старшего порядка для линейных мономов
    for i in range(order+1):
        for j in range(len(eq_schema), len(taylors)):
            calculate_coef(j, i, eq_schema, initial_values, mon_schema, taylors)
        for j in range(len(eq_schema)):
            calculate_coef(j, i+1, eq_schema, initial_values, mon_schema, taylors)
    return taylors

def taylor_printout(coefs: list, t0: float):
    res = str(coefs[0])
    for i in range(1, len(coefs)):
        res += f' + {coefs[i]:.2f} * (t-{t0:.2f})^{i}'
    return res

def taylor_eval(coefs, t, t0):
    res = coefs[0]
    pow = t - t0
    for i in range(1, len(coefs)):
        res += pow * coefs[i]
        pow *= t - t0
    return res

# полином от одной вещественной переменной
def poly_eval(coefs, x):
    res = coefs[0]
    cur_pow = x
    for i in range(1, len(coefs)):
        res += cur_pow * coefs[i]
        cur_pow *= x
    return res

# оценки
# функция для подсчета нормы матрицы (оценка линейных систем)
def matrix_norm(A):
    maxx = -1
    for row in A:
        si = 0
        for el in row:
            si += abs(el)
        if si > maxx:
            maxx = si
    return si

# трансформирование матрицы масштабирующими множителями для линейных систем
def scale_matrix(A, alpha):
    B = []
    for i in range(len(A)):
        B.append([])
        for j in range(len(A)):
            B[i].append(A[i][j] * alpha[j]/alpha[i])
    return B

def inv_matrix_norm(A):
    return 1 / matrix_norm(A)

# ряд Тейлора для e^tau
def e_tau(tau, M=5):
    res = 0
    for i in range(M+1):
        res += tau ** i / factorial(i)
    return res

# эвристический подсчет масштабирующих множителей для линейной системы
# в терминах вещественных переменных
# и выбор соответствующего максимального шага
def lin_scale_step(taylors, A, tau=0.5, alphI=1):
    # число фазовых переменных
    n = len(A)
    # 1 поделить на норму матрицы А
    rho = inv_matrix_norm(A)
    # посчитать e^tau
    e_t = e_tau(tau)
    sigmas = []
    # посчитать сигмы для вещественного времени
    # (в комплексном случае вместо tau комплексное число модуля tau
    # и аргумента, максимизирующего все выражение)
    for i in range(n):
        sigmas.append(abs(poly_eval(taylors[i], rho*tau))/(e_t-1))
    # подсчет возможных вариантов alpha и поиск максимального ро для шага
    alphas = [0] * len(A)
    max_rho = -1
    for I in range(n):
        for i in range(n):
            if i == I:
                alphas[i] = alphI
            else:
                if sigmas[I] == 0:
                    sI = 0.001
                else:
                    sI = sigmas[I]
                alphas[i] = alphI*sigmas[i]/sI
        rho = inv_matrix_norm(scale_matrix(A, alphas))
        if rho > max_rho:
            max_rho = rho
    return max_rho * tau

# промежуточная реализация метода рядов Тейлора с заданным списком шагов и заданными порядками разложения
def base_tsm(eq_schema: list, mon_schema: list, initial_values: list, timepoints: list, ordering: list):
    ts = timepoints
    orders = ordering
    iv = initial_values
    eqs = eq_schema
    schema = mon_schema
    res = []
    for i in range(len(ts)):
        # порядок очередного разложения
        order = orders[i]
        t = ts[i]
        t0 = iv[0]
        T = get_series(order, iv, eqs, schema)
        iv = [t]
        for i in range(1, len(eqs) + 1):
            iv.append(taylor_eval(T[i-1], t, t0))
        res.append(iv[1:])
    return res


if __name__=="__main__":
    # схема, описывающая уравнения.
    # кортежи - коэффициент и порядковый номер монома.
    # первый элемент - свободный член
    eqs = [
        [-5, (1, 0), (1, 1)],
        [2, (3, 0), (-4, 1)]
    ]
    A = [
        [1, 1],
        [3, -4]
    ]
    a = [-5, 2]
    # схема, описывающая, мономы каких индексов при произведении дают нелинейный моном
    # 0: первая переменная
    # len(eqs) - 1: последняя переменная (в примере уравнений два, последняя переменная под индексом 1)
    # старше - нелинейные мономы; только они входят в схему
    schema = []
    mons = ['x1', 'x2']
    # начальные условия
    iv = [1, 2, -3]
    # посчитать коэффициенты Тейлора около начальной точки
    T = get_series(5, iv, eqs, schema)
    for i in range(len(T)):
        print(f'{mons[i]} = {taylor_printout(T[i], iv[0])}')
    # посчитать масштабирующие множители
    h = lin_scale_step(T, A)
    print(f'Chosen stepsize: {h}')
    
    