# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from kryptools import factorint, is_prime


def myprod(factors: dict) -> int:
    n = 1
    for p in factors:
        assert is_prime(p)
        n *= p**factors[p]
    return n


def test_factorint():
    assert factorint(0) == {0: 1}
    assert factorint(1) == {}  # pylint: disable=C1803
    for n in (1489576198567193874913874619387459183543154617315437135656,
              2**128 - 1,
              4521089809**7):
        assert n == myprod(factorint(n))
