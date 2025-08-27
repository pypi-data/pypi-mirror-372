"""
Keccak Sponge, SHA3, SHAKE
"""


class Keccak:
    "Keccak sponge"
    MASK_64 = (1 << 64) - 1
    rounds = 24

    def __init__(self, rate: int = 1088):
        if rate % 64:
            raise ValueError(f"Rate {rate} must be a multiple of 64.")
        self.pad = [b'\x81', b'\x01', b'\x80']
        self.rate = rate // 8  # in bytes
        self.state = [0] * 25
        self.lfsr = 1
        self.buffer = b''
        self.rnd_bytes = None

    def reset(self):
        "Reset the state of the sponge."
        self.state = [0] * 25
        self.lfsr = 1
        self.buffer = b''
        self.rnd_bytes = None

    def __repr__(self):
        out = ""
        for i in range(5):
            for j in range(5):
                out += f"{self.state[5 * i + j]:016x}"
                if j < 4:
                    out += " "
            if i < 4:
                out += "\n"
        return out

    def f(self) -> None:
        "Apply f to the state."
        self.lfsr = 1
        for _ in range(Keccak.rounds):
            self.theta()
            self.pi()
            self.rho()
            self.chi()
            self.iota()

    def absorb(self, msg: bytes | str) -> None:
        "Absorbe a message into the state."
        if isinstance(msg, str):
            msg = msg.encode()
        msg = self.buffer + msg
        msg_len = len(msg) - len(msg) % self.rate
        msg, self.buffer = msg[:msg_len], msg[msg_len:]
        for i in range(len(msg)//self.rate):
            self.absorb_block(msg[i*self.rate:(i+1)*self.rate])

    def absorb_block(self, block: bytes) -> None:
        "Absorbe a block into the state. Pad the block if neccessary."

        if len(block) > self.rate:
            raise ValueError(f"Block must be at most {self.rate} bytes.")
        padlen = self.rate - len(block)
        if padlen == 1:
            block += self.pad[0]
        else:
            block += self.pad[1] + (b'\x00' * (padlen - 2)) + self.pad[2]
        for i in range(len(block)//8):
            self.state[i] ^= int.from_bytes(block[i*8:(i+1)*8], 'little')
        self.f()

    def squeeze(self, r: int) -> bytes:
        "Squeesze out 'r' bytes from the state."
        if r < 0:
            raise ValueError("Number of bytes must be positive.")
        if self.rnd_bytes is None:
            self.absorb_block(self.buffer)
            self.rnd_bytes = self.extract_block()
        while r > len(self.rnd_bytes):
            self.f()
            self.rnd_bytes += self.extract_block()
        out, self.rnd_bytes = self.rnd_bytes[:r], self.rnd_bytes[r:]
        return out

    def extract_block(self) -> bytes:
        "Extract one block from the state."
        out = b''
        for i in range(self.rate//8):
            out += self.state[i].to_bytes(8, 'little')
        return out

    def left_rotate(self, w: int, n: int) -> int:
        "Left rotate a 64-bit integer w by n bits."
        return ((w << n) & Keccak.MASK_64) | (w >> (64 - n))

    def theta(self) -> None:
        "Apply Theta to the state."
        v = [0] * 5
        for j in range(5):
            for i in range(5):
                v[j] ^= self.state[5 * i + j]

        for j in range(5):
            h = v[(j + 4) % 5] ^ self.left_rotate(v[(j + 1) % 5], 1)
            for i in range(5):
                self.state[5 * i + j] ^= h

    def pi(self) -> None:
        "Apply Pi to the state."
        i, j = 0, 1

        for t in range(1, 25):
            idx = 5 * i + j
            w = (t * (t + 1) // 2) % 64
            self.state[idx] = self.left_rotate(self.state[idx], w)
            i, j = (3 * i + 2 * j) % 5, i

    def rho(self) -> None:
        "Apply Rho to the state."
        i, j = 0, 1
        vv = self.state[1]

        for _ in range(24):
            i, j = (3 * i + 2 * j) % 5, i
            idx = 5 * i + j
            self.state[idx], vv = vv, self.state[idx]

    def chi(self) -> None:
        "Apply Chi to the state."
        v = [0] * 5

        for i in range(0, 25, 5):
            for j in range(5):
                v[j] = self.state[i + j]
            for j in range(5):
                self.state[i + j] ^= (v[(j + 1) % 5] ^
                                      Keccak.MASK_64) & v[(j + 2) % 5]

    def iota(self) -> None:
        "Apply Iota to the state."
        for w in [0, 1, 3, 7, 15, 31, 63]:
            self.state[0] ^= ((self.lfsr & 1) << w)
            self.lfsr <<= 1
            self.lfsr &= Keccak.MASK_64
            if self.lfsr & 0x100:
                self.lfsr ^= 0x171


class SHA3():
    """
    SHA3 secure hash algorithm

    Example:

    >>>sha3 = SHA3(256)
    >>>sha3("abc").hex()
    '3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532'
    """

    def __init__(self, n: int = 256):
        if n not in (224, 256, 384, 512):
            raise ValueError("n must be one of: 224, 256, 384, 512")
        self.keccak = Keccak(rate = 1600 - 2*n)
        self.keccak.pad = [b'\x86', b'\x06', b'\x80']
        self.digest_size = n // 8  # in bytes
        self.block_size = (1600 - 2*n) // 8  # in bytes
        self.name = f"SHA3-{n}"

    def __call__(self, msg: bytes | str) -> bytes:
        "Compute the hash of the message given or absorbed."
        self.keccak.reset()
        self.keccak.absorb(msg)
        return self.keccak.squeeze(self.digest_size)

    def __repr__(self):
        return self.name

    def update(self, msg: bytes | str) -> None:
        "Absorb the given message into the sponge."
        self.keccak.absorb(msg)

    def digest(self, msg: bytes | str | None = None) -> bytes:
        "Compute the hash of the message given or absorbed."
        if msg is not None:
            self.keccak.absorb(msg)
        digest = self.keccak.squeeze(self.digest_size)
        self.keccak.reset()
        return digest

    def hexdigest(self, msg: bytes | str | None = None) -> bytes:
        "Compute the hash of the message given or absorbed. Return as hex value."
        return self.digest(msg).hex()


class SHAKE():
    """
    SHAKE Extendable output function

    Example:

    >>> shake = SHAKE(b'secret', n = 128)
    >>> shake(8)
    b'O:dn&\\xb2i>'
    """

    def __init__(self, msg: bytes | str, n: int = 128) -> None:
        if n not in (128, 256):
            raise ValueError("n must be one of: 128, 256")
        self.keccak = Keccak(rate=1600-2*n)
        self.keccak.pad = [b'\x9f', b'\x1f', b'\x80']
        self.keccak.absorb(msg)
        self.name = f"SHAKE-{n}"

    def __repr__(self):
        return self.name

    def __call__(self, r: int) -> bytes:
        "Extract `r` bytes."
        return self.keccak.squeeze(r)

    def digest(self, r: int) -> bytes:
        "Extract `r` bytes."
        return self(r)

    def hexdigest(self, r: int) -> bytes:
        "Extract `r` bytes as hex values."
        return self(r).hex()
