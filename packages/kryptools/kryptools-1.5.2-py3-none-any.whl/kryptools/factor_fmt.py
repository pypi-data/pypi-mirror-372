"""
Integer factorization: Fermat's method
"""

from math import isqrt, floor, log10


def factor_fermat(n: int, maxsteps: int | None = None, verbose: int = 0) -> list:
    """Find factors of `n` using the method of Fermat."""
    if not isinstance(n, int) or n < 1:
        raise ValueError("Number to be factored must be a positive integer!")
    if verbose:
        print(f"Factoring (Fermat): {n} ({floor(log10(n)) + 1} digits)")
    factors = []
    parameters = {11: (12, 6), 23: (12, 0),
                  5: (6, 3), 17: (6, 3),
                  19: (4, 2), 7: (4, 0),
                  1: (2, 1), 13: (2, 1)}
   # Speedup only works if n is neiter a multipl of 2 or 3
    for p in (2, 3):
        while n % p == 0:
            factors.append(p)
            n //= p
    if n == 1:
        return factors
    start = isqrt(n - 1) + 1
    step, mod = parameters[n % 24]
    start += (mod - start) % step
    if verbose > 1:
        print("Working ", end="")
    maxa = (n + 9) // 6 + 1
    if maxsteps:
        maxsteps = max(1, maxsteps)
        maxa = min(maxa, start + maxsteps * step + 1)
    for a in range(start, maxa, step):
        if verbose > 1:
            print(".", end="")
        b = isqrt(a * a - n)
        if b * b == a * a - n:
            factors.append(a - b)
            factors.append(a + b)
            if verbose > 1:
                print("")
            return factors
    factors.append(n)
    if verbose > 1:
        print("")
    return factors
