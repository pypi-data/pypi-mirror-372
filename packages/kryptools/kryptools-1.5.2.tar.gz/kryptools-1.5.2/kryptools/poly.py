"""
Polynomials
"""

from math import prod
from numbers import Number
from random import randint

class Poly:
    """
    Represents a polynomial as a list of coefficients.

    Example:

    To define a polynomial as a list of coefficients use
    >>> Poly([1, 2, 3])
    3 x^2 + 2 x + 1
    """

    print_reversed = True  # print the terms in reversed order
    print_x = "x"  # variable for printing
    print_pow = "^"  # you can change this to "**" if you want it python style

    def __init__(self, coeff: list, ring=None, modulus: list = None):
        self.coeff = list(coeff)
        for i in range(len(self.coeff) - 1, 0, -1):  # strip leading zeros
            if self.coeff[i]:
                break
            self.coeff.pop(i)
        self.modulus = modulus
        if ring:
            self.map(ring)
        if modulus:
            self.mod(modulus)

    def __call__(self, x):
        result = 0 * self.coeff[0]
        if not type(x) == type(result):  # pylint: disable=C0123
            raise ValueError(
                "Evaluation point must be an element of the ring.")
        # Horner's method
        for c in reversed(self.coeff):
            result = result * x + c
        return result

    def __getitem__(self, item):
        if item >= len(self.coeff):
            return self.coeff[0] * 0
        return self.coeff[item]

    def __setitem__(self, item, value):
        if item >= len(self.coeff):
            zero = self.coeff[0] * 0
            self.coeff += [zero] * (item - len(self.coeff) + 1)
        self.coeff[item] = value

    def __iter__(self):
        yield from self.coeff

    def __len__(self):
        return len(self.coeff)

    def __hash__(self):
        return hash(tuple(self.coeff))

    def __repr__(self, latex=False):
        def prx(i: int) -> str:
            if i == 0:
                return ""
            if i == 1:
                return self.__class__.print_x
            if latex:
                return self.__class__.print_x + "^{" + str(i) + "}"
            return self.__class__.print_x + self.__class__.print_pow + str(i)

        if not self:
            return str(self.coeff[0])
        one = self.coeff[0]**0
        plus = ""
        tmp = ""
        coef_range = range(len(self.coeff))
        if self.__class__.print_reversed:
            coef_range = reversed(coef_range)
        for i in coef_range:
            s = self.coeff[i]
            if not s:
                continue
            if not s - one and i != 0:
                tmp += plus + prx(i)
                plus = " + "
                continue
            try:
                if not s + one and i != 0:
                    if plus:
                        plus = " "
                    tmp += plus + "- " + prx(i)
                    plus = " + "
                    continue
            except:  # pylint: disable=W0702
                pass
            try:
                if plus and s < 0:
                    tmp += " - " + str(-s)
                    if i != 0:
                        tmp += " " + prx(i)
                    continue
            except:  # pylint: disable=W0702
                pass
            tmp += plus + str(s)
            if i != 0:
                tmp += " " + prx(i)
            plus = " + "
        return tmp.strip()

    def _repr_mimebundle_(self, **kwargs):  # pylint: disable=W0613
        return {
            "text/plain": repr(self),
            "text/latex": "$" + self.__repr__(latex=True) + "$"  # pylint: disable=C2801
        }

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return not bool(self - other)

    def __bool__(self):
        return bool(self.degree()) or bool(self.coeff[0])

    def degree(self) -> int:
        "Return the degree."
        return len(self.coeff) - 1

    def map(self, func):
        "Apply a given function to all coefficients in place."
        self.coeff = list(map(func, self.coeff))

    def applyfunc(self, func) -> "Poly":
        "Apply a function to all coefficients."
        return self.__class__(list(map(func, self.coeff)), modulus=self.modulus)

    def _check_type(self, other):
        return isinstance(other, int) or (isinstance(other, Number) and isinstance(self.coeff[0], Number)) or type(other) == type(self.coeff[0])  # pylint: disable=C0123

    def _guess_ring(self):
        zero = 0 * self.coeff[0]
        one = zero**0
        if hasattr(zero, "ring"):
            ring = zero.ring  # Zmod
        elif hasattr(zero, "field"):
            ring = zero.field  # GF2
        elif hasattr(type(zero), "order"):
            ring = type(zero)  # galois
        else:
            ring = None
        return zero, one, ring

    def _guess_field(self):
        zero, one, field = self._guess_ring()
        if not field:
            raise ValueError(
                "The polynomial does not seem to be over a known finite field.")
        if hasattr(field, 'n'):  # Zmod
            p = field.n
            q = field.n
            if not field.is_field():
                raise ValueError(
                    "The polynomial does not seem to be over a finite field.")
        else:  # G2 or galois
            p = field.characteristic
            q = field.order
        return field, zero, one, q, p

    def __add__(self, other: "Poly") -> "Poly":
        if not isinstance(other, self.__class__):
            if self._check_type(other):
                tmp = self.coeff[:]
                tmp[0] += other
                return self.__class__(tmp, modulus=self.modulus)
            return NotImplemented
        modulus = self.modulus
        if not modulus and other.modulus:
            modulus = other.modulus
        ls, lo = len(self.coeff), len(other.coeff)
        if ls < lo:
            return self.__class__([s + o for s, o in zip(self.coeff, other.coeff)] + other.coeff[ls:], modulus=modulus)
        return self.__class__([s + o for s, o in zip(self.coeff, other.coeff)] + self.coeff[lo:], modulus=modulus)

    def __radd__(self, other: "Poly") -> "Poly":
        return self + other

    def __neg__(self) -> "Poly":
        return Poly([-s for s in self.coeff], modulus=self.modulus)

    def __pos__(self) -> "Poly":
        return self

    def __sub__(self, other: "Poly") -> "Poly":
        return self + (- other)

    def __rsub__(self, other: "Poly") -> "Poly":
        return (- self) + other

    def __mul__(self, other: "Poly") -> "Poly":
        if not isinstance(other, self.__class__):
            if self._check_type(other):
                return Poly([other * s for s in self.coeff], modulus=self.modulus)
            return NotImplemented
        zero = 0 * self.coeff[0]
        ls, lo = len(self.coeff), len(other.coeff)
        coeff = [sum((self.coeff[j] * other.coeff[k - j] for j in range(max(0, k - lo + 1), min(ls, k + 1))), start=zero)
                     for k in range(ls + lo - 1)]
        modulus = self.modulus
        if not modulus and other.modulus:
            modulus = other.modulus
        return self.__class__(coeff, modulus=modulus)

    def __rmul__(self, other) -> "Poly":
        return self * other

    def __truediv__(self, other) -> "Poly":
        if self._check_type(other):
            return self.__class__([s / other for s in self.coeff], modulus=self.modulus)
        if isinstance(other, self.__class__):
            if not other.modulus:
                raise NotImplementedError(
                    "Cannot invert polynomials without modulus.")
            return self * other.inv()
        return NotImplemented

    def __rtruediv__(self, other) -> "Poly":
        if not self.modulus:
            raise NotImplementedError(
                "Cannot invert polynomials without modulus.")
        return other * self.inv()

    def __pow__(self, j: int) -> "Poly":
        if not isinstance(j, int):
            return NotImplemented
        one = self.coeff[0]**0
        res = self.__class__([one], modulus=self.modulus)
        if j < 0:
            if not self.modulus:
                raise NotImplementedError(
                    "Cannot divide polynomials without modulus.")
            tmp = self.inv()
            j *= -1
        else:
            tmp = self
        while j > 0:
            # If j is odd, multiply
            if j & 1:
                res *= tmp
            # Now square
            j = j >> 1  # j= j//2
            tmp *= tmp
        return res

    def bits(self) -> list[int]:
        "List of bits of all coefficients."
        ring = self.coeff[0].__class__
        if not (hasattr(ring, 'bits') and callable(ring.bits)):
            raise NotImplementedError(
                "Coefficients cannot be converted to bits.")
        out = []
        for c in self.coeff:
            out += c.bits()
        return out

    def max(self) -> int:
        "Maximum of the absolute value of all coefficients."
        return max(abs(c) for c in self.coeff)

    def sum(self) -> int:
        "Sum of the absolute value of all coefficients."
        return sum(abs(c) for c in self.coeff)

    def __floordiv__(self, other: "Poly") -> "Poly":
        return self.divmod(other)[0]

    def __mod__(self, other: "Poly") -> "Poly":
        return self.divmod(other)[1]

    def divmod(self, other: "Poly") -> ("Poly", "Poly"):
        "Polynom division with remainder."
        zero, one, ring = self._guess_ring()
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot divide {self} and {other}.")
        if not other:
            raise ValueError(f"{other} must be nonzero.")
        sd, od = self.degree(), other.degree()
        if sd < od:
            return self.__class__([zero]), self
        div = [zero] * (sd - od + 1)
        lco = other.coeff[-1]
        if bool(lco - one):
            tmp = one / lco
            oth = [c * tmp for c in other.coeff]
            rem = [c * tmp for c in self.coeff]
        else:
            oth = other.coeff  # "* 1" is here to make sure we get a copy
            rem = [c * one for c in self.coeff]
        for i in range(sd - od + 1):
            tmp = rem[sd - i] * one  # "* 1" is here to make sure we get a copy
            div[sd - od - i] = tmp
            for j in range(od + 1):
                rem[sd - i - j] -= tmp * oth[od - j]
        if bool(lco - one):
            rem = [c * lco for c in rem]
        return self.__class__(div, modulus=self.modulus), self.__class__(rem, modulus=self.modulus)

    def mod(self, other: "Poly") -> None:
        "Reduce with respect to a given polynomial."
        one, ring = self._guess_ring()[1:]
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot divide {self} and {other}.")
        if not other:
            raise NotImplementedError(f"{other} must be nonzero.")
        sd, od = self.degree(), other.degree()
        if sd < od:
            return self
        lco = other.coeff[-1]
        if bool(lco - one):
            tmp = one / lco
            oth = [c * tmp for c in other.coeff]
        else:
            oth = other.coeff
        for i in range(sd - od + 1):
            tmp = self.coeff[sd - i] * one  # "* 1" is here to make sure we get a copy
            for j in range(od + 1):
                self.coeff[sd - i - j] -= tmp * oth[od - j]
        for i in range(len(self.coeff) - 1, 0, -1):  # strip leading zeros
            if self.coeff[i]:
                break
            self.coeff.pop(i)

    def inv(self, other: "Poly" = None) -> "Poly":
        "Inverse modulo a given polynomial."
        if not other:
            other = self.modulus
        zero, one, ring = self._guess_ring()
        if isinstance(other, self.__class__):
            other = other.coeff
        elif not isinstance(other, list):
            raise NotImplementedError(
                f"{other} must be a list of coefficients or a polynomial.")
        other = Poly(other, ring=ring)
        if not other:
            raise NotImplementedError(f"{other} must be nonzero.")
        r0, r1 = other, self
        y0, y1 = self.__class__([zero]), self.__class__([one])
        while r1:
            q, r = r0.divmod(r1)
            r0, r1 = r1, r
            y0, y1 = y1, y0 - q * y1
        if r0.degree() != 0:
            raise ValueError(f"{self} is not invertible mod {other}.")
        y0.modulus = self.modulus
        return y0 / r0.coeff[0]

    def gcd(self, other: "Poly") -> "Poly":
        "Greates common divisor with a given polynomial."
        if not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot compute gcd: {other} must be a polynomial.")
        if not self:
            if not other:
                return Poly([self.coeff[0]])
            tmp = other / other.coeff[-1]
            tmp.modulus = None
            return tmp
        r0, r1 = other, self
        while r1:
            r0, r1 = r1, r0.divmod(r1)[1]
        r0.modulus = None
        return r0 / r0.coeff[-1]

    def egcd(self, other: "Poly") -> ("Poly", "Poly", "Poly"):
        """Perform the extended Euclidean agorithm for polynomials. Returns gcd, x, y such that other * x + self * y = gcd."""
        zero, one, _ = self._guess_ring()
        if not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot perform egcd: {other} must be a polynomial.")
        if not self:
            if not other:
                return Poly([zero]), Poly([zero]), Poly([zero])
            return other / other.coeff[-1], Poly([zero]), one / other.coeff[-1]
        r0, r1 = other, self
        x0, x1 = self.__class__([one]), self.__class__([zero])
        y0, y1 = self.__class__([zero]), self.__class__([one])
        while r1:
            q, r = r0.divmod(r1)
            r0, r1 = r1, r
            x0, x1 = x1, x0 - x1 * q
            y0, y1 = y1, y0 - y1 * q
        lcr0 = r0.coeff[-1]
        return r0 / lcr0, x0 / lcr0, y0 / lcr0

    def derivative(self) -> "Poly":
        "Returns the formal derivative."
        l = len(self.coeff)
        if l == 1:
            tmp = 0 * self.coeff[0]
        else:
            tmp = [j * self.coeff[j] for j in range(1, l)]
        return self.__class__(tmp, modulus=self.modulus)

    def square_free_factors(self) -> dict:
        "Determine the square free factors of a polynomial over a Galois field."
        _, zero, _, q, p = self._guess_field()
        pr = q // p  # x^pr will be the p'th root of x
        if self.degree() < 1:
            return {}
        if self.degree() == 1:
            return {self / self.coeff[-1]: 1}
        factors = {}
        w = self / self.coeff[-1]
        c = w.gcd(w.derivative())
        w = w // c

        # first we find all factors which are not a power of p
        i = 1
        while w.degree() > 0:
            y = w.gcd(c)
            fac = w // y
            if fac.degree() > 0:
                factors[fac] = i
            w = y
            c //= y
            i += 1
        # c is now a power of p
        if c.degree() > 0:
            # compute the p'th root of c
            d = c.degree() // p
            root = [zero] * (d + 1)
            while d >= 0:
                root[d] = c.coeff[d * p]**pr
                d -= 1
            # assert Poly(root)**p == c, root
            for fac, mult in Poly(root).square_free_factors().items():
                factors[fac] = p * mult
        return factors

    def is_square_free(self) -> bool:
        "Test if the polynomial over a Galois field is square free."
        multiplicities = self.square_free_factors().values()
        return len(multiplicities) == 1 and multiplicities[0] == 1

    def distinct_degree_factors(self, test: bool = False) -> bool | dict:
        "Factors the polynomial over a Galois field into distinct products of irredicible factors of the same degree."
        _, zero, one, q, _ = self._guess_field()
        if self.degree() < 1:
            raise ValueError("The polynomial must be non-constant.")
        factors = {}
        w = self
        x = Poly([zero, one], modulus=self.coeff)  # x
        b = x
        k = 1
        while k <= w.degree()//2:
            b **= q  # we compute x^{q^k} mod a recursively
            g = w.gcd(b - x)  # gcd with x^{q^k} - x
            if g.degree():
                if test:
                    return False
                factors[k] = g
                w = w // factors[k]
            k += 1
        if test:
            return True
        if w.degree() > 0:
            factors[w.degree()] = w
        return factors

    def rabin_test(self) -> bool:
        "Determine if a polynomial is irreducible over a Galois field using a Rabin test."
        return self.distinct_degree_factors(test=True)

    def is_irreducible(self) -> bool:
        "Test if the polynomial over a Galois field is irreducibel."
        if self.degree() == 0:
            return False
        return self.distinct_degree_factors(test=True)

    def equal_degree_factors(self, k: int) -> list:
        "Factors a square free product of irreducibel polynomials of degree `k` over a Galois field."
        field, _, one, q, p = self._guess_field()
        if hasattr(field, "degree"):
            degree = field.degree
        else:
            degree = 1
        d = self.degree()
        if not isinstance(k, int) or k < 1:
            raise ValueError(f"The degree {k} must be a positive integer.")
        if d < k or d % k:
            raise ValueError(
                f"The polynomial is no product of irreducibel polynomials of degree {k}.")
        r = d // k
        qk = (q**k - 1) // 2

        factors = [self]
        while len(factors) < r:
            g = Poly([randint(0, q-1)
                     for _ in range(d+1)], ring=field, modulus=self)
            if p == 2:  # Gathen-Shoup
                h = g
                for _ in range(1, k):
                    g += h**q
                if degree > 1:
                    h = g
                    for _ in range(1, degree):
                        g += g**2
            else:  # Cantor–Zassenhaus
                g = g**qk - one
            factors2 = []  # list for the next round (to avoid the the new factors are tested a second time with the same g)
            for fac in factors:
                if fac.degree() == k:  # this one is already irreducible
                    factors2.append(fac)
                    continue
                gg = fac.gcd(g)
                if gg.degree() == 0 or gg.degree() == fac.degree():  # trivial factor
                    factors2.append(fac)
                    continue
                gg.modulus = None
                factors2.append(gg)
                factors2.append(fac // gg)
            factors = factors2
        return factors

    def factor(self) -> dict:
        "Factors a polynomials over a Galois field."
        if self.degree() < 1:
            return {self: 1}
        c = Poly([self.coeff[-1]])
        one = c**0
        if c != one:
            factors = {c: 1}
        else:
            factors = {}
        for fac1, m in self.square_free_factors().items():
            for k, fac2 in fac1.distinct_degree_factors().items():
                if k == fac2.degree():  # irreducible
                    factors[fac2] = m
                else:
                    for fac3 in fac2.equal_degree_factors(k):
                        factors[fac3] = m
        return dict(sorted(factors.items(), key=lambda item: item[0].degree()))


def lagrange_interpolation(x_coordinates: list, y_coordinates: list) -> "Poly":
    "Compute the Lagrange interpolation polynomial from a given list of x and y values."
    l = len(x_coordinates)
    if l == 0 or l != len(y_coordinates):
        raise ValueError(
            'List of x and y values must be nonempty of equal length.')
    if l != len(set(x_coordinates)):
        raise ValueError('List of x values must not contain duplicate values.')
    # guess zero and one
    zero = 0 * x_coordinates[0]
    one = zero**0

    poly = Poly([zero])
    L_all = prod([Poly([-x, one]) for x in x_coordinates], start=one)

    for x, y in zip(x_coordinates, y_coordinates):
        L = L_all // Poly([-x, one])
        poly += (y /
                 prod([x - xx for xx in x_coordinates if xx != x], start=one)) * L
    return poly
