"""
Discrete log solvers: Quadratic sieve
"""

from math import exp, log, sqrt, gcd, isqrt
from random import randint, seed
from .nt import sqrt_mod
from .primes import sieve_eratosthenes
seed(0)


def determine_factorbound(n: int) -> (int, int):
    """Determines the optimal factor bound and the expected number of trys until a relation is found for a given `n`."""
    # Choosing B=p^(1/u) Canfield-Erdös-Pomerance gives us the expected running time |factorbase|^2 u^u = u^(u+2) n^(2/u)/log(n).
    # There is no explicit expression for the optimum, hence we use Newton
    u = 2 * sqrt(log(n) / log(log(n)))  # asymptotic value
    for _ in range(3):
        u = (2 * log(n) + u * u * (2 + log(u))) / (
            2 + 3 * u + 2 * u * log(u)
        )  # Newton iteration
    B = int(exp(log(n) / u))
    # B = int(exp(0.5 * sqrt( log(n) * log(log(n)) )*( 1 + 1/log(log(n)) )))
    # expected number of trys to find a relation for random values
    expected_trys = int(exp(u*log(u)))+1
    # expected number of trys to find a relation for sieved values
    expected_trys2 = int(exp(u*log(u/2)/2))+1
    return B, expected_trys, expected_trys2


def determine_trialdivison_bounds(B: int, factorbase: list) -> (int, int):
    """Determine the parameters for speeding up trial division."""
    if B < 12:
        return len(factorbase), None
    pollard_k = 1  # guess for the order to be used in the Pollard p-1 test
    smallprimes_len = 1  # number of primes we try first during trial division
    for p in factorbase:
        if p >= B:
            break
        k = p
        kk = k * p
        while kk < B:
            k = kk
            kk *= p
        pollard_k *= k
        smallprimes_len += 1
    return smallprimes_len, pollard_k


def is_smooth(n: int, factorbase: list, factorbase_len: int, smallprimes_len: int, pollard_k: int = None) -> list or None:
    """Try to factor `n` with respect to a given factorbase. Upon success a list of exponents with repect to the factorbase is returned. Otherwise None."""
    # factorbase_len = len(factorbase)
    factors = [0] * factorbase_len
    for i in range(smallprimes_len):
        p = factorbase[i]
        while n % p == 0:  # divide by p as many times as possible
            factors[i] += 1
            n = n // p
    if pollard_k:
        if gcd(pow(2, pollard_k, n)-1, n) == 1:  # Pollard p-1 test
            return None  # most likely not smooth, give up
        for i in range(smallprimes_len, factorbase_len):
            p = factorbase[i]
            while n % p == 0:  # divide by p as many times as possible
                factors[i] += 1
                n = n // p
    if n != 1:
        return None  # the number factors if at the end nothing is left
    return factors


def dlog_qs(a: int, b: int, n: int, m: int, pollard: bool = True, sieve_factor: float = None, verbose: int = 0) -> int:
    """
    Compute the discrete log_a(b) in Z_p of an element `a` of prime order `m` using Index Calculus with a quadratic sieve.
    The problem is assumed solvable.
    """
    # assert is_prime(m), "The order of a must be prime."
    # assert order(a, n) == m, "The order of a is incorrect."
    # assert pow(b, m, n) == 1, "The DLP is not solvable."

    def find_relation(include_b: bool) -> None or list:
        """Find a relation for b * a^x or a^x"""
        nonlocal a, b, m, n, max_trys, factorbase, factorbase_len, smallprimes_len, pollard_k, sieve_bound

        x_max = m - 1
        x_min = 0
        if include_b:
            x_min = 1
        trys = 0
        while trys < max_trys:  # first find a relation involving b
            x = randint(x_min, x_max)
            if include_b:
                bax = b * pow(a, x, n) % n
            else:
                bax = pow(a, x, n)
            relation = is_smooth(bax, factorbase, factorbase_len, smallprimes_len, pollard_k)
            if relation:
                break
            trys += 1
        else:
            raise RuntimeWarning(f"Sorry, Quadratic Sieve failed to find a new relation after {trys} trys.")
        if verbose > 2:
            if include_b:
                print(f"rel found: b*a^{x}=", b * pow(a, x, n) % n, relation)
            else:
                print(f"rel found: a^{x}=", pow(a, x, n), relation)
        relation.reverse()  # the linear algebra is slightly faster if we take the large primes first
        if include_b:
            relation += [1, x]
        else:
            relation += [ 0, x ]
        relation = [0] * sieve_bound + relation # sieve values + primes + b + x
        return relation

   # this functions does the linear algebra
    def process_relation(relation: list) -> None or int:
        """Add a new relation to the linear system and keep the system in echelon form."""
        nonlocal a, b, m, n, relations, len_relations, n_relations

        n_relations += 1
        # Gauss elimination
        for i in range(len_relations):
            ri = relation[i] % m
            if ri == 0:
                continue
            if relations[i] is not None:  # subtract the current relations
                relation[i] = 0
                for j in range(i + 1, len_relations + 1):
                    relation[j] = (relation[j] - ri * relations[i][j]) % m
                continue
            # normalize the first nonzero entry
            rinv = pow(ri, -1, m)
            relation[i] = 1
            for j in range(i+1, len_relations + 1):
                relation[j] = rinv * relation[j] % m
            relations[i] = relation
            if verbose > 2:
                print(n_relations, f"rel found (index={i}) :", relation)
            elif verbose > 1:
                print(n_relations, f"rel found (index={i})")
            index = i
            break  # we don't need a reduced echelon form
        else:  # the relation contains no new information
            if verbose > 1:
                print(n_relations, "redundant rel found")
            return None
        #for i in range(index):  # reduced echelon form
        #    if relations[i] != None:
        #        ri = relations[i][index]  # make this entry zero
        #        if ri > 0:
        #            relations[i][index] = 0
        #            for j in range(index+1, len_relations + 1):
        #                relations[i][j] = (relations[i][j] - ri * relation[j]) % m
        #print(n_relations, f"i={i}={index} ({len_relations})", relations)
        if index == len_relations - 1:  # we found the solution
            if verbose:
                print(f"Success after {n_relations} relations out of {len_relations}.")
            #for i in range(lf):
            #    p = factorbase[i]
            #    print(f'{p:d}',pow(p,m,n)==1,relations[i])
            x = (m - relations[index][len_relations]) % m
            if pow(a, x, n) == b:
                return x
            raise RuntimeWarning("Sorry, Quadratic Sieve failed! Either the DLP is not solvable or the order is not prime or incorrect.")

    #
    # Determine the parameters
    #

    B, expected_trys, expected_trys2 = determine_factorbound(n)
    max_trys = 10 * expected_trys
    factorbase = []
    factorbase = tuple(p for p in sieve_eratosthenes(B) if gcd(p,n) == 1)  # compute the factorbse
    factorbase_log = [log(p) for p in factorbase]  # we add these up to test if a number will probably factor
    factorbase_len = len(factorbase)  # length of the factorbase
    if factorbase_len == 0:
        raise RuntimeWarning("Sorry, Index Calculus could not find a factorbase!")
    smallprimes_len, pollard_k = factorbase_len, None
    if pollard:  # should we speed up trial division with Pollard p-1
        smallprimes_len, pollard_k = determine_trialdivison_bounds(B // 150, factorbase)
    no_sieve_bound = 1  # We do not sieve for primes smaller than this bound (not worth the effort)
    no_sieve_primes = [ ]
    for i in range(factorbase_len):
        if factorbase[i] > no_sieve_bound:
            break
        no_sieve_primes.append(i)

    if sieve_factor is None:  # Smaller numbers seem to require a larger sieve range
        if n.bit_length() < 30:
            sieve_factor = 3
        elif n.bit_length() < 50:
            sieve_factor = 2
        elif n.bit_length() < 70:
            sieve_factor = 1.5
        else:
            sieve_factor = 1.2
    sieve_bound = int(sieve_factor*(2*expected_trys2 + factorbase_len))+1
    if verbose:
        print(f"Factorbase: bound = {B},  size = {factorbase_len} + {sieve_bound} = {factorbase_len + sieve_bound}, max_trys = {max_trys}")
    factors = [ {} for j in range(sieve_bound) ]  # here we will store the prime factors for the points we are sieving

    #
    # Do the sieving
    #

    sn = isqrt(n - 1) + 1  # ceil(sqrt(n))
    d = sn**2 - n
    sn2 = 2 * sn

    for j in range(sieve_bound):
        # we sieve with respect to the quadratic polynomial f_j(x) = (x+sn)*(x+j+sn) - n = x^2 + (2*sn+j)*x + (d+j*sn)
        snj = sn2 + j
        dj = d + j * sn
        max_j = sieve_bound - j
        for i in range(factorbase_len):
            p = factorbase[i]
            if p <= no_sieve_bound:
                continue
            aa = snj % p
            bb = dj % p
            # determine the roots of f_j(x) mod p
            if p == 2:
                if aa == 0:
                    roots = [bb]
                elif bb == 0:
                    roots = [0, 1]
                else:
                    continue  # no root
            else:
                r = sqrt_mod(aa**2 - 4 * bb, p)
                if r is None:  # no roots
                    continue
                inv2 = pow(2, -1, p)
                if r == 0:
                    roots = [-(inv2 * aa) % p]  # one root
                else:
                    roots = [ (inv2 * (r - aa)) % p, (inv2 * (-r - aa)) % p ]  # two roots  pylint: disable=E1130
            for r in roots:
                x = r  # start value for x
                while x < max_j:
                    # record which primes divide x and sum up the logs
                    if x in factors[j]:
                        factors[j][x][0].append(i)
                        factors[j][x][1] += factorbase_log[i]
                    else:
                        factors[j][x] = [[i], factorbase_log[i]]
                    x += p
    if verbose:
        print("Done sieving.")

    #
    # Set up the linear system
    #
    len_relations = factorbase_len + sieve_bound + 1
    relations = [None] * len_relations
    n_relations = 0
    n_relations_redundant = 0
    #
    # Find the relation for b plus another relation for a (I don't know why, but with this extra relation we find a solution much faster)
    #
    for include_b in (True, False):
        relation = find_relation(include_b)
        res = process_relation(relation)
        if res:
            return res

    #
    # find the B-smooth numbers and add them to the system
    #

    for s in range(sieve_bound):
        for j in range(s+1):
            x = s - j
            if x not in factors[j]:
                continue
            v = (x + sn) * (x + j + sn) - n
            if factors[j][x][1] < 0.49 * log(v):
                continue  # the number is unlikely to factor
            primes = factors[j][x][0]
            primes.extend(no_sieve_primes)
            factors_jx = [0] * factorbase_len
            for i in primes:
                p = factorbase[i]
                if p <= no_sieve_bound and v % p != 0:
                    continue
                k = 1  # per our sieve we already know that p divides v
                v //= p
                while v % p == 0:  # divide by p as many times as possible
                    k += 1
                    v //= p
                factors_jx[i] = k
            if v == 1:
                factors_jx.reverse()
                relation = [0] * sieve_bound + factors_jx + [0, 0]
                if j == 0:
                    relation[x] = 2
                else:
                    relation[x] = 1
                    relation[x + j] = 1
                res = process_relation(relation)
                if res:
                    return res

    raise RuntimeWarning(f"Sorry, Quadratic sieve could not find enough relations! ({n_relations} - {n_relations_redundant} = {n_relations - n_relations_redundant} out of {len_relations}). Try to increase sieve_factor={sieve_factor}")
