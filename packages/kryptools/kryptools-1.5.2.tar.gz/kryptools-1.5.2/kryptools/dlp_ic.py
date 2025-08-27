"""
Discrete log solvers: Index calculus
"""

from math import gcd
from random import randint, seed
from .primes import sieve_eratosthenes
from .dlp_qs import determine_factorbound, determine_trialdivison_bounds, is_smooth
seed(0)


def dlog_ic(a: int, b: int, n: int, m: int, pollard: bool = True, verbose: int = 0) -> int:
    """Compute the discrete log_a(b) in Z_p of an element `a` of prime order `m` using Index Calculus."""

    # assert is_prime(m), "The order of a must be prime."
    # assert order(a, n) == m, "The order of a is incorrect."
    # assert pow(b, m, n) == 1, "The DLP is not solvable."

    def find_relation(include_b: bool) -> None or list:
        """Find a relation for b * a^x or a^x"""
        nonlocal a, b, m, n, max_trys, factorbase, factorbase_len, smallprimes_len, pollard_k

        x_max = m - 1
        x_min = 0
        if include_b:
            x_min = 1
        trys = 0
        while trys < max_trys:
            x = randint(x_min, x_max)
            if include_b:
                bax = b * pow(a, x, n) % n
            else:
                bax = pow(a, x, n)
            relation = is_smooth(
                bax, factorbase, factorbase_len, smallprimes_len, pollard_k)
            if relation:
                break
            trys += 1
        else:
            raise RuntimeWarning(f"Sorry, Index Calculus failed to find a relation after {trys} trys.")
        if verbose > 2:
            if include_b:
                print(f"rel found: b*a^{x}=", b * pow(a, x, n) % n, relation)
            else:
                print(f"rel found: a^{x}=", pow(a, x, n), relation)
        # the linear algebra is slightly faster if we take the large primes first
        relation.reverse()
        if include_b:
            relation += [1, x]
        else:
            relation += [0, x]
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
            raise RuntimeWarning("Sorry, Index Calculus failed! Either the DLP is not solvable, or the order is not prime or incorrect.")

    #
    # Determine the parameters
    #
    B, expected_trys = determine_factorbound(n)[:2]
    max_trys = 10 * expected_trys
    factorbase = tuple(p for p in sieve_eratosthenes(B) if gcd(p,n) == 1)  # compute the factorbse
    factorbase_len = len(factorbase)  # length of the factorbase
    if factorbase_len == 0:
        raise RuntimeWarning("Sorry, Index Calculus could not find a factorbase!")
    smallprimes_len, pollard_k = factorbase_len, None
    if pollard:  # should we speed up trial division with Pollard p-1
        smallprimes_len, pollard_k = determine_trialdivison_bounds(B // 150, factorbase)
    if verbose > 0:
        print(f"Factorbase: bound = {B}, size = {factorbase_len}, max_trys = {max_trys}")

    # Start the work
    n_relations = 0  # number of relations found

    # first find a relation involving b
    relation = find_relation(True)

    # Set up the linear system
    len_relations = factorbase_len + 1
    relations = [None] * len_relations
    res = process_relation(relation)
    if res:
        return res

    while n_relations < 5 * factorbase_len:  # find relations for all primes in our factor base
        relation = find_relation(False)
        res = process_relation(relation)
        if res:
            return res

    raise RuntimeWarning("Sorry, Index Calculus could not find enough relations! ({n_relations} - {n_relations_redundant} = {n_relations - n_relations_redundant} out of {len_relations})")
