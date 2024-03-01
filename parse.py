def parse_num(st: str, start: int) -> tuple[float, int]:
    res = ''
    i = start
    while st[i] != '*' and st[i] != ' ' and i < len(st):
        res += st[i]
        i += 1
    return float(res), i

def parse_name(st: str, start: int) -> tuple[str, int]:
    res = st[start]
    i = start
    while st[i] != '^' and st[i] != '*' and st[i] != ' ' and i < len(st):
        res += st[i]
        i += 1
    return res, i

