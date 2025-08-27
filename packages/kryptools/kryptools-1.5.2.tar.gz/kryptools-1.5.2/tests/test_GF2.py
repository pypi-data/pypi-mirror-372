# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from random import randint, seed  # pylint: disable=C0411
from kryptools import GF2, euler_phi
seed(0)

num_tests = 50

def test_GF2_ops():
    for n, modulus in [(4, None), (8, None), (8, 0b100011011), (12, None), (128, 0b11100001 << 120)]:
        gf = GF2(n, modulus=modulus)
        assert gf(1)
        assert not gf(0)
        assert gf(1) == gf(1)
        assert gf(1) != gf(0)
        assert gf(0) != 0
        if gf.degree < 17:
            assert len(list(gf)) == gf.order
            assert len(list(gf.star())) == gf.order - 1
            assert len(list(gf.generators())) == euler_phi(gf.order - 1)
        for _ in range(num_tests):
            a = gf(randint(0, gf.order-1))
            b = gf(randint(0, gf.order-1))
            assert (a + b).poly() == a.poly() + b.poly()
            assert (a - b).poly() == a.poly() - b.poly()
            assert (a * b).poly() == a.poly() * b.poly()
            if a:
                assert (a**-1).poly() == a.poly().inv()
            if b:
                assert (a / b).poly() == a.poly() / b.poly()
            assert a.sqrt()**2 == a
        with pytest.raises(ValueError):
            gf(1) / gf(0)  # pylint: disable=W0106
        with pytest.raises(ValueError):
            gf(0)**-1  # pylint: disable=W0106

def test_GF2_order():
    for n in range(1, 8):
        gf = GF2(n)
        assert len(list(gf)) == gf.order
        assert len(list(gf.star())) == gf.order - 1
        assert len(list(gf.generators())) == euler_phi(gf.order - 1)

def test_GF2P_order():
    for n in range(1, 9):
        gf = GF2(n)
        one = gf(1)
        for x in gf.star():
            o = 1
            xx = x
            while xx != one:
                o += 1
                xx *=x
            assert o == x.order()

def test_GF2_generator():
    for n in range(1, 9):
        gf = GF2(n)
        a = gf.generator()
        assert a.order() == gf.mult_order
