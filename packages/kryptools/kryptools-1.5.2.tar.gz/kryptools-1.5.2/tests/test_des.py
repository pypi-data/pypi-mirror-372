# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from kryptools import SDESKeySchedule, SDESCipher, DESKeySchedule, DESCipher, list2int


def test_SDES():
    # Test the key schedule
    key = 34
    test_values = [[0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0]]

    ks = SDESKeySchedule(key)
    assert ks.gen_keys() == test_values

    # Test the encryption
    x = b'\x01'
    y = b'\xb9'

    sdes = SDESCipher(key)
    sdes(x).encrypt()
    assert bytes(sdes) == y
    assert sdes.decrypt() == x


def test_DES():
    # Test the key schedule
    key = 0x0123456789ABCDEF.to_bytes(8, 'big')
    test_values = [0x0B02679B49A5, 0x69A659256A26, 0x45D48AB428D2, 0x7289D2A58257, 0x3CE80317A6C2, 0x23251E3C8545, 0x6C04950AE4C6, 0x5788386CE581,
                   0xC0C9E926B839, 0x91E307631D72, 0x211F830D893A, 0x7130E5455C54, 0x91C4D04980FC, 0x5443B681DC8D, 0xB691050A16B5, 0xCA3D03B87032]

    ks = DESKeySchedule(key)
    keys = ks.gen_keys()
    for k1, k2 in zip(keys, test_values):
        assert list2int(k1) == k2

    # Test the encryption (Handbook of Applied Cryptography and NBS Special Publication 500-20)
    test_values = [[ 0x0123456789ABCDEF, 0x4E6F772069732074, 0x3FA40E8A984D4815 ],
        [0x10316E028C8F3B4A, 0x0000000000000000, 0x82DCBAFBDEAB6602],
        [0x0101010101010101, 0x95F8A5E5DD31D900, 0x8000000000000000],
        [0x0101010101010101, 0xDD7F121CA5015619, 0x4000000000000000],
        [0x0101010101010101, 0x2E8653104F3834EA, 0x2000000000000000],
        [0x0101010101010101, 0x4BD388FF6CD81D4F, 0x1000000000000000],
        [0x0101010101010101, 0x20B9E767B2FB1456, 0x0800000000000000],
        [0x0101010101010101, 0x8000000000000000, 0x95F8A5E5DD31D900],
        [0x0101010101010101, 0x4000000000000000, 0xDD7F121CA5015619],
        [0x0101010101010101, 0x2000000000000000, 0x2E8653104F3834EA],
        [0x0101010101010101, 0x1000000000000000, 0x4BD388FF6CD81D4F],
        [0x8001010101010101, 0x0000000000000000, 0x95A8D72813DAA94D],
        [0x4001010101010101, 0x0000000000000000, 0x0EEC1487DD8C26D5],
        [0x2001010101010101, 0x0000000000000000, 0x7AD16FFB79C45926],
        [0x1001010101010101, 0x0000000000000000, 0xD3746294CA6A6CF3]]

    for key, x, y in test_values:
        key = key.to_bytes(8, 'big')
        x = x.to_bytes(8, 'big')
        y = y.to_bytes(8, 'big')

        des = DESCipher(key)
        des(x).encrypt()
        assert bytes(des) == y
        assert des.decrypt() == x
