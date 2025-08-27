# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from random import randint, seed  # pylint: disable=C0411
from math import gcd  # pylint: disable=C0411
from kryptools import EC_Weierstrass
seed(0)


def test_EC():
    ec = EC_Weierstrass(239, 3, 1)
    assert len(list(ec)) == ec.order()
    O = ec.inf()  # point at infinity
    assert O in ec
    assert O + O == O
    assert O - O == O
    assert 0 * O == O
    assert 3 * O == O
    assert O.order() == 1
    assert O.dlog(O) == 0
    for _ in range(100):
        P = ec.random()
        assert P in ec
        assert P + O == P
        assert O + P == P
        assert P - O == P
        assert O - P == -P
        assert P - P == O
        assert P + P == 2 * P
        Q = O
        order_P = P.order()
        assert order_P * P == O
        for i in range(9):
            assert i * P == Q
            assert Q.order() == order_P // gcd(order_P, i)
            Q += P
        Q = ec.random()
        assert Q in ec
        assert P + Q == Q + P
        R = ec.random()
        assert R in ec
        assert (P + Q) + R == P + (Q + R)
        for _ in range(10):
            k = randint(0, Q.order()-1)
            R = k * Q
            assert R.dlog(Q) == k
