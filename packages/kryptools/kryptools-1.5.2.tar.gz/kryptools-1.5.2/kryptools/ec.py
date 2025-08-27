"""
Elliptic curves:
    EC_Weierstrass() constructor for a Weierstrass curve y^2 = x^3 + ax + b mod p
"""

from math import isqrt, floor, sqrt
from random import randint
from .factor import factorint
from .nt import legendre_symbol, sqrt_mod, crt
from .Zmod import Zmod
from .poly import Poly


class EC_Weierstrass():
    """
    Elliptic curve in Weierstrass normal form `y^2 = x^3 + ax + b mod p`.

    Example:

    To define an elliptic curve y^2 = x^3 + 3x + 1 mod 239 use
    >>> ec = EC_Weierstrass(239, 3, 1)

    To declare a point on the elliptic curve use
    >>> P = ec(43, 222)
    >>> Q = ec(148, 218))


    The usual arithmetic operations are supported.
    >>> P + Q
    (195, 41)
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, p: int, a: int, b: int, order: int = None):
        if p < 3:
            raise ValueError(f"{p} must be a prime larger than 2.")
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            raise ValueError("Curve is singular!")
        self.p = p
        self.gf = Zmod(p, short=True)
        self.a = self.gf(a % p)
        self.b = self.gf(b % p)
        self.group_order = order
        self.group_order_factors = None
        self.psi_list = [Poly([0], ring=self.gf)]  # division polynomials
        self.short = False  # display points in short format
        self.hex = False  # display points as hex values in compressed format

    def __call__(self, x: int | str | None = None, y: int | None = None, short: bool = False):
        if isinstance(x, str):
            x = x.replace(" ", "")
            coordinate_type = x[:2]
            x = x[2:]
            if coordinate_type in ('02', '03'):
                short = 1
                x = int(x, 16)
                if type == '02':
                    y = 0
                else:
                    y = 1
            elif type == '04':
                l = len(x)//2
                y = int(x[l:], 16)
                x = int(x[:l], 16)
            else:
                raise ValueError('Unsupported hex type.')
        return ECPoint(x, y, self, short)

    def __iter__(self):
        yield self.inf()
        for x in range(self.p):
            y2 = int(x**3 + self.a * x + self.b)
            y = sqrt_mod(y2, self.p)
            if y is None:
                continue
            yield ECPoint(x, y, self)
            if y:
                yield ECPoint(x, (self.p - y) % self.p, self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.p == other.p and self.a == other.a and self.b == other.b
        return False

    def __contains__(self, P: "ECPoint") -> bool:
        if not isinstance(P, ECPoint) or P.curve != self:
            return False
        if P.x is None and P.y is None:
            return True
        return P.y**2 == P.x**3 + self.a * P.x + self.b

    def inf(self):
        "Point at infinity"
        return ECPoint(None, None, self)

    def info(self):
        "Display some basic info on the curve"
        out = "Weierstrass curve y^2 = x^3"
        if int(self.a):
            out += f" + {self.a} x"
        if int(self.b):
            out += f" + {self.b}"
        out += f" over Z_{self.p}."
        print(out)

    def add(self, x1, y1, x2, y2):
        "Point addition"
        if x1 is None:
            return x2, y2
        if x2 is None:
            return x1, y1
        if x1 == x2:
            if y1 == y2:
                return self.dbl(x1, y1)
            return None, None
        s = (y2 - y1) / (x2 - x1)
        x3 = s**2 - x1 - x2
        y3 = s * (x1 - x3) - y1
        return x3, y3

    def dbl(self, x, y):
        "Point doubling"
        if x is None or not y:
            return None, None
        s = (3 * x**2 + self.a) / (2 * y)
        x3 = s**2 - x - x
        y3 = s * (x - x3) - y
        return x3, y3

    def mult(self, j: int, x, y):  # Addition-subtraction ladder
        "Point multiplication"
        if j == 0 or x is None:
            return None, None
        if j < 0:
            y = -y
            j *= -1
        #    xx, yy = None, None
        #    while j > 0:
        #        # If j is odd, add x
        #        if j & 1:
        #            xx, yy = self.add(xx, yy, x, y)
        #        # Now double
        #        j >>= 1  # j= j//2
        #        x, y = self.dbl(x, y)
        xx, yy = x, y
        j3 = 3 * j
        form = "0" + str(j3.bit_length()) + "b"
        for a, b in zip(format(j3, form)[1:-1], format(j, form)[1:-1]):
            xx, yy = self.dbl(xx, yy)
            if a == "1" and b == "0":
                xx, yy = self.add(xx, yy, x, y)
            if a == "0" and b == "1":
                xx, yy = self.add(xx, yy, x, -y)
        return xx, yy

    def random(self):
        "Return a random point."
        j = -1
        while j == -1:
            x = self.gf(randint(0, self.p - 1))
            y2 = int(x**3 + self.a * x + self.b)
            j = legendre_symbol(y2, self.p)
        return ECPoint(x, randint(0, 1), self, short=True)

    def psi(self, n: int):
        """The x-part of the n'th division polynomial."""
        if len(self.psi_list) < 5:
            self.psi_list = [ Poly([i], ring=self.gf) for i in range(3)]
            self.psi_list += [ Poly([-self.a * self.a, 12 * self.b, 6 * self.a, 0, 3], ring=self.gf) ]
            self.psi_list += [ Poly([-4 * self.a**3 - 32 * self.b * self.b, -16 * self.a * self.b, -20 * self.a * self.a, 80 * self.b, 20 * self.a, 0, 4], ring=self.gf) ]
        if len(self.psi_list) < n + 1:
            y2 = Poly([self.b, self.a, 0, 1], ring=self.gf)**2
            ti = 1 / self.gf(2)
            for m in range(len(self.psi_list), n + 1):
                if m % 2:  # odd
                    m = (m - 1) // 2
                    if m % 2:
                        self.psi_list += [ self.psi_list[m + 2] * self.psi_list[m]**3 - y2 * self.psi_list[m - 1] * self.psi_list[m + 1]**3]
                    else:
                        self.psi_list += [ y2 * self.psi_list[m + 2] * self.psi_list[m]**3 - self.psi_list[m - 1] * self.psi_list[m + 1]**3]
                else:  # even
                    m = m // 2
                    self.psi_list += [ ti * self.psi_list[m] * (self.psi_list[m + 2] * self.psi_list[m - 1]**2 - self.psi_list[m - 2] * self.psi_list[m + 1]**2) ]
        return self.psi_list[n]

    def order(self, order: int = None) -> int:
        "Return the group order."
        if order:
            self.group_order = order
        elif not self.group_order:
            if self.p < 230:
                self.group_order = self.order_naive()
            else:
                self.group_order = self.order_shanks_mestre()
        return self.group_order

    def factor_order(self) -> dict:
        "Factor the group order."
        if self.group_order_factors:
            return self.group_order_factors
        if not self.group_order:
            self.order()
        self.group_order_factors = factorint(self.group_order)
        return self.group_order_factors

    def order_naive(self) -> int:
        "Return the order of the group by adding the Legendre symbols."
        a1 = (int(self.a) + 1) % self.p
        y = int(self.b)
        order = self.p + 1 + legendre_symbol(y, self.p)
        for x in range(self.p - 1):
            y += (3 * x * (x + 1) + a1) % self.p
            order += legendre_symbol(y, self.p)
        return order

    def order_shanks_mestre(self) -> int:
        "Return the order of the group using the Shanks-Mestre algorithm."
        if self.p < 230:
            return self.order_naive()
        j = 1
        while j != -1:
            g = randint(1, self.p - 1)
            j = legendre_symbol(g, self.p)
        W = floor(sqrt(2 * sqrt(self.p)))
        a, b = int(self.a), int(self.b)
        while True:
            sigma = 0
            while sigma == 0:
                x = randint(0, self.p - 1)
                sigma = legendre_symbol(x**3 + a * x + b, self.p)
            if sigma == 1:
                ec = EC_Weierstrass(self.p, a, b)
            else:
                ec = EC_Weierstrass(
                    self.p, pow(g, 2, self.p) * a, pow(g, 3, self.p) * b
                )
                x = g * x % self.p
            x = ec.gf(x)
            y2 = int(x**3 + ec.a * x + ec.b)
            y = ec.gf(sqrt_mod(y2, self.p))

            A = {}
            xx, yy = ec.mult(ec.p + 1, x, y)
            for j in range(W):
                if xx is None:
                    A[None] = j
                else:
                    A[int(xx)] = j
                xx, yy = ec.add(xx, yy, x, y)
            B = []
            xg, yg = ec.mult(W, x, y)
            xx, yy = None, None
            for j in range(W + 1):
                if xx is None:
                    if xx in A:
                        B.append([A[None], j])
                elif int(xx) in A:
                    B.append([A[int(xx)], j])
                xx, yy = ec.add(xx, yy, xg, yg)
            if len(B) == 1:
                beta, gamma = B[0]
                break
        t = beta + gamma * W
        if ec.mult(ec.p + 1 + t, x, y)[0] is not None:
            t = beta - gamma * W
            assert ec.mult(ec.p + 1 + t, x, y)[0] is None

        return self.p + 1 + sigma * t


class ECPoint:
    "Point on an elliptic curve"

    def __init__(self, x: int | None, y: int | None, curve: EC_Weierstrass, short: bool = False):
        self.curve = curve
        if x is None:
            self.x = None
            self.y = None
        else:
            self.x = curve.gf(x)
            if short:
                y2 = int(self.x**3 + curve.a * self.x + curve.b)
                j = legendre_symbol(y2, curve.p)
                if j == -1:
                    raise ValueError("Point not on curve!")
                y1 = sqrt_mod(y2, curve.p)
                if y % 2 == 0:
                    y = y1
                else:
                    y = (curve.p - y1) % curve.p
            self.y = curve.gf(y)
            if self not in curve:
                raise ValueError("Point not on curve!")

    def __repr__(self):
        if self.x is None:
            return "O"
        if self.curve.hex is True:
            if self.curve.short is True:
                pre = '0x02'
                if int(self.y) % 2 == 1:
                    pre = '0x03'
                return pre+f'{int(self.x):x}'
            pre = '0x04'
            return pre+f'{int(self.x):x}{int(self.y):x}'
        if self.curve.short is True:
            return f"({int(self.x)}, {int(self.y) % 2})"
        return f"({int(self.x)}, {int(self.y)})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not self.curve == other.curve:
            return False
        if self.x is None:
            return other.x is None
        if other.x is None:
            return self.x is None
        return self.x == other.x and self.y == other.y

    def __bool__(self):
        return self.x is not None

    def __hash__(self):
        if self.x is None:
            return hash(None)
        return hash((int(self.x), int(self.y)))

    def __add__(self, other: "ECPoint") -> "ECPoint":
        if not isinstance(other, self.__class__) or self.curve != other.curve:
            raise ValueError(f"Cannot add {self} and {other}.")
        x, y = self.curve.add(self.x, self.y, other.x, other.y)
        return ECPoint(x, y, self.curve)

    def __sub__(self, other: "ECPoint") -> "ECPoint":
        return self + other.__neg__()

    def __rmul__(self, scalar: int) -> "ECPoint":
        x, y = self.curve.mult(scalar, self.x, self.y)
        return ECPoint(x, y, self.curve)

    def __neg__(self) -> "ECPoint":
        if self.x is None or not self.y:
            return self
        return ECPoint(self.x, -self.y, self.curve)  # pylint: disable=E1130

    def order(self) -> int:
        """Compute the order of an element."""
        if self.x is None:
            return 1
        self.curve.factor_order()  # Make sure the factorization is available
        order = self.curve.group_order
        for p, k in self.curve.group_order_factors.items():
            for _ in range(k):
                order_try = order // p
                if self.curve.mult(order_try, self.x, self.y)[0] is None:
                    order = order_try
                else:
                    break
        return order

    def psi(self, n: int):
        """Value of the n'th division polynomial."""
        if n % 2:
            return self.curve.psi(n)(self.x)
        return self.y * self.curve.psi(n)(self.x)

    def dlog(self, other: "ECPoint") -> int:
        """Compute the discrete log_P(Q) in EC."""
        m = other.order()
        mf = factorint(m)
        assert m * self == other.curve(None, None), "DLP not solvable."
        # We first use Pohlig-Hellman to split m into powers of prime factors
        mm = []
        ll = []
        for pj, kj in mf.items():
            Pj = (m // pj**kj) * other
            Qj = (m // pj**kj) * self
            l = Qj.dlog_ph(Pj, pj, kj)
            if l is None:
                return None
            mm += [pj**kj]
            ll += [l]
        return crt(ll, mm)

    def dlog_ph(self, other: "ECPoint", q: int, k: int) -> int:
        """Compute the discrete log_P(Q) in EC if P has order q^k using Pohlig-Hellman reduction."""
        if k == 1 or q**k < 10000:
            return self.dlog_switch(other, q**k)
        Pj = q**(k - 1) * self
        P1 = Pj
        Qj = q**(k - 1) * other
        xj = Qj.dlog_switch(P1, q)
        for j in range(2, k + 1):
            Pj = q**(k - j) * self
            Qj = q**(k - j) * other - xj * Pj
            yj = Qj.dlog_switch(P1, q)
            xj = xj + q ** (j - 1) * yj % q**j
        return xj

    def dlog_switch(self, other: "ECPoint", m: int) -> int:
        """Compute the discrete log_P(Q) in EC if P has order m choosing an appropriate method."""
        if m < 100:
            return self.dlog_naive(other, m)
        return self.dlog_bsgs(other, m)

    def dlog_naive(self, other: "ECPoint", m: int) -> int:
        """Compute the discrete log_P(Q) in EC using an exhaustive search."""
        if not self.curve == other.curve and not isinstance(self, other.__class__):
            raise ValueError("Points must be on the same curve!")
        j = 0
        xx, yy = None, None
        while xx != self.x:
            j += 1
            xx, yy = self.curve.add(xx, yy, other.x, other.y)
            if xx is None:
                raise ValueError("DLP not solvabel!")
        if yy == self.y:
            return j
        return m - j

    def dlog_bsgs(self, other: "ECPoint", m: int) -> int:
        """Compute the discrete log_P(Q) in EC if P has order m using Shanks' baby-step-giant-step algorithm."""
        if not self.curve == other.curve and not isinstance(other, self.__class__):
            raise ValueError("Points must be on the same curve!")
        mm = 1 + isqrt(m - 1)
        m2 = mm//2 + mm % 1  # we use the group symmetry to halve the number of steps
        # initialize baby_steps table
        baby_steps = {}
        baby_step = other
        for j in range(1, m2+1):
            baby_steps[int(baby_step.x)] = j, int(baby_step.y)
            baby_step += other

        # now take the giant steps
        giant_stride = -mm * other
        giant_step = self
        for l in range(mm+1):
            if giant_step.x is None:
                return l * mm
            if int(giant_step.x) in baby_steps:
                j = baby_steps[int(giant_step.x)][0]
                if int(giant_step.y) != baby_steps[int(giant_step.x)][1]:
                    j *= -1
                return (l * mm + j) % m
            giant_step += giant_stride
        raise ValueError("DLP not solvabel!")
