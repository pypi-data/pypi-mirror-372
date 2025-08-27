"""
Integer factorization: Dixon's method
"""

from math import isqrt, gcd, sqrt, log, exp, ceil
from .primes import sieve_eratosthenes
from .nt import legendre_symbol
from .factor_qs import bytexor, byteset, bytetest


def is_smooth(n: int, factorbase: list, lfb: int) -> bytes | None:
    """Try to factor `n` with respect to a given factorbase.
    Upon success a bytestring, whose bits are the exponents with repect to the factorbase mod 2, is returned.
    Otherwise None."""
    factors = bytearray(b"\x00") * lfb  # we store the exponents mod 2 as bits
    if n < 0:
        byteset(factors, 0)
        n *= -1
    for i, p in enumerate(factorbase):
        k = 0
        while n % p == 0:  # divide by p as many times as possible
            k = (k + 1) % 2  # we only need the exponents mod 2
            n = n // p
        if k:
            byteset(factors, i + 1)
    if n != 1:
        return None  # the number factors if at the end nothing is left
    return factors


def factor_dixon(n: int) -> int | None:
    """Find factors of `n` using the method of Dixon."""
    # first determine the bound B for the factorbase: Choosing B=p^(1/u) Canfield-Erdös-Pomerance gives us
    # the expected running time |B|^2 u^u = u^(u+2) p^(2/u)/log(n). There is no explicit expression for the optimum, hence
    # we use Newton
    u = 2 * sqrt(log(n) / log(log(n)))  # asymptotic value
    for _ in range(3):
        u = (2 * log(n) + u * u * (2 + log(u))) / (
            2 + 3 * u + 2 * u * log(u)
        )  # Newton iteration
    B = int(exp(log(n) / u))

    # B = int(exp(0.5 * sqrt( log(n) * log(log(n)) )*( 1 + 1/log(log(n)) )))
    factorbase = []
    for p in sieve_eratosthenes(B):  # compute the factorbase
        ls = legendre_symbol(n, p)
        if ls == 0:  # we already found a factor;-)
            if n == p:
                return n
            return p
        if ls == 1:  # we only take primes such that n is quadratic residue
            factorbase.append(p)
    lf = len(factorbase) + 1  # length of the factorbase (including -1)
    lfb = ceil(lf / 8)  # the number of bytes we need to store a relation
    m = isqrt(n - 1) + 1

    def process_relation(j: int, relation: bytes):
        "Add a relation to the linear system and reduce the new system."
        nonlocal relation_no, values, relations
        relation_no += 1
        # construct the k'th row of the identity matrix
        rhs = bytearray(b"\x00") * lfb
        byteset(rhs, relation_no)
        relation += rhs  # extend the relation with this row
        values[relation_no] = j  # store the value which lead to the relation
        # do the Gauss elimination
        index = lf  # this will be the index of the first nonzero entry
        # print(f'{j:3}', ' '.join(f'{b:08b}' for b in reversed(relation)))
        for i in range(lf):
            if bytetest(relation, i) and relations[i] is not None:  # make this entry zero if we can (Gauss elimination)
                bytexor(relation, relations[i])
            if bytetest(relation, i) and index == lf:  # is this the index of the first nonzero entry?
                index = i
        # print(f'{j:3}', ' '.join(f'{b:08b}' for b in reversed(relation)))
        if index == lf:  # the new relation is linearly dependent: we have found a linear combination of the 0 vector
            # now we need to determine the factors
            u = 1  # product over all values m - j such that f(m-j) is B-smooth
            v = 1  # sqrt of the product over all f(m-j) which are B-smooth
            w = 1  # save nonsquare terms for the next round
            for i in range(lf):
                if bytetest(relation, lfb * 8 + i):  # select the relations which sum to the 0 vector
                    ui = m + values[i]
                    u = (u * ui) % n
                    vi = ui ** 2 - n
                    d = gcd(w, vi)
                    v = (v * d) % n  # sqrt of the part which is already square
                    w = (w // d) * (vi // d)  # this part is not square yet
            v = v * isqrt(w) % n
            res = gcd(u - v, n)
            if 1 < res < n:
                return res
            relation_no -= 1  # this one did not work, try again
        else:
            relations[index] = relation
        return None

    relation_no = -1
    relations = [None] * lf  # here we will store the relations in case we found a B-smooth number
    values = [None] * lf  # here we will store the values leading to the B-smooth numbers
    for j in range(1,m): # loop over j=0,1,-1,2,-2,...
        if j & 1 == 0:
            j >>= 1
        else:
            j >>= 1
            j *= -1
        relation = is_smooth((j + m) ** 2 - n, factorbase, lfb)  # test if f(j) is B-smooth
        if relation is None:
            continue
        res = process_relation(j, relation)
        if res:
            return res
    return n
