"""
Lattice tools
"""

from math import prod, floor
from fractions import Fraction
from random import choice, sample
from .la import Matrix, zeros


def hermite_nf(M: Matrix) -> Matrix:
    "Compute the Hermite normal form of a matrix M."
    n, m = M.cols, M.rows
    H = M[:, :]
    j = n - 1
    for i in reversed(range(m)):
        j0 = j
        minimum = abs(H[i, j])  # search for the pivot in the present row
        for jj in range(j):
            tmp = abs(H[i, jj])
            if tmp > 0 and (tmp < minimum or minimum == 0):
                minimum = tmp
                j0 = jj
        if minimum == 0:
            continue  # all entries are zero
        if j0 < j:
            H[:, j], H[:, j0] = (
                H[:, j0],
                H[:, j],
            )  # swap columns, to move the pivot in place
        if H[i, j] < 0:
            H[:, j] *= -1  # make the pivot positive
        jj = j - 1
        while jj >= 0:  # make the row entries left to the pivot zero
            tmp = H[i, jj] // H[i, j]
            H[:, jj] -= tmp * H[:, j]
            if H[i, jj]:
                H[:, j], H[:, jj] = H[:, jj], H[:, j]  # swap columns
            else:
                jj -= 1
        for jj in range(j + 1, n):  # reduce the row entries right to the pivot
            tmp = H[i, jj] // H[i, j]
            H[:, jj] -= tmp * H[:, j]
        #print(H)
        j -= 1
        if j < 0:
            break
    while H.cols > 1 and all(not H[i, 0] for i in range(m)):  # remove zero columns
        H = H[:, 1:]
    return H


def norm2(v: Matrix) -> float:
    "Square of the Euclidean norm of a vector v."
    return sum(map(lambda x: x * x, v))


def gram_schmidt(U: Matrix) -> (Matrix, Matrix):
    "Compute the Gram-Schmidt orthogonalization of the column vectors of a matrix M."
    M = U.eye()
    Us = U[:, :]
    for j in range(1, U.rows):
        tmp = U[:, j]
        for i in range(j):
            M[i, j] = U[:, j].dot(Us[:, i]) / norm2(Us[:, i])
            tmp -= M[i, j] * Us[:, i]
        Us[:, j] = tmp
    return Us, M


def gram_det(U: Matrix) -> float:
    "Compute the Gram determinant of a matrix."
    Us = gram_schmidt(U)[0]
    return prod([Us[:, i].norm() for i in range(U.rows)])


def hadamard_ratio(M: Matrix) -> float:
    "Compute the Hadamard ratio of a matrix."
    m = M.rows
    return (gram_det(M) / prod([M[:, i].norm() for i in range(m)])) ** (1 / m)


def babai_round_cvp(x: Matrix, U: Matrix) -> Matrix:
    "Babai's rounding algorithm for approximately solving the CVP."
    s = U.inv() * x
    k = s.applyfunc(round)
    return U * k


def babai_round_bnd(U: Matrix) -> float:
    "Bound for Babai's rounding algorithm for solving the CVPwith respect to the sup norm."
    return floor(1 / (2 * max(U.inv()[i, :].norm(1) for i in range(U.rows))))


def babai_plane_cvp(x: Matrix, U: Matrix) -> Matrix:
    "Babai's closest plane algorithm for approximately solving the CVP."
    Us = gram_schmidt(U)[0]
    y = x
    for k in range(U.cols - 1, -1, -1):
        y = y - round(y.dot(Us[:, k]) / norm2(Us[:, k])) * U[:, k]
    return (x - y).applyfunc(round)


def babai_plane_bnd(U: Matrix, p=2) -> float:
    "Bound for Babai's closest plane algorithm for solving the CVP with respect to the Euclidean norm (p=2) or sup norm (p=inf)."
    Us = gram_schmidt(U)[0]
    return float(0.5 * min(Us[:, i].norm(p) for i in range(Us.rows)))


def lagrange_lr(V: Matrix) -> Matrix:
    "Lagrange lattice reduction."
    if (V.rows, V.cols) != (2, 2):
        raise ValueError("Lagrange lattice reduction requires dimension two.")
    v1, v2 = V[:, 0], V[:, 1]
    if norm2(v1) > norm2(v2):
        v1, v2 = v2, v1
    v3 = v2 - round(v1.dot(v2) / norm2(v1)) * v1
    while norm2(v3) < norm2(v1):
        v2, v1 = v1, v3
        v3 = v2 - round(v1.dot(v2) / norm2(v1)) * v1
    return Matrix([list(v1), list(v3)]).transpose()


def lll(V: Matrix, delta: float = 0.75, sort: bool = True) -> Matrix:
    "LLL algorithm for lattice reduction."

    assert 0 < delta <= 1, f"LLL reqires 0 < delta={delta} <= 1"
    j = 1
    U = V[:, :]
    U.map(int)
    Us = U[:, :]
    Us.map(Fraction)
    M = U.zeros()
    M.map(Fraction)
    M[0, 0] = norm2(Us[:, 0])  # we store the squared norms on the diagonal
    for l in range(1, U.rows):  # Gram-Schmidt decomposition
        tmp = U[:, l]
        for i in range(l):
            M[i, l] = U[:, l].dot(Us[:, i]) / M[i, i]
            tmp -= M[i, l] * Us[:, i]
        Us[:, l] = tmp
        M[l, l] = norm2(Us[:, l])

    while j < U.rows:
        for i in range(j - 1, -1, -1):  # reduce the weights of the basis vectors
            r = round(M[i, j])
            if r:
                U[:, j] -= r * U[:, i]
                for k in range(j):
                    if k == i:
                        M[k, j] -= r
                    else:
                        M[k, j] -= r * M[k, i]

        newM11 = M[j, j] + M[j - 1, j] ** 2 * M[j - 1, j - 1]
        if (delta * M[j - 1, j - 1] <= newM11):  # Lovasz condition
            j += 1
            continue  # nothing to be done
        # else swap vectors
        U[:, j], U[:, j - 1] = U[:, j - 1], U[:, j]
        # update the Gram-Schmidt decomposition
        oldM11 = M[j - 1, j - 1]
        oldM10 = M[j - 1, j]
        oldM00 = M[j, j]
        oldUs = Us[:, j - 1]
        Us[:, j - 1] = Us[:, j] + M[j - 1, j] * Us[:, j - 1]
        M[j - 1, j - 1] = newM11
        M[j - 1, j] *= oldM11 / M[j - 1, j - 1]
        Us[:, j] = oldUs - M[j - 1, j] * Us[:, j - 1]
        M[j, j] = oldM11 - M[j - 1, j] ** 2 * M[j - 1, j - 1]
        for l in range(j - 1):
            M[l, j], M[l, j - 1] = M[l, j - 1], M[l, j]
        tmp1 = oldM00 / M[j - 1, j - 1]
        tmp2 = oldM10 * oldM11 / M[j - 1, j - 1]
        for l in range(j + 1, U.rows):
            M[j - 1, l], M[j, l] = (
                tmp1 * M[j, l] + tmp2 * M[j - 1, l],
                M[j - 1, l] - oldM10 * M[j, l],
            )
        j = max(j - 1, 1)  # redo the last step

    if sort:  # sort the vectors according to their norm
        tmp = [U[:, j] for j in range(U.rows)]
        tmp.sort(key=norm2)
        for j in range(U.rows):
            U[:, j] = tmp[j]
    return U


def random_unimodular_matrix(n: int, iterations: int = 50, max_val: int = None) -> Matrix:
    "Create a pseudorandom unimodular matrix of dimension n."
    W = zeros(n)
    for i in range(n):
        for j in range(i, n):
            W[i, j] = choice([-1, 1])
    W = W[sample(range(n), n), sample(range(n), n)]
    for _ in range(iterations):
        i, j = sample(range(n), 2)
        tmp = W[i, :] + choice([-1, 1]) * W[j, :]
        if not max_val or max(abs(x) for x in tmp) <= max_val:
            W[i, :] = tmp
        i, j = sample(range(n), 2)
        tmp = W[:, i] + choice([-1, 1]) * W[:, j]
        if not max_val or max(abs(x) for x in tmp) <= max_val:
            W[:, i] = tmp
    return W
