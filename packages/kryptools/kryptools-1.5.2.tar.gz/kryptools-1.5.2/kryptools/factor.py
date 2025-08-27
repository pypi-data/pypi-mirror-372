"""
Factorization of integers:
    factorint(n) factorize the integer n into prime factors
    divisors(n) unsorted list of all divisors of the integer n
"""

from math import isqrt, gcd, prod, floor, log10
from .primes import sieve_eratosthenes, is_prime
from .intfuncs import perfect_power
from .factor_pm1 import _pm1_parameters, factor_pm1
from .factor_ecm import _ecm_parameters, factor_ecm
#from .factor_qs import factor_qs


# Factoring


def _factor_fermat(n: int, maxsteps: int = 10, verbose: int = 0) -> list:
    "Fermat method"
    if verbose:
        print(f"Factoring (Fermat, steps={maxsteps}): {n} ({floor(log10(n)) + 1} digits)")
    parameters = {11: (12, 6), 23: (12, 0),
                  5: (6, 3), 17: (6, 3),
                  19: (4, 2), 7: (4, 0),
                  1: (2, 1), 13: (2, 1)}
    start = isqrt(n - 1) + 1
    step, mod = parameters[n % 24]
    start += (mod - start) % step
    if verbose > 1:
        print("Working ", end="")
    maxa = (n + 9) // 6 + 1
    if maxsteps:
        maxa = min(maxa, start + maxsteps * step + 1)
    for a in range(start, maxa, step):
        if verbose > 1:
            print(".", end="")
        b = isqrt(a * a - n)
        if b * b == a * a - n:
            if verbose > 1:
                print("")
            return a - b
    if verbose > 1:
        print("")


def factorint(n: int, trial_bnd: int = 2500, verbose: int = 0) -> dict:
    "Factor an ineger `n` into prime factors."
    prime_factors = {}
    if not isinstance(n, int):
        raise ValueError("Number to be factored must be an integer!")
    if n == 0:
        return {0: 1}
    if n < 0:
        n *= -1
        prime_factors[-1] = 1

    def add_factors(m: int, mm: tuple) -> None:
        "Delete m from remaining factors and add its factors mm to the appropriate dict."
        k = remaining_factors[m]
        del remaining_factors[m]

        for m_i in mm:
            if m_i in prime_factors:
                prime_factors[m_i] += k
            elif is_prime(m_i, trialdivision=False):
                prime_factors[m_i] = k
            else:
                if m_i in remaining_factors:
                    remaining_factors[m_i] += k
                elif m_i in new_factors:
                    new_factors[m_i] += k
                else:
                    new_factors[m_i] = k

    if verbose:
        print(f"Factoring: {n} ({floor(log10(n)) + 1} digits)")
    # trial division
    B = max(3, trial_bnd)
    factorbase = sieve_eratosthenes(B)
    for p in factorbase:
        k = 0
        while n % p == 0:
            k += 1
            n //= p
        if k:
            prime_factors[p] = k
    if n == 1:
        return prime_factors
    if verbose:
        print("Trial division found:", list(prime_factors))
    # check if the remainder is a perfect power
    res = perfect_power(n)
    if res:
        n, k = res
    else:
        k = 1
    if is_prime(n, trialdivision=False):
        prime_factors[n] = k
        return prime_factors
    remaining_factors = {n: k}

    # https://gitlab.inria.fr/zimmerma/ecm/
    ECM_PARAMETERS = [
        [     5000,         130000,    54],
        [    11000,        1900000,    74],
        [    50000,       13000000,   221],
        [   250000,      130000000,   453],
        [  1000000,     1000000000,   984],
        [  3000000,     5700000000,  2541],
        [ 11000000,    35000000000,  4949],
        [ 43000000,   240000000000,  8266],
        [110000000,   780000000000, 20158],
        [260000000,  3200000000000, 47173],
        [850000000, 16000000000000, 77666]
    ]
    fermat_steps = 10

    for nr, parameters in enumerate(ECM_PARAMETERS):
        fermat_steps += 10
        B1, B2, num_curves = parameters
        p_max = isqrt(max(remaining_factors))+1
        B1 = min(B1, p_max//50)
        B1 += B1 & 1
        B2 = min(B2, p_max)
        B2 += B2 & 1
        num_curves *= 2
        D = isqrt(B2)

        if verbose:
            print(f"Round {nr+1} (B1={B1})")

        primes = sieve_eratosthenes(B1 - 1 + ((B2 - B1 + 1) // (2 * D) + 1) * 2 * D)
        pm1_parameters = tuple([10 * B1, B2] + list(_pm1_parameters(10 * B1, B2, primes=primes)))
        ecm_parameters = tuple([B1, B2, num_curves] + list(_ecm_parameters(B1, B2, D, primes=primes)))

        methods = {_factor_fermat: "fmt", factor_pm1: "pm1", factor_ecm: "ecm"}  #, factor_qs: "qs"}
        while remaining_factors:
            new_factors = {}
            for method, method_name in methods.items():
                factors = list(remaining_factors) # make a copy to avoid a runtime error if the dict changes
                for m in factors:
                    if method == _factor_fermat:  # pylint: disable=W0143
                        tmp = _factor_fermat(m, maxsteps=fermat_steps, verbose=max(0, verbose - 1))
                    elif method == factor_pm1:  # pylint: disable=W0143
                        tmp = factor_pm1(m, pm1_parameters=pm1_parameters, verbose=max(0, verbose - 1))
                    elif method == factor_ecm:  # pylint: disable=W0143
                        tmp = factor_ecm(m, ecm_parameters=ecm_parameters, verbose=max(0, verbose - 1))
                    else:
                        tmp = method(m, verbose=max(0, verbose - 1))
                    if tmp:
                        tmp2 = m // tmp
                        g = gcd(tmp, tmp2)
                        if g > 1:
                            tmp3 = [g, g]
                            for x in (tmp, tmp2):
                                x //= g
                                while x % g == 0:
                                    tmp3.append(g)
                                    x //= g
                                if x > 1:
                                    tmp3.append(x)
                        else:
                            tmp3 = [tmp, tmp2]
                        if verbose > 0:
                            print(f"Factors found ({method_name}): ", tmp3)
                        add_factors(m, tmp3)
            if not new_factors:
                break
            for m, k in new_factors.items():
                if m in remaining_factors:
                    remaining_factors[m] += k
                else:
                    remaining_factors[m] = k
            if verbose > 1:
                print("Remaining: ", remaining_factors)

        if len(remaining_factors) == 0:
            return prime_factors

    raise ValueError("Incomplete factorization:", prime_factors, remaining_factors, new_factors)

# Divisors

def divisors(n:int, proper:bool = False) -> int:
    """Returns an unsorted list of all divisors of an integer `n`."""
    if not isinstance(n, int):
        raise ValueError("Number must be an integer!")
    n = abs(n)
    if proper:
        divisor_list = []
    else:
        divisor_list = [1]
    if n <= 1:
        return divisor_list
    facctordict= factorint(n)
    primes = list(facctordict)
    nprimes = len(primes)
    multiplicites = [facctordict[p] for p in primes]

    exponents = [0] * nprimes
    i = 0
    while True:
        exponents[i] += 1
        if exponents[i] > multiplicites[i]:
            while exponents[i] > multiplicites[i]:
                exponents[i] = 0
                i += 1
                exponents[i] += 1
            i = 0
        d = prod(primes[i] ** exponents[i] for i in range(nprimes))
        if d == n:
            if proper:
                return divisor_list
            divisor_list.append(n)
            return divisor_list
        divisor_list.append(d)
