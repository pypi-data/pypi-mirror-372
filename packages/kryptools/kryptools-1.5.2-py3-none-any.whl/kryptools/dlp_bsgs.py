"""
Discrete log solvers: Shanks' baby-step-giant-step algorithm
"""

from math import isqrt


def dlog_bsgs(a: int, b: int, n: int, m: int = None, verbose: int = 0) -> int:
    """Compute the discrete log_a(b) in Z_n of an element `a` of order `m` using Shanks' baby-step-giant-step algorithm."""
    a %= n
    b %= n
    if not m:
        m = n - 1
    mm = 1 + isqrt(m - 1)

    # initialize baby_steps table
    if verbose:
        print("Computing baby steps", end="")
        show = mm // 100
        if show:
            print(": ", end="")
    else:
        show = 0
    baby_steps = {}
    baby_step = 1
    for k in range(mm):
        if show and not k % show and k:
            print(".", end="")
        baby_steps[baby_step] = k
        if b == baby_step:
            if verbose:
                print(".")
            return k
        baby_step = baby_step * a % n

    # now take the giant steps
    if verbose:
        print(".")
        print("Computing giant steps", end="")
        if show:
            print(": ", end="")
    giant_stride = pow(a, -mm, n)
    giant_step = b
    for l in range(1, mm):
        giant_step = (giant_step * giant_stride) % n
        if show and not l % show and l:
            print(".", end="")
        if giant_step in baby_steps:
            if verbose:
                print(".")
            return l * mm + baby_steps[giant_step]
    raise ValueError("DLP not solvable.")
