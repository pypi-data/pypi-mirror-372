# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from fractions import Fraction  # pylint: disable=C0411
from kryptools import Matrix, gram_schmidt, random_unimodular_matrix


def test_gram_schmidt():
    V = Matrix([[5, 8], [0, 1]], ring=Fraction)
    Vs, M = gram_schmidt(V)
    assert V == Vs * M


def test_random_unimodular_matrix():
    for i in range(2, 5):
        U = random_unimodular_matrix(i)
        U.map(Fraction)
        assert U.det() in (-1, 1)
