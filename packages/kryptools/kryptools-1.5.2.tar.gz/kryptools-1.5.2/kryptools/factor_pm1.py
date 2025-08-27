"""
Integer factorization: Pollard's p-1 method
"""

from math import gcd, log, isqrt, floor, log10
from .primes import sieve_eratosthenes


def _pm1_parameters(B1: int, B2: int, primes: tuple = None) -> tuple:
    "Precompute parameters for the p-1 method."
    if not primes:
        primes = sieve_eratosthenes(B2)

    stage_one = 1
    stage_two_deltas = []
    pp = 0
    for p in primes:
        if p <= B1:
            stage_one *= p**int(log(B1, p))
        elif p <= B2:
            stage_two_deltas.append(p - pp)  # pylint: disable=W0631
            pp = p
        if p > B2:
            break

    return stage_one, stage_two_deltas


def factor_pm1(n: int, B1: int | None = None, B2: int | None = None, x: int = 2, pm1_parameters: tuple = None, verbose: int = 0) -> int | None:
    "Factors a number `n` using Pollard's p-1 method."
    if pm1_parameters:
        B1, B2, stage_one, stage_two_deltas = pm1_parameters
    else:
        if not B1:
            B1 = min(1000_000, isqrt(isqrt(n)) + 2)
        if not B2 or B2 < B1:
            B2 = 100 * B1
        stage_one, stage_two_deltas = _pm1_parameters(B1, B2)

    if verbose:
        print(f"Factoring (Pollard p-1, B1={B1}, B2={B2}): {n} ({floor(log10(n)) + 1} digits)", end ="")

    # stage one
    if verbose > 1:
        print("\nWorking 1", end="")
    x = pow(x, stage_one, n)
    g = gcd(x - 1, n)
    if g == n:  # we hit a multiple of n
        if verbose:
            print("\nFailed after stage one.")
        return None
    if 1 < g:
        if verbose > 1:
            print("\nFactor found in stage one.")
        return g

    # stage two
    if verbose > 1:
        print(",2", end="")
    saved = {}
    y = pow(x, stage_two_deltas[0], n)
    D = (y - 1) % n
    for k, d in enumerate(stage_two_deltas[1:]):
        if d not in saved:
            saved[d] = pow(x, d, n)
        y = y * saved[d] % n
        D = D * (y - 1) % n
        if k % 20 == 0:
            g = gcd(D, n)
            if g == n:
                if verbose > 1:
                    print("\nFailed during stage two.")
                return None
            if 1 < g:
                if verbose > 1:
                    print("\nFactor found in stage two.")
                return g
    g = gcd(D, n)
    if 1 < g < n:
        if verbose > 1:
            print("\nFactor found in stage two.")
        return g
    if verbose:
        print("\nFailed after stage two.")
    return None
