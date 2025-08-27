"""
Ring of intergers modulo `n`.
"""

from math import gcd
from random import randint
from .factor import factorint
from .primes import is_prime
from .nt import sqrt_mod, crt
from .intfuncs import prime_power


class Zmod:
    """
    Ring of intergers modulo `n`.

    Example:

    To define a finite Galois field modulo the prime 5 use
    >>> Z_5=Zmod(5)

    To declare 3 as an element of our Galois field use
    >>> Z_5(3)
    3

    The usual arithmetic operations are supported.
    >>> Z_5(2) + Z_5(3)
    0
    """

    def __init__(self, n: int, short: bool = True):
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"{n} is not a positive integer.")
        self.n = n
        self.isfield = None
        self.n_factors = {} # factoring of n
        self.short = short
        self.group_order = 0 # order of the multiplicative group
        self.factors = {}  # factoring of the multiplicative group order

    def __repr__(self):
        return f"Z_{self.n}"

    def __call__(self, x: int | list | tuple | range | map):
        if isinstance(x, list|tuple|range|map):
            return [ZmodPoint(xx, self) for xx in x]
        return ZmodPoint(x, self)

    def __iter__(self):
        for x in range(self.n):
            yield ZmodPoint(x, self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.n == other.n
        return False

    def __contains__(self, other: "ZmodPoint") -> bool:
        return isinstance(other, ZmodPoint) and self.n == other.ring.n

    def random(self, num: int = 0) -> "ZmodPoint":
        "Return a single random point or a list of random points."
        if num:
            return([self(randint(0,self.n-1)) for _ in range(num)])
        return self(randint(0,self.n-1))

    def order(self) -> int:
        "Compute the order of the group Z_n^*."
        if self.group_order:
            return self.group_order
        # We compute euler_phi(n) and its factorization in one pass
        if not self.n_factors:
            self.n_factors = factorint(self.n)
        for p, k in self.n_factors.items():  # factorization of n
            # factor p-1 and add the factors
            for pm, km in factorint(p - 1).items():
                if pm in self.factors:
                    self.factors[pm] += km
                else:
                    self.factors[pm] = km
            # if the multiplicity of of p is >1, then we need to add p**(k-1)
            if k > 1:
                if p in self.factors:
                    self.factors[p] += k - 1
                else:
                    self.factors[p] = k - 1
        self.group_order = 1
        for p, k in self.factors.items():
            self.group_order *= p**k
        return self.group_order

    def is_cyclic(self) -> bool:
        "Test if the group Z_n^* is cyclic."
        n = self.n
        if n < 8:
            return True
        if not n % 2:
            n //= 2
        if not n % 2:
            return False
        if prime_power(n):
            return True
        return False

    def is_field(self) -> bool:
        "Test if Z_n is a field."
        if self.isfield is None:
            if self.n_factors:
                if len(self.n_factors) == 1:
                    self.isfield = True
                else:
                    self.isfield = False
            elif is_prime(self.n):
                self.isfield = True
                self.n_factors = { self.n: 1}
            else:
                self.isfield = False
        return self.isfield

    def generator(self) -> int | None:
        "Return a generator of the group Z_n^*."
        if not self.is_cyclic():
            return None
        if self.n == 1:
            return self(0)
        if self.n == 2:
            return self(1)
        for a in range(2, self.n):
            if gcd(a, self.n) > 1:
                continue
            a = self(a)
            if a.is_generator():
                return a

    def generators(self) -> list | None:
        "Return a generator for all generators of the group Z_n^*."
        a = self.generator()
        if a is not None:
            yield a
            self.order()
            for j in range(2, self.group_order):
                if gcd(j, self.group_order) == 1:
                    yield a**j

    def star(self) -> list:
        "Return a generator for all elements of the group Z_n^*."
        if self.n == 1:
            yield self(0)
        else:
            yield self(1)
            for a in range(2, self.n):
                if gcd(a, self.n) == 1:
                    yield self(a)


class ZmodPoint:
    "Represents a point in the ring Zmod."

    def __init__(self, x: int, ring: "Zmod"):
        self.x = int(x) % ring.n
        self.ring = ring

    def __repr__(self):
        if self.ring.short:
            return str(self.x)
        return f"{self.x} (mod {self.ring.n})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__) or self.ring != other.ring:
            return False
        return self.x == other.x

    def __bool__(self):
        return self.x != 0

    def __int__(self):
        return self.x

    def __hash__(self):
        return hash(self.x)

    def __add__(self, other: "ZmodPoint") -> "ZmodPoint":
        if isinstance(other, self.__class__):
            if self.ring != other.ring:
                raise NotImplementedError("Cannot add elements from different rings.")
            return self.__class__(self.x + other.x, self.ring)
        if isinstance(other, int):
            return self.__class__(self.x + other, self.ring)
        return NotImplemented

    def __radd__(self, scalar: int) -> "ZmodPoint":
        return self + scalar

    def __neg__(self) -> "ZmodPoint":
        return self.__class__(-self.x, self.ring)

    def __pos__(self) -> "ZmodPoint":
        return self

    def __sub__(self, other: "ZmodPoint") -> "ZmodPoint":
        if isinstance(other, self.__class__):
            if self.ring != other.ring:
                raise NotImplementedError("Cannot subtract elements from different rings.")
            return self.__class__(self.x - other.x, self.ring)
        if isinstance(other, int):
            return self.__class__(self.x - other, self.ring)
        return NotImplemented

    def __rsub__(self, scalar: int) -> "ZmodPoint":
        return (- self) + scalar

    def __mul__(self, other: "ZmodPoint") -> "ZmodPoint":
        if isinstance(other, self.__class__):
            if self.ring != other.ring:
                raise NotImplementedError("Cannot multiply elements from different rings.")
            return self.__class__(self.x * other.x, self.ring)
        if isinstance(other, int):
            return self.__class__(self.x * other, self.ring)
        return NotImplemented

    def __rmul__(self, scalar: int) -> "ZmodPoint":
        return self * scalar

    def __truediv__(self, other: "ZmodPoint") -> "ZmodPoint":
        if isinstance(other, self.__class__):
            if self.ring != other.ring:
                raise NotImplementedError("Cannot divide elements from different rings.")
            return self.__class__(self.x * pow(other.x, -1, self.ring.n), self.ring)
        return NotImplemented

    def __rtruediv__(self, scalar: int) -> "ZmodPoint":
        if isinstance(scalar, int):
            return self.__class__(scalar * pow(self.x, -1, self.ring.n), self.ring)
        return NotImplemented

    def __pow__(self, scalar: int) -> "ZmodPoint":
        if isinstance(scalar, int):
            return self.__class__(pow(self.x, scalar, self.ring.n), self.ring)
        return NotImplemented

    def __abs__(self) -> int:
        return abs(self.sharp())

    def bits(self) -> list:
        "Convert to a list of bits."
        return [int(d) for d in str(format(self.x, "0" + str(int.bit_length(self.ring.n - 1)) + "b"))]

    def sharp(self):
        "Returns a symmetric (w.r.t. 0) representative."
        tmp = (self.ring.n - 1) // 2
        return (self.x + tmp) % self.ring.n - tmp

    def order(self) -> int:
        "Compute the order of the point in the group Z_n^*."
        if self.ring.n == 1:
            return 1
        if self.x == 0 or gcd(self.x, self.ring.n) != 1:
            raise ValueError(f"{self.x} and {self.ring.n} are not coprime!")
        order = self.ring.order()  # use euler_phi(n) as our current guess
        for p, k in self.ring.factors.items():
            for _ in range(k):
                order_try = order // p
                if pow(self.x, order_try, self.ring.n) == 1:
                    order = order_try
                else:
                    break
        return order

    def sqrt(self) -> "ZmodPoint":
        "Compute a square root of the point."
        if not self.ring.n_factors:
            self.ring.n_factors = factorint(self.ring.n)
        a = int(self)
        if a in (0, 1):
            return self.ring(a)
        roots = []
        powers = []
        for p, k in self.ring.n_factors.items():
            q = p**(k-1)
            pk = q * p
            ak = a % pk
            powers.append(pk)
            if ak in (0, 1):
                roots.append(ak)
                continue
            # write ak as p^j * invertible
            j = 0
            while ak % p == 0:
                j += 1
                ak //= p
            if j % 2:
                raise ValueError("No quadratic residue!")
            if ak == 1:
                roots.append(p**(j//2))
                continue
            if p == 2:
                if ak % 8 != 1:
                    raise ValueError("No quadratic residue!")
                m = 4 # start at 2^2
                x = ak % m # this is the root mod m
                for _ in range(3, k + 1):
                    # test all 4 poosible roots
                    if (x**2 - ak) % (m * 2):
                        x = m - x
                        if (x**2 - ak) % (m*2):
                            x = (x * (m//2-1)) % m
                            if (x**2 - ak) % (m * 2):
                                x = m - x
                    m *= 2
            else:
                # odd prime: Cipolla's formula
                x = sqrt_mod(ak, p)
                if x is None:
                    raise ValueError("No quadratic residue!")
                if k > 1:
                    x = pow(x, q, pk) * pow(ak,((p-2)*q+1)//2, pk) % pk
            roots.append((p**(j//2) * x) % pk)
        return self.ring(crt(roots, powers))

    def is_generator(self):
        "Test if the point is a generator of the group Z_n^*."
        return self.ring.order() == self.order()
