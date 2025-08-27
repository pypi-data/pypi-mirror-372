"""
Generic class for a block cipher.
"""

from secrets import token_bytes as randbytes

def bytexor(a: bytes, b: bytes) -> bytes:
    "Xor two byte strings."
    return bytes([x ^ y for (x, y) in zip(a, b)])

class BlockCipher:
    "Generic class for a block cipher."

    blocksize: int = 1 # blocksize in bytes

    def __init__(self, key: bytes|int = None, mode: str|None = None):
        self.key = None  # here we store the key (if any)
        self.cipher = None  # here we can store an instance of the cipher initialized with the key
        self.mode = mode # here we store the default en/decryption mode
        if key:
            self.set_key(key)

    def set_key(self, key: bytes|int):
        "Store a new key and initialize the cipher with this key."
        if key is not None:
            if isinstance(key, bytes) and len(key) != self.__class__.blocksize:
                raise ValueError(f"Key must be {self.__class__.blocksize} bytes.")
            self.key = key

    def encrypt_block(self, b: bytes) -> bytes:
        "Decrypt one block."
        return self.cipher.encrypt(b)

    def decrypt_block(self, b: bytes) -> bytes:
        "Encrypt one block."
        return self.cipher.decrypt(b)

    def blocksplit(self, text: bytes, padding: bool):
        "Split a byte string according to the blocksize. Pad (PKCS#7) if requested."
        if padding and self.__class__.blocksize > 1:  # padding according to PKCS#7
            pad = -len(text) % self.__class__.blocksize
            if pad == 0:
                pad = self.__class__.blocksize
            text = bytearray(text)
            text.extend([pad]*pad)  # pad
            text = bytes(text)
        return [text[i:i+self.__class__.blocksize] for i in range(0, len(text), self.__class__.blocksize)]

    def encrypt(self, text: bytes, key: bytes|int|None=None, mode=None):
        "Encrypt using the given mode."
        if mode is None:
            mode = self.mode
        if hasattr(self, "encrypt_" + mode.lower()):
            method = getattr(self, "encrypt_" + mode.lower())
        else:
            raise ValueError("Unsupported encryption mode: ", mode)
        if key:
            self.set_key(key)
        return method(text)

    def decrypt(self, ctext: bytes, key: bytes|int|None=None, mode=None):
        "Decrypt using the given mode."
        if mode is None:
            mode = self.mode
        if hasattr(self, "decrypt_" + mode):
            method = getattr(self, "decrypt_" + mode)
        else:
            raise ValueError("Unsupported encryption mode: ", mode)
        if key:
            self.set_key(key)
        return method(ctext)

    def encrypt_ecb(self, text: bytes, padding: bool = True) -> bytes:
        "Encrypt using ECB mode."
        ctext = bytearray(b'')
        for b in self.blocksplit(text, padding):
            ctext.extend(self.encrypt_block(b))
        return bytes(ctext)

    def decrypt_ecb(self, ctext: bytes, padding: bool = True) -> bytes:
        "Decrypt using ECB mode."
        text = bytearray(b'')
        for b in self.blocksplit(ctext, False):
            text.extend(self.decrypt_block(b))
        if padding and self.__class__.blocksize > 1:
            return bytes(text[:-text[-1]])  # unpad
        return bytes(text)

    def encrypt_cbc(self, text: bytes, iv: bytes | None = None, padding: bool = True) -> bytes:
        "Encrypt using CBC mode."
        ctext = bytearray(b'')
        if iv is None:
            bb = randbytes(self.__class__.blocksize)  # iv
        else:
            bb = iv
        ctext.extend(bb)
        for b in self.blocksplit(text, padding):
            bb = self.encrypt_block(bytexor(bb, b))
            ctext.extend(bb)
        return bytes(ctext)

    def decrypt_cbc(self, ctext: bytes, padding: bool = True) -> bytes:
        "Decrypt using CBC mode."
        text = bytearray(b'')
        bb = ctext[:self.__class__.blocksize]  # iv
        ctext = ctext[self.__class__.blocksize:]  # remove iv
        for b in self.blocksplit(ctext, False):
            text.extend(bytexor(bb, self.decrypt_block(b)))
            bb = b
        if padding and self.__class__.blocksize > 1:
            return bytes(text[:-text[-1]])  # unpad
        return bytes(text)

    def encrypt_cfb(self, text: bytes, iv: bytes | None = None) -> bytes:
        "Encrypt using CFB mode."
        ctext = bytearray(b'')
        if iv is None:
            bb = randbytes(self.__class__.blocksize)  # iv
        else:
            bb = iv
        ctext.extend(bb)  # add iv as first block of the cipher text
        for b in self.blocksplit(text, False):
            z = self.encrypt_block(bb)
            bb = bytexor(b, z)
            ctext.extend(bb)
        return bytes(ctext)

    def decrypt_cfb(self, ctext: bytes) -> bytes:
        "Decrypt using CFB mode."
        text = bytearray(b'')
        bb = ctext[:self.__class__.blocksize]  # iv
        ctext = ctext[self.__class__.blocksize:]  # remove iv
        for b in self.blocksplit(ctext, False):
            z = self.encrypt_block(bb)
            text.extend(bytexor(b, z))
            bb = b
        return bytes(text)

    def encrypt_ofb(self, text: bytes, iv: bytes | None = None) -> bytes:
        "Encrypt using OFB mode."
        ctext = bytearray(b'')
        if iv is None:
            z = randbytes(self.__class__.blocksize)  # iv
        else:
            z = iv
        ctext.extend(z)  # add iv as first block of the cipher text
        for b in self.blocksplit(text, False):
            z = self.encrypt_block(z)
            ctext.extend(bytexor(b, z))
        return bytes(ctext)

    def decrypt_ofb(self, ctext: bytes) -> bytes:
        "Decrypt using OFB mode."
        text = bytearray(b'')
        z = ctext[:self.__class__.blocksize]  # iv
        ctext = ctext[self.__class__.blocksize:]  # remove iv
        for b in self.blocksplit(ctext, False):
            z = self.encrypt_block(z)
            text.extend(bytexor(b, z))
        return bytes(text)

    def adv_ctr(self, z: bytes, s: int) -> bytes:
        "Advance the counter."
        zz = bytearray(z)
        for i in range(self.__class__.blocksize-1, self.__class__.blocksize-s-1, -1):
            c = z[i]+1
            if c < 256:
                zz[i] = c
                break
            zz[i] = 0
        return zz

    def encrypt_ctr(self, text: bytes, iv: bytes | None = None) -> bytes:
        "Encrypt using CTR mode."
        ctext = bytearray(b'')
        if iv is None:
            ctr = randbytes(self.__class__.blocksize)  # iv
        else:
            ctr = iv
        ctext.extend(ctr)  # add iv as first block of the cipher text
        for b in self.blocksplit(text, False):
            z = self.encrypt_block(ctr)
            ctext.extend(bytexor(b, z))
            ctr = self.adv_ctr(ctr, self.__class__.blocksize)
        return bytes(ctext)

    def decrypt_ctr(self, ctext: bytes) -> bytes:
        "Decrypt using CTR mode."
        text = bytearray(b'')
        ctr = ctext[:self.__class__.blocksize]  # iv
        ctext = ctext[self.__class__.blocksize:]  # remove iv
        for b in self.blocksplit(ctext, False):
            z = self.encrypt_block(ctr)
            text.extend(bytexor(b, z))
            ctr = self.adv_ctr(ctr, self.__class__.blocksize)
        return bytes(text)

    def mac_cbc(self, text: bytes, padding: bool = True) -> bytes:
        "CBC-MAC of a bytestring."
        bb = b'\x00' * self.__class__.blocksize
        for b in self.blocksplit(text, padding = padding):
            bb = self.encrypt_block(bytexor(bb, b))
        return bytes(bb)

    def mac_cmac(self, text: bytes) -> bytes:
        "CMAC of a bytestring."
        R_b = {16: 0b10000111, 8: 0b11011, 4: 0b10001101,
               2: 0b101011, 1: 0b11011}[self.__class__.blocksize]

        bb = b'\x00' * self.__class__.blocksize
        # Compute key K1
        key_extra = self.encrypt_block(bb)
        key_extra = int.from_bytes(key_extra, byteorder='big')
        msb = key_extra >> (self.__class__.blocksize * 8 - 1)
        key_extra <<= 1
        if msb:
            key_extra ^= 1 << self.__class__.blocksize * 8
            key_extra ^= R_b

        pad = len(text) % self.__class__.blocksize
        if pad or not text:
            # Compute key K2
            text += b'\x80' + b'\x00' * (self.__class__.blocksize - pad - 1)
            msb = key_extra >> (self.__class__.blocksize * 8 - 1)
            key_extra <<= 1
            if msb:
                key_extra ^= 1 << self.__class__.blocksize * 8
                key_extra ^= R_b
        key_extra = key_extra.to_bytes(self.__class__.blocksize, byteorder='big')  # K1 or K2 depending on padding
        last_block = bytexor(text[-self.__class__.blocksize:], key_extra)  # Xor extra key to the last block
        text = text[:-self.__class__.blocksize] + last_block
        for i in range(0, len(text), self.__class__.blocksize):
            bb = self.encrypt_block(bytexor(bb, text[i:i+self.__class__.blocksize]))
        return bytes(bb)

    def gf_mult(self, x: int, y: int) -> int:
        "Muliplication in GF(2^128)."
        # r = 0b11011 << 27  # 1 + x + x^3 + x^4 (+ x^32)
        # r = 0b11100001 << 56  # 1 + x + x^2 + x^7 (+ x^64)
        r = 0b11100001 << 120  # 1 + x + x^2 + x^7 (+ x^128)
        z = 0
        v = y
        for d in bin(x)[2:].zfill(128):
            if int(d):
                z ^= v
            if v % 2:
                v >>= 1
                v ^= r
            else:
                v >>= 1
        return z

    def ghash(self, text: bytes, h: int, init: int = 0) -> bytes:
        "Compute GHASH of a given byte string."
        assert self.__class__.blocksize == 16, "GCTR mode requires a blocksize of 128 bit."
        pad = len(text) % self.__class__.blocksize
        if pad > 0:
            text += b"\x00" * (self.__class__.blocksize - pad)
        y = init
        for i in range(len(text) // self.__class__.blocksize):
            x = int.from_bytes(
                text[i * self.__class__.blocksize: (i + 1) * self.__class__.blocksize], byteorder="big")
            y = self.gf_mult(h, x ^ y)
        return y

    def _aad_helper(self, len_text:int, aad: bytes | None):
        "Compute the tag for the additional authenticated data."
        zero = b'\x00' * self.__class__.blocksize
        h = int.from_bytes(self.encrypt_block(zero), byteorder="big")
        len_text *= 8
        assert len_text.bit_length() <= 4 * self.__class__.blocksize, "Message too long!"
        len_block = len_text.to_bytes((self.__class__.blocksize // 2), byteorder="big")
        if aad is not None:
            len_aad = len(aad) * 8
            assert len_aad.bit_length() <= 4 * self.__class__.blocksize, "Additional authenticated data too long!"
            len_block = len_aad.to_bytes(
                (self.__class__.blocksize // 2), byteorder="big") + len_block
            tag = self.ghash(aad, h)
        else:
            len_block = b'\x00' * (self.__class__.blocksize // 2) + len_block
            tag = 0
        return h, len_block, tag


    def encrypt_gcm(self, text: bytes, iv: bytes | None = None, aad: bytes | None = None) -> bytes:
        "Encrypt using Galois CTR mode."
        assert self.__class__.blocksize == 16, "GHASH requires a blocksize of 16 bytes."
        ctext = bytearray(b'')
        len_ctr = self.__class__.blocksize // 4
        if iv is None:
            iv = randbytes(self.__class__.blocksize - len_ctr)
        else:
            assert len(iv) + \
                len_ctr == self.__class__.blocksize, "IV has inappropriate length!"
        ctr = iv + (len_ctr - 1) * b'\x00' + b'\x01'
        ctr0 = ctr
        ctext.extend(iv)
        h, len_block, tag = self._aad_helper(len(text), aad)
        for b in self.blocksplit(text, 0):
            ctr = self.adv_ctr(ctr, len_ctr)
            z = self.encrypt_block(ctr)
            ctext.extend(bytexor(b, z))
        tag = self.ghash(ctext[self.__class__.blocksize - len_ctr:], h, init=tag)
        tag = self.ghash(len_block, h, init=tag).to_bytes(
            self.__class__.blocksize, byteorder="big")
        z = self.encrypt_block(ctr0)
        ctext.extend(bytexor(tag, z))
        return bytes(ctext)

    def decrypt_gcm(self, ctext: bytes, aad: bytes | None = None) -> bytes:
        "Decrypt using Galois CTR mode."
        assert self.__class__.blocksize == 16, "GHASH requires a blocksize of 16 bytes."
        text = bytearray(b'')
        len_ctr = self.__class__.blocksize // 4
        iv = ctext[:self.__class__.blocksize - len_ctr]  # iv
        ctr = iv + (len_ctr - 1) * b'\x00' + b'\x01'
        mac = ctext[-self.__class__.blocksize:]  # mac
        ctext = ctext[self.__class__.blocksize - len_ctr:-self.__class__.blocksize]
        h, len_block, tag = self._aad_helper(len(ctext), aad)
        tag = self.ghash(ctext, h, init=tag)
        tag = self.ghash(len_block, h, init=tag).to_bytes(
            self.__class__.blocksize, byteorder="big")
        z = self.encrypt_block(ctr)
        tag = bytexor(tag, z)
        assert tag == mac, "Incorrect MAC!"
        for b in self.blocksplit(ctext, 0):
            ctr = self.adv_ctr(ctr, len_ctr)
            z = self.encrypt_block(ctr)
            text.extend(bytexor(b, z))
        return bytes(text)
