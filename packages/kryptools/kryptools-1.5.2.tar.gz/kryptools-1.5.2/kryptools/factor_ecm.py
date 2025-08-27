"""
Integer factorization: Lentra's ECM
"""

from math import gcd, isqrt, log, floor, log10
from random import randint, seed
from .primes import sieve_eratosthenes
seed(0)

# Crandall and Pomerance: Primes (doi=10.1007/0-387-28979-8)
# Algorithm 7.2.7


def dbl(P, c2, p):
    "EC Montgommery point doubling"
    # c2 = c - 2
    t1 = (P[0] + P[1]) % p
    t2 = (P[0] - P[1]) % p
    t3 = P[0] * P[1] % p
    return pow(t1 * t2, 2, p), ((t1 * t1 + c2 * t3) % p) * 4 * t3 % p


def add(P1, P2, P3, p):
    "EC Montgommery point addition"
    t1 = pow(P1[0] * P2[0] - P1[1] * P2[1], 2, p)
    t2 = pow(P1[0] * P2[1] - P2[0] * P1[1], 2, p)
    return P3[1] * t1 % p, P3[0] * t2 % p


def mult(k, P, c2, p):
    "EC Montgommery point multiplication"
    if k == 1:
        return P
    if k == 2:
        return dbl(P, c2, p)
    Q = dbl(P, c2, p)
    R = P
    for i in bin(k)[3:-1]:
        if i == "1":
            R = add(Q, R, P, p)
            Q = dbl(Q, c2, p)
        else:
            Q = add(R, Q, P, p)
            R = dbl(R, c2, p)
    if k % 2:
        return add(Q, R, P, p)
    return dbl(R, c2, p)

# Crandall and Pomerance: Primes (doi=10.1007/0-387-28979-8)
# Algorithm 7.4.4 (Inversionless ECM)


def _ecm_parameters(B1: int, B2: int | None = None, D: int | None = None, primes: tuple | None = None) -> tuple:
    "Precompute parameters for the ECM method."

    # Stage-one/two limits must be even
    if B1 % 2:
        raise ValueError("B1 must be even.")
    if not B2:
        B2 = 100 * B1
    if B2 % 2:
        raise ValueError("B2 must be even.")
    if not D:
        D = min(isqrt(B2), B1 // 2 - 1)
    if not primes:
        primes = sieve_eratosthenes(B1 - 1 + ((B2 - B1 + 1) // (2 * D) + 1) * 2 * D)

    stage_one = 1
    for p in primes:
        if p > B1:
            break
        stage_one *= p**int(log(B1, p))

    stage_two_deltas = {}
    r = B1 - 1
    stage_two_deltas[r] = []
    for p in primes:
        if p < r:
            continue
        if p <= r + 2 * D:
            stage_two_deltas[r].append((p - r) // 2)
        else:
            r += 2 * D
            while p > r + 2 * D:
                stage_two_deltas[r] = []
                r += 2 * D
            stage_two_deltas[r] = [(p - r) // 2]
    return D, stage_one, stage_two_deltas


def factor_ecm(n: int, B1: int | None = None, B2: int | None = None, curves: int = 150, ecm_parameters: tuple | None = None, verbose: int = 0) -> int | None:
    "Factors a number `n` using Lentsta's ECM method."

    if ecm_parameters:
        B1, B2, curves, D, stage_one, stage_two_deltas = ecm_parameters
    else:
        if not B1:
            B1 = min(1000_000, isqrt(n)//200 + 2)
        # Stage-one/two limits must be even
        B1 += B1 & 1
        if not B2:
            B2 = 100 * B1
        D, stage_one, stage_two_deltas = _ecm_parameters(B1, B2)

    if verbose:
        print(f"Factoring (ECM, B1={B1}, B2={B2}): {n} ({floor(log10(n)) + 1} digits)")
    if verbose > 1:
        print("Working ", end="")
    for _ in range(curves):
        # find a random curve
        if verbose > 1:
            print("C", end="")  # stage one
        sigma = randint(6, n - 1)
        u = (sigma**2 - 5) % n
        v = (4 * sigma) % n
        try:
            c = (pow(v - u, 3, n) * (3 * u + v) * pow(4 * u**3 * v, -1, n) - 2) % n
        except ValueError:
            if verbose > 1:
                print("\nFactor found.")
            m = gcd(u, n)
            if m > 1:
                return m
            m = gcd(v, n)
            if m > 1:
                return m
            return 2
        c2 = (c - 2) % n
        # and a point on the curve (or its twist)
        Q = (pow(u, 3, n), pow(v, 3, n))
        # Stage one
        if verbose > 1:
            print("1", end="")
        Q = mult(stage_one, Q, c2, n)
        if Q[1] == 0:
            continue
        g = gcd(Q[1], n)
        if g > 1:
            if verbose > 1:
                print("\nFactor found.")
            return g

        # Stage two
        if verbose > 1:
            print("2", end="")
        S = [dbl(Q, c2, n)]
        S.append(dbl(S[0], c2, n))

        for i in range(2, D):
            S.append(add(S[i - 1], S[0], S[i - 2], n))

        beta = []
        for i in range(D):
            beta.append((S[i][0] * S[i][1]) % n)
        g = 1
        T = mult(B1 - 2 * D - 1, Q, c2, n)
        R = mult(B1 - 1, Q, c2, n)
        for r in range(B1 - 1, B2, 2 * D):
            alpha = R[0] * R[1] % n
            for delta in stage_two_deltas[r]:
                g = g * ((R[0] - S[delta - 1][0]) * (R[1] + S[delta - 1][1]) - alpha + beta[delta - 1]) % n
                if g == 0:
                    break
            if g == 0:
                break
            g = gcd(g, n)
            if 1 < g:
                if verbose > 1:
                    print("\nFactor found.")
                return g
            R, T = add(R, S[D - 1], T, n), R

        g = gcd(g, n)
        if 1 < g < n:
            if verbose > 1:
                print("\nFactor found.")
            return g

    if verbose > 1:
        print(f"\nNo factor after trying {curves} curves.")
