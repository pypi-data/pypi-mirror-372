# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from fractions import Fraction  # pylint: disable=C0411
from kryptools import Matrix, Zmod


def test_Matrix():
    M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 12]])
    Z = M.zeros()
    assert M
    assert M == M + Z
    assert not Z
    Z[0] = 1
    assert Z
    assert Z != Z.zeros()
    assert len(M) == 3 * 3
    assert M[0] == 1
    assert M[:] == [1, 2, 3, 4, 5, 6, 7, 8, 12]
    assert 2 * M - M == M
    M.map(Fraction)
    Mi = M.inv()
    assert M * Mi == M.eye()

    Z_11 = Zmod(11)
    assert 2 * M - M == M
    M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 12]], ring=Z_11)
    Mi = M.inv()
    assert M * Mi == M.eye()
