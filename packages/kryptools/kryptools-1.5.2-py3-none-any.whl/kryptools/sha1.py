"""
SHA1
"""


class SHA1:
    "SHA1 Hash function"

    h_init = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)

    def __init__(self):
        pass

    def __call__(self, message: bytes | str, h_init: list = h_init, length: int = None) -> int:
        return self.hash(message, h_init, length)

    def left_rotate(self, w: int, n: int) -> int:
        """Left rotate a 32-bit integer w by n bits."""
        return ((w << n) | (w >> (32 - n))) & 0xffffffff

    def pad(self, msg: bytes, length: int = None) -> bytes:
        """Pad a message. Optionally augment the message length."""
        msg = bytearray(msg)
        l = len(msg)
        if length:
            l += length
        # append 1 plus zeros such that the length % 64 = 56
        msg += b'\x80'+b'\x00'*((55 - l) % 64)
        # add the bit length of the message
        msg += int(l*8).to_bytes(8, byteorder='big')
        return bytes(msg)

    def compression_function(self, h: list, chunk: bytes) -> list:
        """Process a chunk of data and return the new digest variables."""
        assert len(chunk) == 64, "Chunk must be 64 bytes."

        w = [0] * 80

        # Break chunk into sixteen 4-byte big-endian words w[i]
        for i in range(16):
            w[i] = int.from_bytes(chunk[i * 4:(i+1) * 4], byteorder='big')

        # Message schedule: extend the sixteen 32-bit words into eighty 32-bit words
        for i in range(16, 80):
            # Note: SHA-0 differs by not having this leftrotate
            w[i] = self.left_rotate(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1)

        # Initialize hash value for this chunk
        a, b, c, d, e = h

        for i in range(80):
            if 0 <= i <= 19:
                # Use alternative 1 for f from FIPS PB 180-1 to avoid bitwise not
                f = d ^ (b & (c ^ d))
                k = 0x5A827999
            elif 20 <= i <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            elif 60 <= i <= 79:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            a, b, c, d, e = ((self.left_rotate(a, 5) + f + e + k + w[i]) & 0xffffffff, a, self.left_rotate(b, 30), c, d)  # pylint: disable=E0606

        # Add this chunk's hash to result so far
        h0 = (h[0] + a) & 0xffffffff
        h1 = (h[1] + b) & 0xffffffff
        h2 = (h[2] + c) & 0xffffffff
        h3 = (h[3] + d) & 0xffffffff
        h4 = (h[4] + e) & 0xffffffff

        return [h0, h1, h2, h3, h4]

    def hash(self, message: bytes | str, h_init: list = h_init, length: int = None) -> int:
        """
        Computes SHA1 of a given message.
        Optinally the initial hash can be given and the length of the message can be augmented.
        """
        if isinstance(message, str):
            message = message.encode()
        message = self.pad(message, length)
        h = h_init  # initialize the status
        for i in range(0, len(message), 64):
            h = self.compression_function(h, message[i:i+64])
        # return (h[0] << 128) | (h[1] << 96) | (h[2] << 64) | (h[3] << 32) | h[4]
        return b''.join(map(lambda n: int.to_bytes(n, 4, byteorder='big'), h))
