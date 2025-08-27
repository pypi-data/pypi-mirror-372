"""
DES and S-DES ciphers
"""

from math import ceil
from .blockcipher import BlockCipher

def permute(a: list[int], permutation: tuple[int]) -> list[int]:
    "Apply a permutation (DES style - counting starts at 1) to a list."
    return [ a[i-1] for i in permutation]

def invert_permutation(permutation: tuple[int]) -> tuple[int]:
    "Invert a permutation (DES style - counting starts at 1)."
    inverse = [ 0 ] * len(permutation)
    for i, j in enumerate(permutation):
        inverse[j-1] = i+1
    return tuple(inverse)

def rotate_left(l: list, n: int = 1) -> list:
    "Rotate a list cyclically n places to the left."
    n = n % len(l)
    return l[n:] + l[:n]

def int2list(x: int, length: int = 8) -> list:
    "Convert an integer or character to a list of binary digits."
    if not isinstance(x, int):
        x = ord(x)
    return [int(d) for d in str(format(x, "0" + str(length) + "b"))]

def list2int(a: list) -> int:
    "Convert a list of binary digits to an integer."
    s = 0
    for i, d in enumerate(reversed(a)):
        if d:
            s += 1 << i
    return s


# Generic classes for DES-type ciphers

class FeistelKeySchedule:
    "DES-type Feistel network key schedule"

    keylength: int = 2 # in bit; must be even
    print_hex = False
    # permutation tables (index starting at 1)
    IP: tuple = tuple() # PC-1 initial permutation
    CP: tuple = tuple() # PC-2 compression permutation for selection of key bits
    ROT: tuple = tuple()  # schedule of left shift

    def __init__(self, key: int):
        self.round = 0
        if isinstance(key, int) and 0 <= key < 2**self.__class__.keylength:
            self.key = [int(d) for d in str(format(key, "0" + str(self.__class__.keylength) + "b"))]
        elif isinstance(key, bytes) and len(key) == self.__class__.keylength //8:
            k = int.from_bytes(key, byteorder="big")
            self.key = [int(d) for d in str(format(k, "0" + str(self.__class__.keylength) + "b"))]
        else:
            raise NotImplementedError(f"Key must be a nonegative integer of at most {self.__class__.keylength} bits.")
        self.state = permute(self.key, self.__class__.IP)
        self.keylength = len(self.state)

    def __repr__(self):
        if self.__class__.print_hex:
            return str(format(int(self), "0" + str(ceil(self.keylength/4)) + "x"))
        return str(self.state)

    def __int__(self):
        s = 0
        for i, d in enumerate(reversed(self.state)):
            if d:
                s += 1 << i
        return s

    def next(self) -> list[int]:
        "Apply the key schedule and return the next key."
        key_len2 = self.keylength // 2
        rot = self.__class__.ROT[self.round]
        self.state = rotate_left(self.state[:key_len2], rot) + rotate_left(self.state[key_len2:], rot)
        self.round = (self.round + 1 ) % len(self.__class__.ROT)
        return permute(self.state, self.__class__.CP)

    def reset(self) -> None:
        "Reset key schedule."
        self.state = permute(self.key, self.__class__.IP)
        self.round = 0

    def gen_keys(self) -> list:
        "Generate all round keys."
        if self.round:
            self.reset()
        keys = []
        for _ in range(len(self.__class__.ROT)):
            keys.append(self.next())
        return keys



class FeistelCipher:
    "DES-type Feistel network"

    blocksize: int = 1 # in bytes; must be even
    print_hex = False
    key_schedule = FeistelKeySchedule
    # permutation tables (index starting at 1)
    IP: tuple = tuple() # initial permutation
    FP: tuple = tuple() # final permutation
    # cipher function
    E_box: tuple = tuple() # expansion permutation
    P_box: tuple = tuple() # permutation after sbox
    S_split: tuple = tuple() # bit selection for sbox
    S_box: tuple = tuple() # list of sboxes

    def __init__(self, key: bytes = None):
        self.keys = []
        self.state = [ 0 ] * (self.__class__.blocksize * 8)
        self.set_key(key)

    def __call__(self, x: bytes):
        if isinstance(x, bytes|bytearray) and len(x) == self.__class__.blocksize:
            s = int.from_bytes(x, byteorder="big")
            self.state = [int(d) for d in str(format(s, "0" + str(self.__class__.blocksize * 8) + "b"))]
        else:
            raise ValueError(f"Plaintext must be {self.__class__.blocksize} bytes.")
        return self

    def __repr__(self):
        if self.__class__.print_hex:
            return str(format(int(self), "0" + str(self.__class__.blocksize * 2) + "x"))
        s = ''
        for i, d in enumerate(self.state):
            if not i % 8 and 0 < i < self.__class__.blocksize * 8:
                s += ' '
            s += str(d)
        return s

    def __int__(self):
        s = 0
        for i, d in enumerate(reversed(self.state)):
            if d:
                s += 1 << i
        return s

    def __bytes__(self):
        return int(self).to_bytes(self.__class__.blocksize, byteorder="big")

    def set_key(self, key: bytes):
        "Set a new key."
        if key is not None:
            self.keys = self.__class__.key_schedule(key).gen_keys()

    def xor(self, a: list[int], b: list[int]) -> list[int]:
        "XOR two lists"
        return [ i ^ j for i, j in zip(a,b)]

    def left(self) -> list[int]:
        "Left halve"
        return self.state[:self.__class__.blocksize * 4]

    def right(self) -> list[int]:
        "Right halve"
        return self.state[self.__class__.blocksize * 4:]

    def theta(self) -> None:
        "Switch left and right halves"
        self.state = self.right() + self.left()

    def f_box(self, a: list[int], key: list[int], showtmp:bool = False) -> list[int]:
        "Nonlinear f-box"
        if showtmp:
            def printtmp(title: str, a: list) -> None:
                print(f'{title}: {"".join(map(str,a))}')
        else:
            def printtmp(title: str, a: list) -> None:  # pylint: disable=W0613
                pass
        a = permute(a, self.__class__.E_box)  # expansion box
        printtmp("EBox", a)
        a = self.xor(a, key)  # add key
        printtmp("XKey", a)
        split = len(self.__class__.S_split)
        # apply sboxes
        num_sbox = len(self.__class__.S_box)  # number of sboxes
        out_len = self.__class__.blocksize * 4 // num_sbox  # output length of one sbox
        aa = []
        for i in range(num_sbox):
            part = a[i*split:(i+1) * split]
            index = 0
            for k, j in enumerate(reversed(self.__class__.S_split)):
                index += part[j-1] * (1 << k)
            s = self.__class__.S_box[i][index]
            aa += [int(d) for d in str(format(s, "0" + str(out_len) + "b"))]
        a = aa
        printtmp("SBox", a)
        a = permute(a, self.__class__.P_box) # permutation box
        printtmp("PBox", a)
        return a

    def ip(self) -> None:
        "Apply the initial permutation."
        self.state = permute(self.state, self.__class__.IP)

    def fp(self) -> None:
        "Apply the final permutation."
        self.state = permute(self.state, self.__class__.FP)

    def round(self, key: list[int], last: bool = False) -> None:
        "Apply the round function F."
        if last:
            self.state = self.xor(self.f_box(self.right(), key), self.left()) + self.right()
        else:
            self.state = self.right() + self.xor(self.f_box(self.right(), key), self.left())

    def encrypt(self, x: bytes = None) -> bytes:
        "Do a full encryption of a given block (or the current state)."
        if x is not None:
            self(x)
        self.ip()
        for k in self.keys[:-1]:
            self.round(k)
        self.round(self.keys[-1], last=True)
        self.fp()
        return bytes(self)

    def decrypt(self, x: bytes = None) -> bytes:
        "Do a full decryption of a given block (or the current state)."
        if x is not None:
            self(x)
        self.ip()
        for k in reversed(self.keys[1:]):
            self.round(k)
        self.round(self.keys[0], last=True)
        self.fp()
        return bytes(self)

# Paramters for S-DES

class SDESKeySchedule(FeistelKeySchedule):
    "S-DES key schedule"

    keylength: int = 10 # in bit; must be even
    print_hex = False
    IP = (3, 5, 2, 7, 4, 10, 1, 9, 8, 6)
    CP = (6, 3, 7, 4, 8, 5, 10, 9)
    ROT = (1, 2)

class SDESCipher(FeistelCipher):
    "S-DES"

    blocksize: int = 1 # in bytes
    print_hex = False
    key_schedule = SDESKeySchedule
    IP = (2, 6, 3, 1, 4, 8, 5, 7)
    FP = (4, 1, 3, 5, 7, 2, 8, 6)
    E_box = (4, 1, 2, 3, 2, 3, 4, 1)
    P_box = (2, 4, 3, 1)
    S_split = (1, 4, 2, 3)
    S_box = (
        (1, 0, 3, 2, 3, 2, 1, 0, 0, 2, 1, 3, 3, 1, 3, 2),
        (0, 1, 2, 3, 2, 0, 1, 3, 3, 0, 1, 0, 2, 1, 0, 3)
    )

# Paramters for DES

class DESKeySchedule(FeistelKeySchedule):
    "DES key schedule"
    keylength: int = 64 # in bit; must be even
    print_hex = True
    IP = (57, 49, 41, 33, 25, 17,  9,
           1, 58, 50, 42, 34, 26, 18,
          10,  2, 59, 51, 43, 35, 27,
          19, 11,  3, 60, 52, 44, 36,
          63, 55, 47, 39, 31, 23, 15,
           7, 62, 54, 46, 38, 30, 22,
          14,  6, 61, 53, 45, 37, 29,
          21, 13,  5, 28, 20, 12,  4)
    CP = (14, 17, 11, 24,  1,  5,
           3, 28, 15,  6, 21, 10,
          23, 19, 12,  4, 26,  8,
          16,  7, 27, 20, 13,  2,
          41, 52, 31, 37, 47, 55,
          30, 40, 51, 45, 33, 48,
          44, 49, 39, 56, 34, 53,
          46, 42, 50, 36, 29, 32)
    ROT = (1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1)

class DESCipher(FeistelCipher):
    "DES"
    blocksize: int = 8 # in bytes
    print_hex = True
    key_schedule = DESKeySchedule
    IP = (58, 50, 42, 34, 26, 18, 10, 2,
          60, 52, 44, 36, 28, 20, 12, 4,
          62, 54, 46, 38, 30, 22, 14, 6,
          64, 56, 48, 40, 32, 24, 16, 8,
          57, 49, 41, 33, 25, 17, 9, 1,
          59, 51, 43, 35, 27, 19, 11, 3,
          61, 53, 45, 37, 29, 21, 13, 5,
          63, 55, 47, 39, 31, 23, 15, 7)
    FP = (40, 8, 48, 16, 56, 24, 64, 32,
          39, 7, 47, 15, 55, 23, 63, 31,
          38, 6, 46, 14, 54, 22, 62, 30,
          37, 5, 45, 13, 53, 21, 61, 29,
          36, 4, 44, 12, 52, 20, 60, 28,
          35, 3, 43, 11, 51, 19, 59, 27,
          34, 2, 42, 10, 50, 18, 58, 26,
          33, 1, 41, 9, 49, 17, 57, 25)
    E_box = (32, 1, 2, 3, 4, 5,
             4, 5, 6, 7, 8, 9,
             8, 9, 10, 11, 12, 13,
             12, 13, 14, 15, 16, 17,
             16, 17, 18, 19, 20, 21,
             20, 21, 22, 23, 24, 25,
             24, 25, 26, 27, 28, 29,
             28, 29, 30, 31, 32, 1)
    P_box = (16, 7, 20, 21, 29, 12, 28, 17,
             1, 15, 23, 26, 5, 18, 31, 10,
             2, 8, 24, 14, 32, 27, 3, 9,
             19, 13, 30, 6, 22, 11, 4, 25)
    S_split = (1, 6, 2, 3, 4, 5)
    S_box = (
        (14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
             0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
             4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
             15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13),
        (15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
             3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
             0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
             13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9),
        (10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
             13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
             13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
             1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12),
        (7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
             13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
             10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
             3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14),
        (2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
             14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
             4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
             11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3),
        (12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
             10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
             9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
             4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13),
        (4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
             13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
             1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
             6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12),
        (13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
             1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
             7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
             2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11)
    )


class DESBlockCipher(BlockCipher):
    "Block cipher class for DES"
    blocksize = 8
    def set_key(self, key: bytes):
        if not isinstance(key, bytes) and len(key) != self.__class__.blocksize:
            raise ValueError(f"Key must be {self.__class__.blocksize} bytes.")
        self.key = key
        self.cipher = DESCipher(key)
