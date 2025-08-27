# pragma pylint: disable=C0114,C0116
import pytest  # pylint: disable=W0611

from kryptools import Keccak, SHA3


def test_KECCAK():
    result = [ 0xf1258f7940e1dde7, 0x84d5ccf933c0478a, 0xd598261ea65aa9ee, 0xbd1547306f80494d, 0x8b284e056253d057,
        0xff97a42d7f8e6fd4, 0x90fee5a0a44647c4, 0x8c5bda0cd6192e76, 0xad30a6f71b19059c, 0x30935ab7d08ffc64,
        0xeb5aa93f2317d635, 0xa9a6e6260d712103, 0x81a57c16dbcf555f, 0x43b831cd0347c826, 0x1f22f1a11a5569f,
        0x5e5635a21d9ae61, 0x64befef28cc970f2, 0x613670957bc46611, 0xb87c5a554fd00ecb, 0x8c3ee88a1ccf32c8,
        0x940c7922ae3a2614, 0x1841f924a2c509e4, 0x16f53526e70465c2, 0x75f644e97f30a13b, 0xeaf1ff7b5ceca249 ]
    keccak = Keccak()
    keccak.f()
    assert keccak.state == result


# https://www.di-mgt.com.au/sha_testvectors.html
all_tests = [
{"message" : { "data" : "abc", "count" : 1},
"SHA-3-224" : "e642824c3f8cf24ad09234ee7d3c766fc9a3a5168d0c94ad73b46fdf",
"SHA-3-256" : "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532",
"SHA-3-384" : "ec01498288516fc926459f58e2c6ad8df9b473cb0fc08c2596da7cf0e49be4b298d88cea927ac7f539f1edf228376d25",
"SHA-3-512" : "b751850b1a57168a5693cd924b6b096e08f621827444f70d884f5d0240d2712e10e116e9192af3c91a7ec57647e3934057340b4cf408d5a56592f8274eec53f0"
},
{"message" : { "data" : "", "count" : 1},
"SHA-3-224" : "6b4e03423667dbb73b6e15454f0eb1abd4597f9a1b078e3f5b5a6bc7",
"SHA-3-256" : "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a",
"SHA-3-384" : "0c63a75b845e4f7d01107d852e4c2485c51a50aaaa94fc61995e71bbee983a2ac3713831264adb47fb6bd1e058d5f004",
"SHA-3-512" : "a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26"
},
{"message" : { "data" : "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", "count" : 1},
"SHA-3-224" : "8a24108b154ada21c9fd5574494479ba5c7e7ab76ef264ead0fcce33",
"SHA-3-256" : "41c0dba2a9d6240849100376a8235e2c82e1b9998a999e21db32dd97496d3376",
"SHA-3-384" : "991c665755eb3a4b6bbdfb75c78a492e8c56a22c5c4d7e429bfdbc32b9d4ad5aa04a1f076e62fea19eef51acd0657c22",
"SHA-3-512" : "04a371e84ecfb5b8b77cb48610fca8182dd457ce6f326a0fd3d7ec2f1e91636dee691fbe0c985302ba1b0d8dc78c086346b533b49c030d99a27daf1139d6e75e"
},
{"message" : { "data" : "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu", "count" : 1},
"SHA-3-224" : "543e6868e1666c1a643630df77367ae5a62a85070a51c14cbf665cbc",
"SHA-3-256" : "916f6061fe879741ca6469b43971dfdb28b1a32dc36cb3254e812be27aad1d18",
"SHA-3-384" : "79407d3b5916b59c3e30b09822974791c313fb9ecc849e406f23592d04f625dc8c709b98b43b3852b337216179aa7fc7",
"SHA-3-512" : "afebb2ef542e6579c50cad06d2e578f9f8dd6881d7dc824d26360feebf18a4fa73e3261122948efcfd492e74e82e2189ed0fb440d187f382270cb455f21dd185"
}
]

def test_SHA3():
    for test in all_tests:
        msg = bytes(test["message"]["data"], 'utf-8')
        for key, item in test.items():
            if key[:5] != "SHA-3":
                continue
            n = int(key[6:])
            h = int(item, 16)
            k = SHA3(n)(msg)
            assert int.from_bytes(k, 'big') == h, f"{n}: {msg}"
