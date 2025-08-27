"""
Integer factorization: Pollard's rho method
"""

from math import gcd, isqrt, floor, log10
from random import randint


def factor_rho(n: int, x: int = 2, maxinit: int = 10, maxiter: int = 1000, brent: bool = True, verbose: int = 0) -> int | None:
    """Factor `n` using the Pollard's rho method with start value `x`."""
    if not maxiter:
        maxiter = 10 * isqrt(n)  # stop iterating and try a different start value

    def f(x: int) -> int:
        return (pow(x, 2, n) + 2) % n

    if verbose:
        print(f"Factoring (Pollard rho, maxinit={maxinit}, maxiter={maxiter}): {n} ({floor(log10(n)) + 1} digits)", end="")

    if verbose > 1:
        print("\nWorking ", end="")
    for _ in range(maxinit):
        if verbose > 1:
            print("X", end="")
        if not brent:  # Floyd's cycle detection algorithm
            i = 1
            x = f(x)  # x_1=f(x_0)
            y = f(x)  # y_1=f(f(x_0))
            while gcd(x - y, n) == 1 and i < maxiter:
                if verbose > 1 and i % 100 == 0:
                    print(".", end="")
                i += 1
                x = f(x)  # f(x_j)
                y = f(y)
                y = f(y)  # f(f(y_j))
        else:  # Brent's cycle detection algorithm
            i = 1  # search for a cycle length k < 2^i
            k = 1  # cycle length
            y = f(x)  # f(x_0)
            while gcd(x - y, n) == 1 and i < maxiter:
                if verbose > 1 and (i+k) % 100 == 0:
                    print(".", end="")
                if i == k:  # start a new power of 2
                    x = y
                    i *= 2
                    k = 0
                y = f(y)
                k += 1
        # we found a collission (or hit max)
        tmp = gcd(x - y, n)
        if 1 < tmp < n:
            if verbose > 1:
                print("\nFactor found.")
            return tmp
        x = randint(1, n - 1)  # new x_0
    if verbose > 1:
        print("\nFailed.")
