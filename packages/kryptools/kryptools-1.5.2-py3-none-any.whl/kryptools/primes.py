"""
Tools for prime numbers:
    sieve_eratosthenes(B) a tuple of all primes up to including B
    prime_pi(x) number of primes below or equal x
    primorial(x) product of all primes below or equal x
    is_prime(n) test if n is probably prime
    next_prime(n) find the next prime larger or equal n
    previous_prime(n) find the previous prime smaller or equal n
    next_safeprime(n) find the next safe prime larger or equal n
    previous_safeprime(n) find the previous safe prime smaller or equal n
    random_bitlength(l) return a random number with bit lenght l
    random_prime(l) return a random prime with bit length l
    random_strongprime(l) return a random strong prime with factors of bit length l
    is_safeprime(n) test if n is a safe prime
    random_safeprime(l) return a random safe prime with bit length l and ord(2)=(p-1)/2
    is_blumprime(n) test if n is a Blum prime
    random_blumprime(l) return a random Blum prime with bit length l
    miller_rabin_test(n, b) Miller-Rabin primality test with base b
    lucas_test(n) strong Lucas test
"""
from math import isqrt, gcd, floor, ceil, prod
#from random import getrandbits as randbits
from secrets import randbits
from .nt import jacobi_symbol


# Erathostenes

def sieve_eratosthenes(B: float) -> tuple:
    """Returns a tuple of all primes up to (including) `B`."""
    if B < 2:
        return ()
    if B < 3:
        return [2]
    B = floor(B)
    B1 = (isqrt(B) - 1)//2
    B = (B - 1)//2
    # to begin with, all odd numbers are potentially prime
    isprime = bytearray([True]) * (B + 1) # bytearray makes it slightly faster
    # sieve out the primes p=2*q+1 starting at q = 1
    for q in range(1, B1 + 1):
        if isprime[q]:  # sieve out all multiples; numbers p*r with r<p were already sieved out previously
            qq = 2 * q * (q + 1)
            p = 2 * q + 1
            isprime[qq:: p] = bytearray([False]) * ((B - qq) // p + 1)

    return tuple([2] + [2 * q + 1 for q in range(1, B + 1) if isprime[q]])


def prime_pi(x: float) -> int:
    """Prime-counting function pi(x). Returns the number of primes below or equal `x`."""
    return len(sieve_eratosthenes(x))

def primorial(x: float) -> int:
    """Primorial. Returns the product of all primes below or equal `x`."""
    return prod(sieve_eratosthenes(x))


# Primality testing


def miller_rabin_test(n: int, bases: list[int] | int) -> bool:
    """Run a Miller-Rabin test with given bases on `n`."""
    if n < 2:
        return False
    if n % 2 == 0:  # make sure n is odd
        return n == 2

    # write n = m 2^k + 1
    m = (n - 1) // 2
    k = 1
    while m % 2 == 0:
        m //= 2
        k += 1

    if isinstance(bases, int):
        bases = [bases]

    for a in bases:
        a %= n
        if a == 0:
            continue
        b = pow(a, m, n)
        if b in (1, n - 1):
            continue
        for _ in range(1, k):
            b = pow(b, 2, n)
            if b == 0:  # n and a are not coprime
                return False
            if b == 1:  # 1 before -1
                return False
            if b == n - 1:  # -1 found
                break
        else:  # no -1 found
            return False
    return True


def _lucas_sequence(n, D, k):
    """Evaluate a Lucas sequence."""
    # P = 1
    Q = (1 - D)//4
    U = 1
    V = 1
    Qk = Q
    b = k.bit_length()
    while b > 1:
        U = (U * V) % n
        V = (V * V - 2 * Qk) % n
        Qk *= Qk
        b -= 1
        if (k >> (b - 1)) & 1:
            U, V = U + V, V + U * D
            if U & 1:
                U += n
            if V & 1:
                V += n
            U, V = U >> 1, V >> 1
            Qk *= Q
        Qk %= n
    return U % n, V % n, Qk

# https://en.wikipedia.org/wiki/Lucas_pseudoprime#Implementing_a_Lucas_probable_prime_test


def lucas_test(n: int) -> bool:
    """Run a strong Lucas primality test on `n`."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    s = isqrt(n)
    if s * s == n:  # the search for D will not succeed in this case
        return False

    # write n = k 2^s - 1
    k = (n + 1) // 2
    s = 1
    while k % 2 == 0:
        k //= 2
        s += 1

    # Selfridge method for choosing D

    D = 5
    while True:
        g = gcd(abs(D), n)
        if 1 < g < n:
            return False
        if jacobi_symbol(D, n) == -1:
            break
        if D > 0:
            D = -D - 2
        else:
            D = -D + 2

    U, V, Qk = _lucas_sequence(n, D, k)

    if U == 0 or V == 0:
        return True
    for _ in range(1, s):
        V = (V*V - 2*Qk) % n
        if V == 0:
            return True
        Qk = pow(Qk, 2, n)
    return False


def is_prime(n: int, trialdivision: bool = True) -> bool:
    """Test if an integer `n` if probable prime."""
    if not isinstance(n, int) or n < 2:
        return False
    # Test small primes
    if trialdivision:
        for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
                  101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
                  211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293,
                  307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397):
            if n % p == 0:
                return n == p
    if n < 341531:  # https://miller-rabin.appspot.com
        return miller_rabin_test(n, [9345883071009581737])
    if n < 885594169:
        return miller_rabin_test(n, [725270293939359937, 3569819667048198375])
    if n < 350269456337:
        return miller_rabin_test(n, [4230279247111683200, 14694767155120705706, 16641139526367750375])
    if n < 55245642489451:
        return miller_rabin_test(n, [2, 141889084524735, 1199124725622454117, 11096072698276303650])
    if n < 7999252175582851:
        return miller_rabin_test(n, [2, 4130806001517, 149795463772692060, 186635894390467037, 3967304179347715805])
    if n < 585226005592931977:
        return miller_rabin_test(n, [2, 123635709730000, 9233062284813009, 43835965440333360, 761179012939631437, 1263739024124850375])
    if n < 18446744073709551616:
        return miller_rabin_test(n, [2, 325, 9375, 28178, 450775, 9780504, 1795265022])
    if n < 318665857834031151167461:
        return miller_rabin_test(n, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37])
    if n < 3317044064679887385961981:
        return miller_rabin_test(n, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41])
    # Baillie–PSW primality test
    return miller_rabin_test(n, [2]) and lucas_test(n)


def is_safeprime(p: int) -> bool:
    """Tests if a number is a safe prime."""
    if p < 107:
        return p in (5, 7, 11, 23, 47, 59, 83)
    return p % 12 == 11 and is_prime(p) and is_prime((p - 1) // 2)


def is_blumprime(p: int) -> bool:
    """Tests if a number is a Blum prime."""
    return p % 4 == 3 and is_prime(p)


# Generation of primes


def next_prime(n: int) -> int:
    """Find the next prime larger or equal `n`."""
    if n < 3:
        return 2
    n = ceil(n)
    n |= 1  # make sure n is odd
    while not is_prime(n):
        n += 2
    return n


def previous_prime(n: int) -> int:
    """Find the previous prime smaller or equal `n`."""
    if n < 3:
        return 2
    n = floor(n)
    n += (n & 1) - 1  # make sure n is odd
    while not is_prime(n):
        n -= 2
    return n


def next_safeprime(n: int) -> int:
    """Find the next safe prime larger or equal `n`."""
    if n < 6:
        return 5
    if n < 8:
        return 7
    n = n - (n % 12) + 11  # make sure p % 12 = 11
    while not is_safeprime(n):
        n += 12
    return n


def previous_safeprime(n: int) -> int:
    """Find the previous safe prime smaller or equal `n`."""
    if n < 7:
        return 5
    if n < 11:
        return 7
    tmp = (n % 12) + 1
    if tmp != 12:
        n = n - tmp  # make sure p % 12 = 11
    while not is_safeprime(n):
        n -= 12
    return n


def random_bitlength(l: int) -> int:
    "Return a random number with bit lenght `l`."
    l = max(2, l)
    return randbits(l-1) | (1 << l-1)


def random_prime(l: int) -> int:
    """Find a random prime with bit length `l`."""
    l = max(2, int(l))
    while True:
        r = random_bitlength(l)
        r |= 1  # make sure r is odd
        if is_prime(r):
            return r


def random_strongprime(l: int) -> int:
    """Find a random strong prime with factors of bit length `l` using Gordon's algorithm."""
    l = max(2, int(l))
    t = random_prime(l)
    s = random_prime(l)
    u = 2 * t
    uu = u
    while not is_prime(uu + 1):
        uu += u
    r = uu + 1
    u = 2 * r * s
    uu = u + 2 * s * pow(s, r - 2, r) - 1
    while not is_prime(uu):
        uu += u
    return t, s, r, uu


def random_safeprime(l: int) -> int:
    """Find a random safe prime with bit length `l` and `ord(2)=(p-1)/2`."""
    l = max(2, int(l))
    while True:
        r = random_bitlength(l)
        r = r - (r % 24) + 23  # make sure p % 24 = 23
        if is_safeprime(r):
            return r


def random_blumprime(l: int) -> int:
    """Find a random Blum prime with bit length `l`."""
    l = max(2, int(l))
    while True:
        r = random_bitlength(l)
        r = r - (r % 4) + 3  # make sure p % 4 = 3
        if is_prime(r):
            return r
