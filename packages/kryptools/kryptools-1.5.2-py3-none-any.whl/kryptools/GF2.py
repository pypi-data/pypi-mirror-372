"""
Galois field GF(2^n).
"""

from math import gcd
from random import randint
from .poly import Poly
from .Zmod import Zmod
from .factor import factorint
from .conway_polynomials import conway_polynomials2


class GF2:
    """
    Create a Galois field GF(2^n).

    Elements of a Galois filed are specified by integers from 0 to 2**n-1, which are
    identified with polynomials whose coefficients are the binary digits of the integer.
    Multiplication is polynomial multiplication modulo a given irreducible polynomial.
    If the polynomial has the n'th bit set, the lowest bit corresponds to the constant coefficient
    (like in AES). Otherwise, the bit order is reversed (like for Ghash). The default modulus is
    choosen from a list of Conway polynomials.

    Example:

    To define the Galois field GF(2^8) use
    >>> gf=GF2(8)

    To declare 3 as an element of our Galois field use (elements are displayed as hex numbers)
    >>> gf(3)
    03

    The usual arithmetic operations are supported.
    >>> gf(2) * gf(123)
    f6

    """
    def __init__(self, n: int, modulus: int | None = None):
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"{n} is not a positive integer.")
        if not modulus:
            if n in conway_polynomials2:
                modulus = conway_polynomials2[n]
            else:
                raise ValueError("Unknown degree. Please specify a modulus.")
        self.modulus = modulus  # integer whose biniary digits are the coefficients of the irreducible modulus polynomial
        if modulus & 2**n == 2**n:
            self.bitreversed = False
        else:
            self.bitreversed = True
        self.degree = n  # n
        self.characteristic = 2
        self.order = 2**n  # 2**n
        self.print_hex: bool = True
        self.byteorder: str = "big"  # big|little
        self.mult_order = self.order - 1
        self.factors = {}  # factoring of the group order

    def __repr__(self):
        return f"GF(2^{self.degree})"

    def __call__(self, x: int | list | tuple | range | map):
        if isinstance(x, list|tuple|range|map):
            return [GF2nPoint(xx, self) for xx in x]
        return GF2nPoint(x, self)

    def __len__(self):
        return self.order

    def __iter__(self):
        for x in range(self.order):
            yield GF2nPoint(x, self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.order == other.order and self.modulus == other.modulus
        return False

    def __contains__(self, other: "GF2nPoint") -> bool:
        return isinstance(other, GF2nPoint) and self == other.field

    def _factors(self) -> dict:
        "Return the factroization order of the group order of GF(2^n)^*."
        if not self.factors:
            self.factors = factorint(self.mult_order)
        return self.factors

    def zero(self) -> bool:
        "Return zero."
        return self(0)

    def one(self) -> bool:
        "Return one."
        if self.bitreversed:
            return self(self.order - 1)
        return self(1)

    def random(self, num: int = 0) -> "GF2nPoint":
        "Return a single random point or a list of random points."
        if num:
            return([self(randint(0,self.order-1)) for _ in range(num)])
        return self(randint(0,self.order-1))

    def is_cyclic(self) -> bool:
        "GF(2^n)^* is cyclic."
        return True

    def is_field(self) -> bool:
        "GF(2^n) is a field."
        return True

    def generator(self) -> int | None:
        "Return a generator of the group GF(2^n)^*."
        if self.degree == 1:
            return self(1)
        for a in range(2, self.order):
            a = self(a)
            if a.is_generator():
                return a

    def generators(self) -> list | None:
        "Return a generator for all generators of the group GF(2^n)^*."
        a = self.generator()
        yield a
        for j in range(2, self.mult_order):
            if gcd(j, self.mult_order) == 1:
                yield a**j

    def star(self) -> list:
        "Return a generator for all elements of the group GF(2^n)n^*."
        for x in range(1, self.order):
            yield self(x)


class GF2nPoint:
    "Represents a point in the Galois field GF(2^n)."

    def __init__(self, x: int, field: "GF2"):
        if isinstance(x, bytes | bytearray):
            x = int.from_bytes(x, byteorder=field.byteorder)
        self.x = int(x) % field.order
        self.field = field

    def __repr__(self):
        if self.field.print_hex:
            return format(self.x, "0"+str(self.field.degree // 4)+"x")
        return self.x

    def __eq__(self, other):
        if not isinstance(other, self.__class__) or self.field != other.field:
            return False
        return self.x == other.x

    def __bool__(self):
        return bool(self.x)

    def __int__(self):
        return self.x

    def __bytes__(self):
        return self.x.to_bytes(self.field.degree // 8, byteorder=self.field.byteorder)

    def bits(self) -> list:
        "Convert to a list of bits."
        if self.field.bitreversed:
            coeff = [int(d) for d in str(
                format(self.x, "0" + str(self.field.degree) + "b"))]
        else:
            coeff = reversed([int(d) for d in str(
                format(self.x, "0" + str(self.field.degree) + "b"))])
        return list(coeff)

    def poly(self) -> "Poly":
        "Convert to a polynomial."
        Z_2 = Zmod(2)
        if self.field.bitreversed:
            coeff = [Z_2(int(d)) for d in str(
                format(self.x, "0" + str(self.field.degree) + "b"))]
            coeff_modulus = [Z_2(int(d)) for d in str(
                format((self.field.modulus << 1) + 1, "0" + str(self.field.degree) + "b"))]
        else:
            coeff = reversed([Z_2(int(d)) for d in str(
                format(self.x, "0" + str(self.field.degree) + "b"))])
            coeff_modulus = reversed([Z_2(int(d)) for d in str(
                format(self.field.modulus, "0" + str(self.field.degree) + "b"))])
        return Poly(list(coeff), modulus=list(coeff_modulus))

    def __hash__(self):
        return hash(self.x)

    def __add__(self, other: "GF2nPoint") -> "GF2nPoint":
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.field != other.field:
            raise NotImplementedError("Cannot add elements from different fields.")
        return self.field(self.x ^ other.x)

    def __neg__(self) -> "GF2nPoint":
        return self

    def __pos__(self) -> "GF2nPoint":
        return self

    def __sub__(self, other: "GF2nPoint") -> "GF2nPoint":
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.field != other.field:
            raise NotImplementedError("Cannot add elements from different fields.")
        return self.field(self.x ^ other.x)

    def __mul__(self, other: "GF2nPoint") -> "GF2nPoint":
        if isinstance(other, int):
            if other % 2:
                return self
            return self.field(0)
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.field != other.field:
            raise NotImplementedError("Cannot add elements from different fields.")
        z = 0
        y = other.x
        if self.field.bitreversed:
            for d in bin(self.x)[2:].zfill(self.field.degree):
                if int(d):
                    z ^= y
                if y % 2:
                    y >>= 1
                    y ^= self.field.modulus
                else:
                    y >>= 1
        else:
            bitmap1 = self.field.order
            bitmap2 = 1
            for _ in range(self.field.degree):
                if self.x & bitmap2:
                    z ^= y
                bitmap2 <<= 1
                y <<= 1
                if y & bitmap1:
                    y ^= self.field.modulus
        return self.field(z)

    def __rmul__(self, scalar: int) -> "GF2nPoint":
        if isinstance(scalar, int):
            if scalar % 2:
                return self
            return self.field(0)
        return NotImplemented

    def __truediv__(self, other: "GF2nPoint") -> "GF2nPoint":
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.field != other.field:
            raise NotImplementedError("Cannot add elements from different fields.")
        if not other.x:
            raise ValueError("Division by zero.")
        return self * other**(self.field.order - 2)

    def __pow__(self, j: int) -> "GF2nPoint":
        if not isinstance(j, int):
            return NotImplemented
        if not (self.x) and j < 0:
            raise ValueError("Division by zero.")
        if self.field.order == 2:
            return self
        if self.field.bitreversed:
            res = self.field(self.field.order >> 1)
        else:
            res = self.field(1)
        x = self.field(self.x)
        j %= self.field.order - 1
        while j > 0:
            # If j is odd, multiply with x
            if j & 1:
                res *= x
            # Now square
            j = j >> 1  # j= j/2
            x *= x
        return res

    def __lshift__(self, j: int) -> "GF2nPoint":
        "Cyclic rotation to the left."
        x = self.x << j
        x = (x % self.field.order) + (x // self.field.order)
        return self.field(x)

    def __rshift__(self, j: int) -> "GF2nPoint":
        "Cyclic rotation to the right."
        x = self.x >> j
        x += (self.field.order >> j) * (self.x % 2**j)
        return self.field(x)

    def sqrt(self) -> "GF2nPoint":
        "Compute the square root."
        if self.field.order == 2:
            return self
        return self**(self.field.order//2)

    def order(self) -> int:
        "Compute the order of the point in the group GF(2^n)^*."
        self.field._factors()  # pylint: disable=W0212
        order = self.field.mult_order  # our current guess
        one = self.field.one()
        for p, k in self.field.factors.items():
            for _ in range(k):
                order_try = order // p
                if self ** order_try == one:
                    order = order_try
                else:
                    break
        return order

    def is_generator(self):
        "Test if the point is a generator of the group GF(2^n)^*."
        return self.field.mult_order == self.order()

    def sbox(self, inv: bool = False) -> "GF2nPoint":
        "Apply the AES sbox."
        if self.field.degree == 8 and self.field.modulus == 0b100011011: # AES
            if inv:
                return aes_sbox_inv[self.x]
            return aes_sbox[self.x]
        if self.field.degree == 4 and self.field.modulus == 0b10011: # MiniAES
            if inv:
                return miniaes_sbox_inv[self.x]
            return miniaes_sbox[self.x]
        raise ValueError("sbox is only availaible for AES/MiniAES field.")

# sbox for AES
GF2_aes = GF2(8, 0b100011011)  # x^8 + x^4 + x^3 + x + 1 = AES

aes_sbox = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118,
 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192,
 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21,
 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9,
 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83,
 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208,
 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81,
 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205,
 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96,
 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224,
 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231,
 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186,
 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112,
 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225,
 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140,
 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]

# inverse sbox for AES
aes_sbox_inv = [ 0 for i in range(256) ]
for i in range(256):
    aes_sbox_inv[aes_sbox[i]] = i
aes_sbox = list(map(GF2_aes, aes_sbox))
aes_sbox_inv = list(map(GF2_aes, aes_sbox_inv))


# sbox for Mini-AES
GF2_miniaes = GF2(4, 0b10011)  # x^4 + x + 1 = Mini-AES

miniaes_sbox = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]

# inverse sbox for MiniAES
miniaes_sbox_inv = [ 0 for i in range(16) ]
for i in range(16):
    miniaes_sbox_inv[miniaes_sbox[i]] = i

miniaes_sbox = list(map(GF2_miniaes, miniaes_sbox))
miniaes_sbox_inv = list(map(GF2_miniaes, miniaes_sbox_inv))

#Ghash

GF2_ghash = GF2(128, 0b11100001 << 120)  # 1 + x + x^2 + x^7 (+ x^128) = Ghash
