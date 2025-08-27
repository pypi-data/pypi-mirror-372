# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from random import randint, seed  # pylint: disable=C0411
from kryptools import dlog, primorial

seed(0)

with pytest.raises(ValueError):
    dlog(1, 3, 10)


def test_dlogt():
    for data in (
        [557639, 278819, 2],
        [24570203447, 12285101723, 2],
        [28031135240181527, 14015567620090763, 2],
        [primorial(379)+1, primorial(379)//3, 383]):
        p, m, a = data  # m is the order of a in Z_p
        x = randint(2, m - 1)
        b = pow(a, x, p)
        assert dlog(a, b, p) == x
