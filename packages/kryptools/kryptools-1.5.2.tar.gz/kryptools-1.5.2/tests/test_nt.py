# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from random import randint, seed  # pylint: disable=C0411
from math import gcd, prod, lcm  # pylint: disable=C0411
from fractions import Fraction  # pylint: disable=C0411
from kryptools import sieve_eratosthenes, is_prime
from kryptools import egcd, crt, cf, convergents, legendre_symbol, jacobi_symbol, sqrt_mod, carmichael_lambda, euler_phi, moebius_mu, is_carmichael_number
seed(0)


def test_egcd():
    maxsize = 100
    for a in range(-maxsize, maxsize):
        for b in range(-maxsize, maxsize):
            g, x, y = egcd(a, b)
            assert g == gcd(a, b)
            assert x * a + y * b == g


def test_crt():
    maxsize = 1000
    numtests = 100
    primes = sieve_eratosthenes(11)
    n = prod(primes)
    for _ in range(numtests):
        x = randint(0, n-1)
        assert x == crt([x % p for p in primes], primes)
    for _ in range(numtests):
        m = []
        for _ in range(10):
            m.append(randint(2, maxsize))
        M = lcm(*m)
        x = randint(0, M-1)


def test_cf():
    for x in (Fraction(21, 11), Fraction(11, 21), Fraction(1, 3)):
        assert convergents(cf(x))[-1] == x


jacobi_data = (
    (1, 1), (0, 1, -1, 0), (0, 1, -1, -1, 1, 0), (0, 1, 1, -1, 1, -1, -1, 0),
    (0, 1, 1, 0, 1, 1, 0, 1, 1, 0), (0, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1, 0),
    (0, 1, -1, 1, 1, -1, -1, -1, -1, 1, 1, -1, 1, 0),
    (0, 1, 1, 0, 1, 0, 0, -1, 1, 0, 0, -1, 0, -1, -1, 0),
    (0, 1, 1, -1, 1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 0))


def test_jacobi_symbol():
    for i, data in enumerate(jacobi_data):
        n = 2 * i + 1
        if is_prime(n):
            for x in range(n+1):
                assert jacobi_symbol(x, n) == data[x]
                assert jacobi_symbol(x, n) == legendre_symbol(x, n)
        else:
            for x in range(n+1):
                assert jacobi_symbol(x, n) == data[x]


def test_sqrt_mod():
    primes = sieve_eratosthenes(11)
    for p in primes:
        for x in range(p):
            y = sqrt_mod(x, p)
            if y is None:
                assert legendre_symbol(x, p) == -1
            else:
                assert pow(y, 2, p) == x


# https://oeis.org/A000010
OEIS_A000010 = [
    1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18, 8, 12, 10, 22, 8, 20,
    12, 18, 12, 28, 8, 30, 16, 20, 16, 24, 12, 36, 18, 24, 16, 40, 12, 42, 20, 24, 22,
    46, 16, 42, 20, 32, 24, 52, 18, 40, 24, 36, 28, 58, 16, 60, 30, 36, 32, 48, 20,
    66, 32, 44]


def test_euler_phi():
    for n in range(1, len(OEIS_A000010)+1):
        assert euler_phi(n) == OEIS_A000010[n - 1]


# https://oeis.org/A002322
OEIS_A002322 = [
    1, 1, 2, 2, 4, 2, 6, 2, 6, 4, 10, 2, 12, 6, 4, 4, 16, 6, 18, 4, 6, 10, 22, 2, 20,
    12, 18, 6, 28, 4, 30, 8, 10, 16, 12, 6, 36, 18, 12, 4, 40, 6, 42, 10, 12, 22, 46,
    4, 42, 20, 16, 12, 52, 18, 20, 6, 18, 28, 58, 4, 60, 30, 6, 16, 12, 10, 66, 16,
    22, 12, 70, 6, 72, 36, 20, 18, 30, 12, 78, 4, 54]


def test_carmichael_lambda():
    for n in range(1, len(OEIS_A002322)+1):
        assert carmichael_lambda(n) == OEIS_A002322[n - 1]


# https://oeis.org/A008683
OEIS_A008683 = [
    1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0, -
    1, 1, 1, 0, -1, 0, -1, 0, 1, 1, -1, 0,
    0, 1, 0, 0, -1, -1, -1, 0, 1, 1, 1, 0, -
    1, 1, 1, 0, -1, -1, -1, 0, 0, 1, -1, 0, 0,
    0, 1, 0, -1, 0, 1, 0, 1, 1, -1, 0, -1, 1, 0, 0, 1, -1, -1, 0, 1, -1, -1, 0, -1, 1,
    0, 0, 1, -1]


def test_moebius_mu():
    for n in range(1, len(OEIS_A008683)+1):
        assert moebius_mu(n) == OEIS_A008683[n - 1]


OEIS_A002997 = [561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341, 41041,
                46657, 52633, 62745, 63973, 75361, 101101, 115921, 126217, 162401, 172081, 188461,
                252601, 278545, 294409, 314821, 334153, 340561, 399001, 410041, 449065, 488881,
                512461, 530881, 552721]


def test_is_carmichael_number():
    for n in range(OEIS_A002997[4]+2):
        assert is_carmichael_number(n) == (n in OEIS_A002997)
    for n in OEIS_A002997:
        assert is_carmichael_number(n) is True
