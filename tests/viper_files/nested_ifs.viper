def func(y: Int) -> Int:
    x = 0
    if y == 2 or y > 9:
        x = 19
        x += y
    else:
        if y % 3 == 0:
            x = 2
            x *= y
    return x + y
