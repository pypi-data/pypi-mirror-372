"""
Integer Functions:
    iroot(k, n) integer k'th root of n
    ilog(b, n) integer log of n with respect ot base b
    perfect_square(n) test if a number is a perfect square
    perfect_power(n) test if a number is a perfect power
    prime_power(n) test if a number is a prime power
"""
from math import isqrt
from .primes import sieve_eratosthenes, is_prime


def iroot(k: int, n: int) -> int:
    """For a given positive integers `n` and `k`, finds the largest integer `r` such that `r**k <= n`."""
    if not isinstance(k, int) or k < 1:
        raise ValueError(f"k={k} must be a positive integer.")
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"n={n} must be a nonegative integer.")
    if n <= 1 or k == 1:
        return n
    if k == 2: # use the faster internal function
        return isqrt(n)
    l = n.bit_length()
    if k >= l:
        return 1
    r = 1 << ((l-1)//k + 1) # use 2^ceil(l/k) as starting value
    k1 = k - 1
    while True:
        rr = (k1 * r + n // r ** k1) // k  # Newton iteration
        if rr >= r:
            return r
        r = rr


def ilog(b: int, n: int) -> int:
    """For a given positive integer `n`, finds the largest integer `l` such that `b**l <= n`."""
    # https://stackoverflow.com/questions/39190815/how-to-make-perfect-power-algorithm-more-efficient/39191163#39191163
    if not isinstance(b, int) or b < 2:
        raise ValueError(f"base b={b} must a positive integer larger then one.")
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"n={n} must be a positive integer.")
    if n == 1:
        return 0
    if b == 2:
        return n.bit_length() - 1
    lo, blo, hi, bhi = 0, 1, 1, b
    while bhi < n:
        lo, blo, hi, bhi = hi, bhi, hi + hi, bhi * bhi
    while 1 < (hi - lo):
        mid = (lo + hi) // 2
        bmid = blo * pow(b, mid - lo)
        if n < bmid:
            hi, bhi = mid, bmid
        elif bmid < n:
            lo, blo = mid, bmid
        else:
            return mid
    if bhi == n:
        return hi
    return lo


def perfect_square(n: int) -> int | None:
    """Returns the root if `n` is a perfect square and None else."""
    if not isinstance(n, int) or n < 2:
        return None
    s = isqrt(n)
    if s*s == n:
        return s


def perfect_power(n: int) -> tuple | None:
    """Returns integers `(m, p)` with `m**p == n` if `n` is a perfect power and None else."""
    if not isinstance(n, int) or abs(n) < 2:
        return None
    sign = 1
    if n < 0:
        sign = -1
        n = abs(n)
    for p in sieve_eratosthenes(n.bit_length() - 1):
        m = iroot(p, n)
        if pow(m, p) == n:
            if sign == 1:
                return m, p
            if p > 2:
                return -m, p


def prime_power(n: int) -> tuple | None:
    """Returns integers `(p, k)` with `p**k == n` if `n` is a prime power and None else."""
    if not isinstance(n, int) or n < 2:
        return None
    if is_prime(n):
        return (n, 1)
    r = n
    k = 1
    while r.bit_length() > 20:
        k += 1
        r = iroot(k, n)
        if r**k == n and is_prime(r):
            return (r, k)
    for p in sieve_eratosthenes(r - 1):
        k = 0
        while n % p == 0:
            k += 1
            n //= p
        if k >= 1:
            if n == 1:
                return (p, k)
            return None
