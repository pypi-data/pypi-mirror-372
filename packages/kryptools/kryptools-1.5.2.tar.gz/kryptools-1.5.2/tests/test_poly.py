# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from math import prod  # pylint: disable=C0411
from random import sample, choices, randint, seed  # pylint: disable=C0411
from kryptools import Poly, Zmod, GF2, lagrange_interpolation
from kryptools import divisors, moebius_mu
seed(0)
num_tests = 10

def test_Poly():
    p = Poly([2, 0, 2])
    q = Poly([1, 2, 3, 4])
    d, m = q.divmod(p)
    assert d * p + m == q
    for _ in range(num_tests):
        p = Poly([randint(0,100) for _ in range(10)])
        q = Poly([randint(0,100) for _ in range(12)])
        x = randint(0,100)
        assert p(x) == sum((c * x**j for j, c in enumerate(p.coeff)), start=0)
        assert (p + q)(x) == p(x) + q(x)
        assert (p - q)(x) == p(x) - q(x)
        assert (p*q)(x) == p(x) * q(x)

    gf = Zmod(5)
    p = Poly([2, 0, 2], ring = gf)
    q = Poly([1, 2, 3, 4], ring = gf)
    d, m = q.divmod(p)
    assert d * p + m == q
    for _ in range(num_tests):
        p = Poly(gf.random(10))
        q = Poly(gf.random(12))
        x = gf.random()
        assert p(x) == sum((c * x**j for j, c in enumerate(p.coeff)), start=gf(0))
        assert (p + q)(x) == p(x) + q(x)
        assert (p - q)(x) == p(x) - q(x)
        assert (p * q)(x) == p(x) * q(x)

    gf = GF2(8, modulus=0b100011011)
    p = Poly([2, 1, 1, 3], modulus=[1, 0, 0, 0, 1], ring=gf)
    q = p.inv()
    assert p * q == Poly([1], modulus=[1, 0, 0, 0, 1], ring=gf)
    for _ in range(num_tests):
        p = Poly(gf.random(10))
        q = Poly(gf.random(12))
        x = gf.random()
        assert p(x) == sum((c * x**j for j, c in enumerate(p.coeff)), start=gf(0))
        assert (p + q)(x) == p(x) + q(x)
        assert (p - q)(x) == p(x) - q(x)
        assert (p * q)(x) == p(x) * q(x)

def test_rabin():
    for gf,t in [ [Zmod(7), 4], [GF2(4), 3]]:
        order = len(list(gf))
        count = 0
        for i in range(order**t):
            c = []
            while i:
                i, m = divmod(i, order)
                c.append(m)
            c += [0] * (t- len(c)) + [1]
            a = Poly(c, ring=gf)
            if a.rabin_test():
                count += 1
        assert count == sum( moebius_mu(d) * order ** (t // d) for d in divisors(t) ) // t

def test_factor():
    for gf, t in [ [Zmod(7), 14], [GF2(4), 9]]:
        one = Poly([gf(1)])
        for _ in range(20):
            p = one
            while p.degree() < 1:
                p = Poly(gf.random(t), ring =gf)
            factors = p.factor()
            assert prod([f**k for f,k in factors.items()], start = one) == p, p
            for fac in factors:
                assert fac.degree() == 0 or fac.rabin_test(), p

def test_lagrange():
    for gf in [ Zmod(2), Zmod(3), Zmod(5), Zmod(7), Zmod(23), GF2(4), GF2(6)]:
        allpoints = list(gf)
        l = len(allpoints)//2
        for _ in range(10):
            x_coordinates = sample(allpoints, l)
            y_coordinates = choices(allpoints, k = l)
            p = lagrange_interpolation(x_coordinates, y_coordinates)
            assert p.degree() <= len(x_coordinates) - 1
            for x, y in zip(x_coordinates, y_coordinates):
                assert p(x) == y
