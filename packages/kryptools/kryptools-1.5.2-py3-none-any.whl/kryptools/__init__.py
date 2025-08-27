"""
Implemenation of same basic algorithms used in cryptography.
"""

__author__ = "Gerald Teschl"
__copyright__ = "Copyright 2024-2025, Gerald Teschl"
__license__ = "MIT License"
__version__ = "1.5.1"
__email__ = "Gerald.Teschl@univie.ac.at"

from .nt import egcd, cf, convergents, legendre_symbol, jacobi_symbol, sqrt_mod, euler_phi, carmichael_lambda, moebius_mu, is_carmichael_number, order, crt
from .primes import sieve_eratosthenes, prime_pi, primorial, is_prime, next_prime, previous_prime, next_safeprime, previous_safeprime, random_prime, random_strongprime, is_safeprime, random_safeprime, is_blumprime, random_blumprime, miller_rabin_test, lucas_test
from .intfuncs import iroot, ilog, perfect_square, perfect_power, prime_power
from .factor import factorint, divisors
from .dlp import dlog
from .ec import EC_Weierstrass
from .la import Matrix, zeros, eye
from .lat import gram_det, hadamard_ratio, hermite_nf, gram_schmidt, babai_round_cvp, babai_round_bnd, babai_plane_cvp, babai_plane_bnd, lagrange_lr, lll, random_unimodular_matrix
from .poly import Poly, lagrange_interpolation
from .Zmod import Zmod
from .GF2 import GF2, GF2_aes, GF2_miniaes, GF2_ghash
from .code import left_standard_form, gen2pchk, hamming_dist, Goppa, CyclicCode, ReedSolomonCode
from .blockcipher import BlockCipher, bytexor
from .aes import AESKeySchedule, AESCipher, AESBlockCipher
from .des import list2int, int2list, permute, invert_permutation, rotate_left, SDESKeySchedule, SDESCipher, DESKeySchedule, DESCipher, DESBlockCipher
from .keccak import Keccak, SHA3, SHAKE
from .sha1 import SHA1
