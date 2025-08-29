import unittest

from data_gateway_sdk.crypto_algorithms.crypto_aes import aes_ecb_decryption, aes_ecb_encryption, AesError
from data_gateway_sdk.crypto_algorithms.crypto_kuznechik import kuznechik_encryption, kuznechik_decryption, KuznechikError


class TestCrypto(unittest.TestCase):
    def test_aes_128(self) -> None:
        # ECB-AES-128 test
        plaintext = bytes.fromhex('6bc1bee22e409f96e93d7e117393172a'
                                  'ae2d8a571e03ac9c9eb76fac45af8e51'
                                  '30c81c46a35ce411e5fbc1191a0a52ef'
                                  'f69f2445df4f9b17ad2b417be66c3710')

        key = bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')

        expected_ciphertext = bytes.fromhex('3ad77bb40d7a3660a89ecaf32466ef97'
                                            'f5d3d58503b9699de785895a96fdbaaf'
                                            '43b1cd7f598ece23881b00e3ed030688'
                                            '7b0c785e27e8ad3f8223207104725dd4')

        ciphertext = aes_ecb_encryption(plaintext, key)
        self.assertEqual(ciphertext, expected_ciphertext)

        recovered_plaintext = aes_ecb_decryption(ciphertext, key)
        self.assertEqual(recovered_plaintext, plaintext)

    def test_aes_256(self) -> None:
        # ECB-AES-256 test
        plaintext = bytes.fromhex('00112233445566778899aabbccddeeff'
                                  '00112233445566778899aabbccddeeff'
                                  '00112233445566778899aabbccddeeff'
                                  '00112233445566778899aabbccddeeff')

        key = bytes.fromhex('000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f')

        expected_ciphertext = bytes.fromhex('8ea2b7ca516745bfeafc49904b496089'
                                            '8ea2b7ca516745bfeafc49904b496089'
                                            '8ea2b7ca516745bfeafc49904b496089'
                                            '8ea2b7ca516745bfeafc49904b496089')

        ciphertext = aes_ecb_encryption(plaintext, key)
        self.assertEqual(ciphertext, expected_ciphertext)

        recovered_plaintext = aes_ecb_decryption(ciphertext, key)
        self.assertEqual(recovered_plaintext, plaintext)

        with self.assertRaises(AesError):
            plaintext = bytes.fromhex('00112233445566778899aabbccddeeff'
                                      '00112233445566778899aabbccddeeff'
                                      '00112233445566778899aabbccddeeff'
                                      '00112233445566778899aabbccddeeff')
            key = bytes.fromhex('000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e')
            aes_ecb_encryption(plaintext, key)

    def test_kuznechik(self) -> None:
        mtest = bytes.fromhex('1122334455667700ffeeddccbbaa9988')
        ktest = bytes.fromhex('8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef')

        encrypted_block = kuznechik_encryption(mtest, ktest)
        expected_enc = bytes.fromhex('7f679d90bebc24305a468d42b9d4edcd')
        self.assertEqual(encrypted_block, expected_enc)

        decrypted_block = kuznechik_decryption(encrypted_block, ktest)
        expected_dec = bytes.fromhex('1122334455667700ffeeddccbbaa9988')
        self.assertEqual(decrypted_block, expected_dec)

        with self.assertRaises(KuznechikError):
            mtest = bytes.fromhex('1122334455667700ffeeddccbbaa9988')
            ktest = bytes.fromhex('8899aabbccddeeff0011223344556677fedcba98765432100123456789abcd')
            kuznechik_encryption(mtest, ktest)

        with self.assertRaises(KuznechikError):
            mtest = bytes.fromhex('1122334455667700ffeeddccbbaa99')
            ktest = bytes.fromhex('8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef')
            kuznechik_encryption(mtest, ktest)


if __name__ == "__main__":
    unittest.main()
