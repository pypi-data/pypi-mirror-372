# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from random import randint, seed  # pylint: disable=C0411
from math import gcd  # pylint: disable=C0411
from kryptools import sieve_eratosthenes, factorint
from kryptools import iroot, ilog, perfect_square, perfect_power, prime_power
seed(0)

maxrange = 1000
numtests = 1000


def test_iroot():
    assert iroot(3, 0) == 0
    assert iroot(3, 1) == 1
    assert iroot(1, 3) == 3
    for _ in range(numtests):
        n = randint(0, 10**10)
        for k in range(2, 12):
            r = iroot(k, n)
            assert r ** k <= n < (r+1) ** k


def test_ilog():
    for n in range(1, maxrange):
        for b in range(2, 5):
            l = ilog(b, n)
            assert b**l <= n < b**(l+1)
    for _ in range(numtests):
        n = randint(1, 10**10)
        for b in range(2, 5):
            l = ilog(b, n)
            assert b**l <= n < b**(l+1)


def test_perfect_square():
    for n in (-1, 0, 1):
        assert perfect_square(n) is None
    for n in range(2, maxrange):
        factors = factorint(n)
        res = perfect_square(n)
        if all(not (k % 2) for k in factors.values()):
            assert isinstance(res, int)
            assert res**2 == n
        else:
            assert res is None


def test_perfect_power():
    for n in (-1, 0, 1):
        assert perfect_power(n) is None
    for n in range(2, maxrange):
        factors = factorint(n)
        res = perfect_power(n)
        g = gcd(*factors.values())
        if g > 1:
            assert isinstance(res, tuple)
            assert res[0]**res[1] == n
            n = -n
            res = perfect_power(n)
            while not g % 2:
                g //= 2
            if g > 1:
                assert isinstance(res, tuple)
                assert res[0]**res[1] == n
            else:
                assert res is None
        else:
            assert res is None
            assert perfect_power(-n) is None


def test_prime_power():
    for n in (-1, 0, 1):
        assert prime_power(n) is None
    for p in sieve_eratosthenes(30):
        for k in range(1, 6):
            assert prime_power(p**k) == (p, k)
    for n in range(2, maxrange):
        factors = factorint(n)
        res = prime_power(n)
        if len(factors) > 1:
            assert res is None
        else:
            p, k = res
            assert n == p**k
