# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611
from kryptools import AESBlockCipher


def test_AES():
    aes = AESBlockCipher()

    # AES-128-ECB
    k = bytes.fromhex('2B7E151628AED2A6ABF7158809CF4F3C')
    m = bytes.fromhex('6BC1BEE22E409F96E93D7E117393172A')
    c = bytes.fromhex('3AD77BB40D7A3660A89ECAF32466EF97')

    aes.set_key(k)
    res = aes.encrypt_ecb(m, padding=False)
    assert res == c
    assert aes.decrypt_ecb(res, padding=False) == m

    res = aes.encrypt_ecb(m)
    assert aes.decrypt_ecb(res) == m

    # AES-128-CBC
    k = bytes.fromhex('2B7E151628AED2A6ABF7158809CF4F3C')
    iv = bytes.fromhex('000102030405060708090A0B0C0D0E0F')
    m = bytes.fromhex('6BC1BEE22E409F96E93D7E117393172A')
    c = bytes.fromhex('7649ABAC8119B246CEE98E9B12E9197D')

    aes.set_key(k)
    res = aes.encrypt_cbc(m, iv=iv, padding=False)
    assert res[16:] == c
    assert aes.decrypt_cbc(res, padding=False) == m

    res = aes.encrypt_cbc(m, iv=iv)
    assert aes.decrypt_cbc(res) == m

    # AES-128-OFB
    k = bytes.fromhex('2B7E151628AED2A6ABF7158809CF4F3C')
    iv = bytes.fromhex('000102030405060708090A0B0C0D0E0F')
    m = bytes.fromhex('6BC1BEE22E409F96E93D7E117393172A')
    c = bytes.fromhex('3B3FD92EB72DAD20333449F8E83CFB4A')

    aes.set_key(k)
    res = aes.encrypt_ofb(m, iv=iv)
    assert res[16:] == c
    assert aes.decrypt_ofb(res) == m

    # AES-128-CTR
    k = bytes.fromhex('AE6852F8121067CC4BF7A5765577F39E')
    iv = bytes.fromhex('00000030000000000000000000000001')
    m = bytes.fromhex('53696E676C6520626C6F636B206D7367')
    c = bytes.fromhex('E4095D4FB7A7B3792D6175A3261311B8')

    aes.set_key(k)
    res = aes.encrypt_ctr(m, iv=iv)
    assert res[16:] == c
    assert aes.decrypt_ctr(res) == m

    k = bytes.fromhex('7691BE035E5020A8AC6E618529F9A0DC')
    iv = bytes.fromhex('00E0017B27777F3F4A1786F000000001')
    m = bytes.fromhex(
        '000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F20212223')
    c = bytes.fromhex(
        'C1CF48A89F2FFDD9CF4652E9EFDB72D74540A42BDE6D7836D59A5CEAAEF3105325B2072F')

    aes.set_key(k)
    res = aes.encrypt_ctr(m, iv=iv)
    assert res[16:] == c
    assert aes.decrypt_ctr(res) == m

    # AES-128-GCM
    k = bytes.fromhex('00000000000000000000000000000000')
    iv = bytes.fromhex('000000000000000000000000')
    m = b''
    c = b''
    aad = b''
    mac = bytes.fromhex('58e2fccefa7e3061367f1d57a4e7455a')

    aes.set_key(k)
    res = aes.encrypt_gcm(m, aad=aad, iv=iv)
    assert res[12:-16] == c and res[-16:] == mac
    assert aes.decrypt_gcm(res, aad=aad) == m

    k = bytes.fromhex('00000000000000000000000000000000')
    iv = bytes.fromhex('000000000000000000000000')
    m = bytes.fromhex('00000000000000000000000000000000')
    c = bytes.fromhex('0388dace60b6a392f328c2b971b2fe78')
    aad = b''
    mac = bytes.fromhex('ab6e47d42cec13bdf53a67b21257bddf')

    aes.set_key(k)
    res = aes.encrypt_gcm(m, aad=aad, iv=iv)
    assert res[12:-16] == c and res[-16:] == mac
    assert aes.decrypt_gcm(res, aad=aad) == m

    k = bytes.fromhex('AD7A2BD03EAC835A6F620FDCB506B345')
    iv = bytes.fromhex('12153524C0895E81B2C28465')
    m = b''
    c = b''
    aad = bytes.fromhex(
        'D609B1F056637A0D46DF998D88E5222AB2C2846512153524C0895E8108000F101112131415161718191A1B1C1D1E1F202122232425262728292A2B2C2D2E2F30313233340001')
    mac = bytes.fromhex('f09478a9b09007d06f46e9b6a1da25dd')

    aes.set_key(k)
    res = aes.encrypt_gcm(m, aad=aad, iv=iv)
    assert res[12:-16] == c and res[-16:] == mac

    k = bytes.fromhex('00000000000000000000000000000000')
    iv = bytes.fromhex('000000000000000000000000')
    m = b''
    c = b''
    aad = b''
    mac = bytes.fromhex('58e2fccefa7e3061367f1d57a4e7455a')

    aes.set_key(k)
    res = aes.encrypt_gcm(m, aad=aad, iv=iv)
    assert res[12:-16] == c and res[-16:] == mac

    k = bytes.fromhex('feffe9928665731c6d6a8f9467308308')
    iv = bytes.fromhex('cafebabefacedbaddecaf888')
    m = bytes.fromhex(
        'd9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b391aafd255')
    c = bytes.fromhex(
        '42831ec2217774244b7221b784d0d49ce3aa212f2c02a4e035c17e2329aca12e21d514b25466931c7d8f6a5aac84aa051ba30b396a0aac973d58e091473f5985')
    aad = b''
    mac = bytes.fromhex('4d5c2af327cd64a62cf35abd2ba6fab4')

    aes.set_key(k)
    res = aes.encrypt_gcm(m, aad=aad, iv=iv)
    assert res[12:-16] == c and res[-16:] == mac
    assert aes.decrypt_gcm(res, aad=aad) == m

    k = bytes.fromhex('feffe9928665731c6d6a8f9467308308')
    iv = bytes.fromhex('cafebabefacedbaddecaf888')
    m = bytes.fromhex(
        'd9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b39')
    c = bytes.fromhex(
        '42831ec2217774244b7221b784d0d49ce3aa212f2c02a4e035c17e2329aca12e21d514b25466931c7d8f6a5aac84aa051ba30b396a0aac973d58e091')
    aad = bytes.fromhex('feedfacedeadbeeffeedfacedeadbeefabaddad2')
    mac = bytes.fromhex('5bc94fbc3221a5db94fae95ae7121a47')

    aes.set_key(k)
    res = aes.encrypt_gcm(m, aad=aad, iv=iv)
    assert res[12:-16] == c and res[-16:] == mac
    assert aes.decrypt_gcm(res, aad=aad) == m

    # AES-CMAC
    k = bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')
    m = b''
    t = bytes.fromhex('bb1d6929 e9593728 7fa37d12 9b756746')

    aes.set_key(k)
    assert aes.mac_cmac(m) == t
    m = bytes.fromhex('6bc1bee2 2e409f96 e93d7e11 7393172a')
    t = bytes.fromhex('070a16b4 6b4d4144 f79bdd9d d04a287c')
    assert aes.mac_cmac(m) == t
    m = bytes.fromhex(
        '6bc1bee2 2e409f96 e93d7e11 7393172a ae2d8a57 1e03ac9c 9eb76fac 45af8e51 30c81c46 a35ce411')
    t = bytes.fromhex('dfa66747 de9ae630 30ca3261 1497c827')
    assert aes.mac_cmac(m) == t
    m = bytes.fromhex(
        '6bc1bee2 2e409f96 e93d7e11 7393172a ae2d8a57 1e03ac9c 9eb76fac 45af8e51 30c81c46 a35ce411 e5fbc119 1a0a52ef f69f2445 df4f9b17 ad2b417b e66c3710')
    t = bytes.fromhex('51f0bebf 7e3b9d92 fc497417 79363cfe')
    assert aes.mac_cmac(m) == t
