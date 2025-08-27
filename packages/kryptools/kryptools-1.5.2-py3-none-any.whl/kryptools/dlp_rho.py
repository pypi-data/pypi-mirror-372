"""
Discrete log solvers: Pollard rho
"""

from math import gcd, isqrt
from random import randint


def dlog_rho(a: int, b: int, n: int, m: int = None, brent=0) -> int:
    """Compute the discrete log_a(b) in Z_p of an element `a` of order `m` using Pollard's rho algorithm."""
    a %= n
    b %= n
    if not m:
        m = n - 1
    trys = 10
    max_iter = 10 * isqrt(m)  # stop iterating and try a different start value

    def f(x: int, alpha: int, beta: int) -> (int, int, int):
        r = x % 3
        if r == 0:
            return x * a % n, (alpha + 1) % m, beta
        if r == 1:
            return pow(x, 2, n), (2 * alpha) % m, (2 * beta) % m
        return (x * b) % n, alpha, (beta + 1) % m

    while trys > 0:
        j0 = randint(1, m - 1)
        x, alpha_x, beta_x = (b * pow(a, j0, n)) % n, j0, 1  # x_0
        if brent == 0:  # Floyd's cycle detection algorithm
            i = 1
            x, alpha_x, beta_x = f(x, alpha_x, beta_x)  # x_1=f(x_0)
            y, alpha_y, beta_y = f(x, alpha_x, beta_x)  # y_1=f(f(x_0))
            while x != y and i < max_iter:
                i += 1
                x, alpha_x, beta_x = f(x, alpha_x, beta_x)  # f(x_j)
                y, alpha_y, beta_y = f(y, alpha_y, beta_y)
                y, alpha_y, beta_y = f(y, alpha_y, beta_y)  # f(f(y_j))
        else:  # Brent's cycle detection algorithm
            i = 1  # search for a cycle length k < 2^i
            k = 1  # cycle length
            y, alpha_y, beta_y = f(x, alpha_x, beta_x)  # f(x_0)
            while x != y and i < max_iter:
                if i == k:  # start a new power of two
                    x, alpha_x, beta_x = y, alpha_y, beta_y
                    i *= 2
                    k = 0
                y, alpha_y, beta_y = f(y, alpha_y, beta_y)
                k += 1
        # we found a collission (or hit max_iter)
        if x == y and (beta_y - beta_x) % m != 0:
            d = gcd(beta_y - beta_x, m)
            mm = m // d
            if (alpha_x - alpha_y) % d != 0:
                return None  # no solution
            l = (((alpha_x - alpha_y) // d) * pow((beta_y - beta_x) // d, -1, mm)) % mm
            while pow(a, l, n) != b:
                if l >= m:
                    raise ValueError("DLP not solvable.")
                l += mm
            return l
        trys -= 1
    raise RuntimeWarning("Sorry, pollard rho failed!")
