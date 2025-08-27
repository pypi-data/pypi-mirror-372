[![Pypi](https://img.shields.io/pypi/v/kryptools)](https://pypi.org/project/kryptools)
[![PyVersion](https://img.shields.io/pypi/pyversions/kryptools)](https://www.python.org)
[![License](https://img.shields.io/pypi/l/kryptools)](https://github.com/teschlg/kryptools/blob/main/LICENSE)
[![Pylint](https://github.com/teschlg/kryptools/actions/workflows/pylint.yml/badge.svg)](https://github.com/teschlg/kryptools/actions/workflows/pylint.yml)
[![Pytest](https://github.com/teschlg/kryptools/actions/workflows/run_test.yml/badge.svg)](https://github.com/teschlg/kryptools/actions/workflows/run_test.yml)

# kryptools
Gerald Teschl <Gerald.Teschl@univie.ac.at>

This package was written for my course on cryptography. Consequently its intention is
mainly educational, that is, to show how basic algorithms are implemented. In particular,
you are welcome to read (and modify) the source. Any suggestions on how to make the
code more readable or make it better are welcome. However, my main goal is to keep
it simple and readability will be preferred over small speed improvements.

> **Warning**
> These tools are intended for experimenting with cryptographic algorithms. They are not intended for use in real applications.

It does not require any external libraries.

The tools contained are:

* number theory: sqrt modulo primes, Jacobi/Legendre symbol, Chinese Remainder Theorem, continued fractions, etc.
* primes: Sieve of Erathostenes, primality tests, generation of random safe/strong primes
* solvers for discrete logarithms (naive, Pollard rho, Shanks baby step/giant step, index calculus, quadratic sieve)
* integer factorization (Fermat, Pollard p-1, Pollard rho, Lenstra's ECM, Dixon, basic quadratic sieve)
* elliptic curves (Weierstrass form), group operations, order, discrete logarithms
* linear algebra: Hermite normal form, Gram-Schmidt
* lattices: Hadamard ratio, Babai rounding/nearest plane algorithm, lattice reduction (Lenstra-Lenstra-Lovaz)
* linear codes: Hamming distance, left standard form, parity check matrix

* Matrix: a class for Matrices (inverse, det, reduced echelon form, etc.)
* Poly: a class for polynomials (division, modulo, factoring and irreducibility test over finite fields, Lagrange interpolation)
* Zmod: a class for the ring of integers modulo an integer
* GF2: a class for Galois fields GF(2^n)
* Goppa: a class for encoding and decoding Goppa codes
* CyclicCode: a class for encoding and decoding cyclic codes
* ReedSolomonCode: a class for encoding and decoding Reed-Solomon codes

* BlockCipher: a class implementing the usual modes of operation (ECB, CBC, GCM, etc.)
* AESCipher: individual AES operations
* DESCipher: individual DES operations

* SHA1: custom initial state, padding function
* Keccak: individual sponge operations, SHA3, SHAKE

Documentation can be found in the jupyter notebook
(mostly done, but might not contain everything: use the force, read the source).
