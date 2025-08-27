# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611

from kryptools import SHA1


# tests from https://csrc.nist.gov/csrc/media/projects/cryptographic-standards-and-guidelines/documents/examples/sha_all.pdf

test_vectors = [
[b'abc', 0xA9993E364706816ABA3E25717850C26C9CD0D89D ],
[b'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq', 0x84983E441C3BD26EBAAE4AA1F95129E5E54670F1]
]

def test_sha1():
    sha1 = SHA1()
    for msg, digest in test_vectors:
        assert int.from_bytes(sha1(msg), byteorder='big') == digest
