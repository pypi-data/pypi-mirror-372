"""
Number theory tools:
    egcd(a,b) extended Euclidean agorithm
    cf(Fraction(m,n)) continued fraction expansions
    convergents() convergents of a continued fraction
    legendre_symbol(a, p) compute the Legendre symbol of a with respect to the prime p
    jacobi_symbol(a, n) compute the Jacobi symbol of a with respect to n
    sqrt_mod(n, p) square root of n modulo a prime p
    euler_phi(n) Euler phi function of n
    carmichael_lambda(n) Carmichael lambda function of n
    moebius_mu(n) Moebius function of n
    is_carmichael_number(n) tests if a number is a Carmichael number
    order(a, n) oder of a in the multiplicative group Z_n^*
    crt([a1, a2, ...],[m1, m2, ...]) Chinese Remainder Theorem
"""
from math import gcd, lcm, prod
from fractions import Fraction

# extended Euclid


def egcd(a: int, b: int) -> (int, int, int):
    """Perform the extended Euclidean agorithm. Returns `gcd`, `x`, `y` such that `a x + b y = gcd`."""
    if a == 0:
        if b < 0:
            return -b, 0, -1
        return b, 0, 1
    if a < 0:
        r0, r1 = -a, b
        x0, x1, y0, y1 = -1, 0, 0, 1
    else:
        r0, r1 = a, b
        x0, x1, y0, y1 = 1, 0, 0, 1
    if b < 0:
        r1 *= -1
        y1 = -1
    while r1 != 0:
        q, r = divmod(r0, r1)
        r0, r1 = r1, r
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return r0, x0, y0


# Continued fractions


def cf(x: Fraction) -> list[int]:
    "Compute the continued fraction expansion of the rational fraction `x`."
    res = []
    x = Fraction(x)
    m = x.numerator
    n = x.denominator
    while True:
        d, m = divmod(m, n)
        res.append(d)
        if not m:
            return res
        m, n = n, m


def convergents(cont_frac: list[int]) -> list[Fraction]:
    "Compute the convergents of a continued fraction expansion."
    res = []

    def recursion(x: int, m: int, mm: int) -> (int, int):
        return x * m + mm, m

    m, mm = 1, 0
    n, nn = 0, 1
    for x in cont_frac:
        m, mm = recursion(x, m, mm)
        n, nn = recursion(x, n, nn)
        res.append(Fraction(m, n))
    return res


# Legendre symbol

def legendre_symbol(a: int, p: int) -> int:
    """Compute the Legendre symbol of `a` with respect to the prime `p`."""
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"{p} must be a prime.")
    a = a % p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) == 1:
        return 1
    return -1


def jacobi_symbol(a: int, n: int) -> int:
    """Compute the Jacobi symbol of `a` with respect to the odd integer `n`."""
    if not isinstance(n, int) or n < 1 or not n % 2:
        raise ValueError(f"{n} must be a positive odd integer.")
    # Crandall/Pomerance Algorithm 2.3.5
    a = a % n
    t = 1
    while a:
        while a % 2 == 0:
            a //= 2
            tmp = n % 8
            if tmp in (3, 5):
                t *= -1
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            t *= -1
        a %= n
    if n == 1:
        return t
    return 0


def sqrt_mod(a: int, p: int) -> int|None:
    """Compute a square root of `a` modulo `p` unsing Cipolla's algorithm."""
    a %= p
    if a in (0, 1):
        return a
    if pow(a, (p - 1) // 2, p) != 1:  # Legendre symbol must be equal one
        return None
    if p % 4 == 3:  # easy case
        return pow(a, (p + 1) // 4, p)
    if p % 8 == 5:
        x = pow(a, (p + 3)//8, p)
        c = pow(x, 2, p)
        if c % p == a:
            return x
        return (x * pow(2, (p - 1)//4, p)) % p
    # Cipolla's algorithm
    for c in range(1, p):  # find a field extension
        tmp = (c * c - a) % p
        if tmp == 0:
            return c
        if pow(tmp, (p - 1) // 2, p) == p - 1:
            break
    r = (c * c - a) % p
    i = (p + 1) // 2
    x1, x2 = c, 1  # compute x^i in Z_p(sqrt(r))
    y1, y2 = 1, 0
    while i > 0:
        if i & 1:  # if i is odd, multiply with x
            y1, y2 = (x1 * y1 + x2 * y2 * r) % p, (x1 * y2 + x2 * y1) % p
        x1, x2 = (pow(x1, 2, p) + pow(x2, 2, p) * r) % p, 2 * (x1 * x2) % p  # now square
        i = i >> 1  # i= i/2
    return y1

# Euler phi, Carmichael function, Moebius function

from .factor import factorint  # pylint: disable=C0413


def euler_phi(n: int) -> int:
    """Euler's phi function of `n`."""
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"{n} is not a positive integer.")
    return prod([(p - 1) * p ** (k - 1) for p, k in factorint(n).items()])


def carmichael_lambda(n: int) -> int:
    """Carmichael's lambda function of `n`."""
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"{n} is not a positive integer.")
    if n == 1:
        return 1
    lam_all = []  # values corresponding to the prime factors
    for p, k in factorint(n).items():
        lam = (p - 1) * p ** (k - 1)
        if p == 2 and k > 2:
            lam = lam // 2
        lam_all += [lam]
    lam = lam_all[0]  # now take the least common multiple of all values
    for l in lam_all[1:]:
        lam = lcm(lam, l)
    return lam


def moebius_mu(n: int) -> int:
    """Moebius' mu function of `n`."""
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"{n} is not a nonegative integer.")
    if n == 0:
        return 0
    factors = factorint(n)
    if any(i > 1 for i in factors.values()):
        return 0
    if len(factors) % 2 == 1:
        return -1
    return 1


def is_carmichael_number(n: int) -> bool:
    """Tests if a number is a Carmichael number using Korselt's criterion."""
    if n < 561:
        return False
    factors = factorint(n)
    if len(factors) == 1:  # prime
        return False
    return max(factors.values()) == 1 and not any((n-1) % (p-1) for p in factors)

# Order in Z_p^*


def order(a: int, n: int, factor=False) -> int:
    """Compute the order of `a` in the group Z_n^*."""
    a %= n
    if a == 0 or gcd(a, n) != 1:
        raise ValueError(f"{a} and {n} are not coprime!")
    factors = {}  # We compute euler_phi(n) and its factorization in one pass
    for p, k in factorint(n).items():  # first factorize n
        for pm, km in factorint(p - 1).items():  # factor p-1 and add the factors
            if pm in factors:
                factors[pm] += km
            else:
                factors[pm] = km
        # if the multiplicity of of p is >1, then we need to add p**(k-1)
        if k > 1:
            if p in factors:
                factors[p] += k - 1
            else:
                factors[p] = k - 1
    order_a = 1  # compute the group order euler_phi(n) as our current guess
    for p, k in factors.items():
        order_a *= p**k
    if factor:  # we compute the factorization of the order along the way
        factors_order = {}  # factorization of the order
    for p, k in factors.items():
        i = 0
        for _ in range(k):
            order_try = order_a // p
            if pow(a, order_try, n) == 1:
                order_a = order_try
                i += 1
            else:
                break
        if factor and i < k:
            factors_order[p] = k - i  # pylint: disable=E0606
    if factor:
        return order_a, factors_order
    return order_a

# Chinese remainder theorem


def crt(a: list[int], m: list[int], coprime=True) -> int:
    """Solve given linear congruences `x % m[j] == a[j]` using the Chinese Remainder Theorem."""
    l = len(m)
    if l != len(a):
        raise ValueError("The lists of numbers and modules must have equal length.")

    if not coprime:
        if not all((isinstance(mi, int) and mi > 1) for mi in m):
            raise ValueError("Moduli must be positive integers larger than one.")
        if not all(isinstance(ai, int) for ai in a):
            raise ValueError("Residues must be integers.")
        # make a copy
        m = [mi for mi in m]  # pylint: disable=R1721
        a = [ai for ai in a]  # pylint: disable=R1721
        for i in range(l):
            for j in range(i + 1, l):
                g = gcd(m[i], m[j])
                if g == 1:  # moduli are coprime, nothing to be done
                    continue
                if (a[i] - a[j]) % g:
                    raise ValueError("Congruences not solvable!")
                for p, k in factorint(g).items():
                    p = p**k  # remove this factor from one of the equations
                    if gcd(m[i] // p, p) == 1:
                        m[i] //= p
                        a[i] %= m[i]
                    else:
                        m[j] //= p
                        a[j] %= m[j]
    for i in reversed(range(l)):
        if m[i] == 1:
            del m[i]
            del a[i]
    l = len(m)

    M = prod(m)
    Mi = [M // m[i] for i in range(l)]
    MNi = [Mi[i] * pow(Mi[i], -1, m[i]) % M for i in range(l)]
    return sum( a[i] * MNi[i] % M for i in range(l) ) % M
