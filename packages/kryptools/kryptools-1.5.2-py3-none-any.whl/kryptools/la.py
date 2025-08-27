"""
Linear algebra
"""

from math import inf, sqrt, prod
from numbers import Number
from fractions import Fraction

class Matrix:
    """
    Matrix class.

    Example:

    To define a matrix use
    >>> Matrix([[1, 2], [3, 4]])
    [1, 2]
    [3, 4]
    """

    print_pre = "[ "
    print_post = " ]"
    print_sep = ", "

    def __init__(self, matrix, ring=None):
        if not isinstance(matrix[0], list | tuple):
            matrix = [[x] for x in matrix]
        self.matrix = matrix
        self.cols = len(matrix[0])
        self.rows = len(matrix)
        for i in range(1, self.rows):
            if len(matrix[i]) != self.cols:
                raise ValueError("All matrix rows must have equal length!")
        if ring:
            self.map(ring)

    def __repr__(self) -> str:
        out = [self.__class__.print_pre] * self.rows
        for j in range(self.cols):
            tmp = [""] * self.rows
            max_len = 0
            for i in range(self.rows):
                tmp[i] = str(self.matrix[i][j])
                max_len = max(max_len, len(tmp[i]))
            for i in range(self.rows):
                out[i] += " " * (max_len - len(tmp[i])) + tmp[i]
                if j < self.cols - 1:
                    out[i] += self.__class__.print_sep
        for i in range(self.rows):
            out[i] += self.__class__.print_post
        return '\n'.join(out)

    def _repr_mimebundle_(self, **kwargs):  # pylint: disable=W0613
        return {
            "text/plain": repr(self),
            "text/latex": "$\\displaystyle" + self.latex() + "$"
        }

    def latex(self) -> str:
        "Produce LaTeX code for the matrix."
        res = "\\begin{pmatrix}\n"
        for row in self.matrix:
            res += " & ".join(map(str, row)) + '\\\\\n'
        res += '\\end{pmatrix}'
        return res

    def __len__(self):
        return self.cols * self.rows

    def __getitem__(self, item):
        if isinstance(item, tuple):
            i, j = item
            if isinstance(i, int) and isinstance(j, int):
                return self.matrix[i][j]
            if isinstance(i, int):
                rows = [i]
            elif isinstance(i, list):
                rows = i
            else:
                rows = range(self.rows)[i]
            if isinstance(j, int):
                cols = [j]
            elif isinstance(j, list):
                cols = i
            else:
                cols = range(self.cols)[j]
            return self.__class__([[self.matrix[i][j] for j in cols] for i in rows])
        if isinstance(item, int):
            i, j = divmod(item, self.cols)
            return self.matrix[i][j]
        return [self.matrix[k // self.cols][k % self.cols] for k in range(self.cols * self.rows)[item]]

    def __setitem__(self, item, value):
        if isinstance(item, tuple):
            i, j = item
            if isinstance(i, int) and isinstance(j, int):
                self.matrix[i][j] = value
                return
            if isinstance(i, int):
                rows = [i]
            elif isinstance(i, list):
                rows = i
            else:
                rows = range(self.rows)[i]
            if isinstance(j, int):
                cols = [j]
            elif isinstance(j, list):
                cols = j
            else:
                cols = range(self.cols)[j]
            for i, ii in zip(cols, range(len(cols))):
                for j, jj in zip(rows, range(len(rows))):
                    self.matrix[j][i] = value[jj, ii]
        elif isinstance(item, int):
            i, j = divmod(item, self.cols)
            self.matrix[i][j] = value
        else:
            for k in range(self.cols * self.rows)[item]:
                i, j = divmod(k, self.cols)
                self.matrix[i][j] = value[k]

    def __delitem__(self, item):
        if isinstance(item, tuple):
            i, j = item
            if isinstance(i, int):
                rows = [i]
            elif isinstance(i, list):
                rows = set(i)
            else:
                rows = range(self.rows)[i]
            if isinstance(j, int):
                cols = [j]
            elif isinstance(j, list):
                cols = set(j)
            else:
                cols = range(self.cols)[j]
            if len(cols) == self.cols:
                self.delete_rows(rows)
                return
            if len(rows) == self.rows:
                self.delete_columns(cols)
                return
        raise ValueError("Can only delete entire rows or entire columns!")

    def delete_rows(self, rows: int|list) -> None:
        "Deletes a row or a list of rows."
        if isinstance(rows, int):
            rows = [ rows ]
        rows = list(map(lambda x: x % self.rows, rows))
        rows = set(rows)
        if len(rows) >= self.rows:
            raise ValueError("Cannot delete all rows.")
        for i in reversed(sorted(rows)):
            del self.matrix[i]
        self.rows -= len(rows)

    def delete_columns(self, cols: int|list) -> None:
        "Deletes a column or a list of columns."
        if isinstance(cols, int):
            cols = [ cols ]
        cols = list(map(lambda x: x % self.cols, cols))
        cols = set(cols)
        if len(cols) >= self.cols:
            raise ValueError("Cannot delete all columns.")
        for i in range(self.rows):
            for j in reversed(sorted(cols)):
                del self.matrix[i][j]
        self.cols -= len(cols)

    def append_row(self, row: list|tuple, ring = None) -> None:
        "Append a row."
        if not isinstance(row, list|tuple) or len(row) != self.cols:
            raise ValueError("Length does not match the number of columns.")
        if ring:
            row =list(map(ring, row))
        self.matrix.append(row)
        self.rows += 1

    def append_column(self, col: list|tuple, ring = None) -> None:
        "Append a column."
        if not isinstance(col, list|tuple) or len(col) != self.rows:
            raise ValueError("Length does not match the number of rows.")
        if ring:
            col =list(map(ring, col))
        for i in range(self.rows):
            self.matrix[i].append(col[i])
        self.cols += 1

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.rows != other.rows or self.cols != other.cols:
            return False
        return all(self[i] == other[i] for i in range(self.rows * self.cols))

    def __bool__(self):
        return any(bool(self[i]) for i in range(self.rows * self.cols))

    def map(self, func):
        "Apply a function to all elements in place."
        for row in self.matrix:
            row[:] = map(func, row)

    def applyfunc(self, func):
        "Apply a function to all elements."
        tmp = self[:, :]
        tmp.map(func)
        return tmp

    def _guess_zero(self):
        zero = 0 * self.matrix[0][0]
        one = zero**0
        return zero, one

    def norm2(self) -> float:
        "Squared Frobenius/Euclidean norm."
        return sum(sum(x*x for x in row) for row in self.matrix)

    def norm(self, p: int = 2) -> float:
        "p-norm of a matrix regarded as a vector."
        if p == 2:
            return sqrt(self.norm2())
        if p == 1:
            return sum(sum(abs(x) for x in row) for row in self.matrix)
        if p == inf:
            return max(max(abs(x) for x in row) for row in self.matrix)
        tmp = sum(sum(abs(x)**p for x in row) for row in self.matrix)
        return tmp**(1/p)

    def dot(self, other) -> int:
        "Dot product of two vectors."
        if self.rows == 1 and other.rows == 1 and self.cols == other.cols:
            return sum(x * y for x, y in zip(self.matrix[0], other.matrix[0]))
        if self.cols == 1 and other.cols == 1 and self.rows == other.rows:
            return sum(x[0] * y[0] for x, y in zip(self.matrix, other.matrix))
        return NotImplemented

    def transpose(self) -> "Matrix":
        "Transpose of a matrix."
        return Matrix([list(i) for i in zip(*self.matrix)])

    def multiply(self, other) -> "Matrix":
        "Matrix multiplication."
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.cols != other.rows:
            raise NotImplementedError("Matrix dimensions do not match!")
        result = self.zeros(self.rows, other.cols)
        for i in range(self.rows):
            for j in range(other.cols):
                for k in range(other.rows):
                    result.matrix[i][j] += self.matrix[i][k] * other.matrix[k][j]
        if self.rows == 1 and other.cols == 1:
            return result.matrix[0][0]
        return result

    def __add__(self, other) -> "Matrix":
        if isinstance(other, Matrix):
            if other.cols != self.cols or other.rows != self.rows:
                raise NotImplementedError("Matrix dimensions do not match!")
            return self.__class__([[x1 + y1 for x1, y1 in zip(x, y)] for x, y in zip(self.matrix, other.matrix)])
        return NotImplemented

    def __sub__(self, other) -> "Matrix":
        if isinstance(other, Matrix):
            if other.cols != self.cols or other.rows != self.rows:
                raise NotImplementedError("Matrix dimensions do not match!")
            return self.__class__([[x1 - y1 for x1, y1 in zip(x, y)] for x, y in zip(self.matrix, other.matrix)])
        return NotImplemented

    def __neg__(self) -> "Matrix":
        return -1 * self

    def __pos__(self) -> "Matrix":
        return self

    def __mul__(self, other) -> "Matrix":
        if isinstance(other, Matrix):
            return self.multiply(other)
        if isinstance(other, Number) or type(other) is type(self.matrix[0][0]):
            return self.__class__([[item * other for item in row] for row in self.matrix])
        return NotImplemented

    def __rmul__(self, other) -> "Matrix":
        if isinstance(other, Number) or type(other) is type(self.matrix[0][0]):
            return self.__class__([[item * other for item in row] for row in self.matrix])
        return NotImplemented

    def rref(self) -> "Matrix":
        "Compute the reduced echelon form of a matrix M."
        one = self._guess_zero()[1]
        n, m = self.cols, self.rows
        R = self[:, :]
        i = 0
        for j in range(n):
            if not R[i, j]:  # search for a nonzero entry in the present column
                for ii in range(i+1, m):
                    if R[ii, j]:
                        R[i, :], R[ii, :] = R[ii, :], R[i, :]  # swap rows
                        break
                else:
                    continue  # all entries are zero
            if R[i, j] != one:
                R[i, :] = R[i, j]**-1 * R[i, :]  # make the pivot one
            for ii in range(m):  # remove the column entries above/below the pivot
                if i == ii:
                    continue
                tmp = R[ii, j]
                R[ii, ::] -= tmp * R[i, :]
            i += 1
            if i == m:
                break
        return R

    def det(self) -> int:
        "Compute the determinant of a matrix M."
        zero, one = self._guess_zero()
        if self.rows != self.cols:
            raise ValueError("Matrix must be square!")
        n, m = self.cols, self.rows
        R = self[:, :]
        D = one
        i = 0
        for j in range(n):
            if not R[i, j]:  # search for a nonzero entry in the present column
                for ii in range(i+1, m):
                    if R[ii, j]:
                        D *= -one
                        R[i, :], R[ii, :] = R[ii, :], R[i, :]  # swap rows
                        break
                else:
                    return zero  # all entries are zero
            if R[i, j] != one:
                D *= R[i, j]
                R[i, :] = R[i, j]**-1 * R[i, :]  # make the pivot one
            for ii in range(i+1, n):  # remove the column entries below the pivot
                if i == ii:
                    continue
                tmp = R[ii, j]
                R[ii, ::] -= tmp * R[i, :]
            i += 1
        return D

    def rank(self) -> int:
        "Compute the rank of a matrix M."
        MM = self.rref()
        for i in range(self.rows-1,-1,-1):
            if MM[i,:]:
                return i+1
        return 0

    def inv(self) -> "Matrix":
        "Compute the inverse of a square matrix M."
        if self.rows != self.cols:
            raise ValueError("Matrix must be square!")
        zero, one = self._guess_zero()
        n = self.cols
        MM = self.__class__([[zero for _ in range(2*n)] for _ in range(n)])
        for i in range(n):
            MM[i, n+i] = one
        MM[:, 0:n] = self
        MM = MM.rref()
        if not prod(MM[i, i] for i in range(n)):
            raise ValueError("Matrix is not invertible!")
        return MM[:, n:]

    def solve(self, b: "Matrix", ring = None) -> "Matrix":
        "Solve the linear system with given inhomogenous vector."
        if isinstance(b, list|tuple):
            b = Matrix(b, ring = ring)
        if self.rows != b.rows or b.cols != 1:
            raise ValueError("Matrix dimensions do not match.")
        A = self.zeros(self.rows, self.cols + 1) # extended coefficient matrix
        A[:, 0:self.cols] = self
        A[:, self.cols] = b
        A = A.rref()
        solution = self.zeros(self.cols, 1)
        for i in range(A.rows-1, -1, -1):
            if not any(A.matrix[i][:-1]):
                if A.matrix[i][-1]:
                    return None  # Not solvable
            else:
                for j in range(A.cols - 1):
                    if A.matrix[i][j]:
                        break # leading nonzero coefficient
                solution[j]= A.matrix[i][-1]
        return solution

    def is_unimodular(self) -> bool:
        "Test if the matrix is unimodular."
        if self.rows != self.cols:
            return False

        def is_integer(i):
            if isinstance(i, int) or (isinstance(i, Fraction) and i.denominator == 1):
                return True
            return False
        return all(is_integer(i) for i in self) and self.det()**2 == 1

    def zeros(self, m: int = None, n: int = None):
        "Returns a zero matrix of the same dimension."
        if not m and not n:
            n, m = self.cols, self.rows
        elif not n:
            n = m
        if n < 1 or m < 1:
            raise ValueError(f"Matrix dimensions {m}x{n} must be positive!")
        zero = self._guess_zero()[0]
        return self.__class__([[zero for j in range(n)] for i in range(m)])

    def eye(self, m: int = None, n: int = None):
        "Returns an identity matrix of the same dimension."
        def delta(i, j):
            if i == j:
                return one
            return zero
        if not m and not n:
            n, m = self.cols, self.rows
        elif not n:
            n = m
        if n < 1 or m < 1:
            raise ValueError(f"Matrix dimensions {m}x{n} must be positive!")
        zero, one = self._guess_zero()
        return self.__class__([[delta(i, j) for j in range(n)] for i in range(m)])


def zeros(m: int, n: int = None, zero=0, ring=None) -> "Matrix":
    "Returns a zero matrix of the given dimension."
    if not n:
        n = m
    if n < 1 or m < 1:
        raise ValueError(f"Matrix dimensions {m}x{n} must be positive!")
    return Matrix([[zero for j in range(n)] for i in range(m)], ring=ring)


def eye(m: int, n: int = None, zero=0, one=1, ring=None) -> "Matrix":
    "Returns an identity matrix of the given dimension."
    def delta(i, j):
        if i == j:
            return one
        return zero
    if not n:
        n = m
    if n < 1 or m < 1:
        raise ValueError(f"Matrix dimensions {m}x{n} must be positive!")
    return Matrix([[delta(i, j) for j in range(n)] for i in range(m)], ring=ring)
