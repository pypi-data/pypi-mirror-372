"""
AES cipher
"""

from .GF2 import GF2_aes
from .la import Matrix, zeros
from .blockcipher import BlockCipher


def rotate_left(l: list, n: int) -> list:
    "Rotate a list cyclically n places to the left."
    n %= len(l)
    return l[n:] + l[:n]

aes_mix_matrix = Matrix([ rotate_left([2, 3, 1, 1], -n) for n in range(4) ], ring=GF2_aes)
aes_mix_matrix_inv = aes_mix_matrix.inv()

class AESCipher:
    "AES state matrix"
    def __init__(self, key: bytes = None):
        self.keys = []
        self.state = zeros(4, zero=GF2_aes(0))
        self.set_key(key)

    def __call__(self, s: bytes):
        if isinstance(s, bytes|bytearray) and len(s) == 16:
            self.state = zeros(4)
            for l in range(16):
                i, j = divmod(l, 4)
                self.state[j, i] = GF2_aes(s[l])
        elif isinstance(s, list|tuple) and len(s) == 4:
            self.state = Matrix(s, ring=GF2_aes)
        else:
            raise ValueError("Plaintext must be 16 bytes or 4x4 list of bytes.")
        return self

    def __repr__(self):
        return str(self.state)

    def __bytes__(self):
        tmp = bytearray()
        for i in range(4):
            for j in range(4):
                tmp.append(int(self.state[j, i]))
        return bytes(tmp)

    def set_key(self, key: bytes):
        "Set a new key."
        if key is not None:
            self.keys = AESKeySchedule(key).gen_keys()

    def sub_bytes(self, inv: bool = False) -> None:
        "Apply SubBytes to the state."
        if inv:
            self.state.map(lambda x: x.sbox(inv=True))
        else:
            self.state.map(lambda x: x.sbox())

    def shift_rows(self, inv: bool = False) -> None:
        "Apply ShiftRows to the state."
        if inv:
            inv = -1
        else:
            inv = 1
        for i in range(self.state.rows):
            self.state.matrix[i] = rotate_left(self.state.matrix[i], inv * i)

    def mix_columns(self, inv = False) -> None:
        "Apply MixColumns to the state."
        if inv:
            self.state.matrix = (aes_mix_matrix_inv * self.state).matrix
        else:
            self.state.matrix = (aes_mix_matrix * self.state).matrix

    def add_key(self, key: "Matrix") -> None:
        "Add the key to the state."
        self.state += key

    def round(self, k: "Matrix", last = False, inv = False) -> None:
        "Apply one round to the state."
        if inv:
            self.add_key(k)
            if not last:
                self.mix_columns(inv = True)
            self.shift_rows(inv = True)
            self.sub_bytes(inv = True)
        else:
            self.sub_bytes()
            self.shift_rows()
            if not last:
                self.mix_columns()
            self.add_key(k)

    def encrypt(self, x: bytes = None) -> bytes:
        "Do a full encryption of a given block (or the current state)."
        if x is not None:
            self(x)
        self.add_key(self.keys[0])
        for k in self.keys[1:-1]:
            self.round(k)
        self.round(self.keys[-1], last = True)
        return bytes(self)

    def decrypt(self, x: bytes = None) -> bytes:
        "Do a full decryption of a given block (or the current state)."
        if x is not None:
            self(x)
        self.round(self.keys[-1], last = True, inv = True)
        for k in reversed(self.keys[1:-1]):
            self.round(k, inv = True)
        self.add_key(self.keys[0])
        return bytes(self)


class AESKeySchedule:
    "AES key matrix"
    def __init__(self, key: bytes):
        assert len(key) == 16
        self.round = 0
        self.showtmp = False  # print intermediate results
        if isinstance(key, bytes|bytearray) and len(key) == 16:
            self.key = zeros(4)
            for l in range(16):
                i, j = divmod(l, 4)
                self.key[j, i] = GF2_aes(key[l])
        elif isinstance(key, list|tuple) and len(key) == 4:
            self.key = Matrix(key, ring=GF2_aes)
        else:
            raise NotImplementedError("Object must be 16 bytes or 4x4 list of bytes.")

    def __repr__(self):
        return str(self.key)

    def __bytes__(self):
        tmp = bytearray()
        for i in range(4):
            for j in range(4):
                tmp.append(int(self.key[j, i]))
        return bytes(tmp)

    def next(self) -> None:
        "Apply one round of the key shedule and return the next key."
        self.round += 1
        #RotWord
        tmp = list(self.key[:,3])
        if self.showtmp:
            print("Start    :" + str(tmp))
        tmp = rotate_left(tmp, 1)
        if self.showtmp:
            print("RotWord  :" + str(tmp))
        #SubWord
        tmp = list(map(lambda x: x.sbox(), tmp))
        if self.showtmp:
            print("SubWord  :" + str(tmp))
        #AddRound constant
        tmp[0] += GF2_aes(2)**(self.round - 1)
        if self.showtmp:
            print("AddConst :" + str(tmp))
        tmp = Matrix(tmp)
        self.key[:,0] += tmp
        self.key[:,1] += self.key[:,0]
        self.key[:,2] += self.key[:,1]
        self.key[:,3] += self.key[:,2]

    def gen_keys(self) -> list:
        "Generate all round keys."
        if self.round:
            raise ValueError('Some keys have already been generated!')
        keys = [ GF2_aes(1) * self.key ]  # we multiply with one to get a copy
        for _ in range(10):
            self.next()
            keys.append(GF2_aes(1) * self.key)
        return keys

class AESBlockCipher(BlockCipher):
    "Block cipher class for AES"
    blocksize = 16
    def set_key(self, key: bytes):
        if not isinstance(key, bytes) and len(key) != self.__class__.blocksize:
            raise ValueError(f"Key must be {self.__class__.blocksize} bytes.")
        self.key = key
        self.cipher = AESCipher(key)
