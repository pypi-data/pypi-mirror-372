from enum import Enum, unique
from typing import Optional

from data_gateway_sdk.crypto_algorithms.crypto_aes import aes_ecb_encryption, aes_ecb_decryption
from data_gateway_sdk.crypto_algorithms.crypto_kuznechik import kuznechik_encryption, kuznechik_decryption
from data_gateway_sdk.crypto_algorithms.crypto_xtea import xtea_decrypt, xtea_encrypt


@unique
class EncryptionType(Enum):  # DO NOT CHANGE VALUE because it should be compatible with data_aggregator_sdk db !!!
    NO_ENCRYPTION = 'NO_ENCRYPTION'
    XTEA_V_NERO_V0 = 'XTEA_V_NERO_V0'
    AES_ECB_V_NERO_V0 = 'AES_ECB_V_NERO_V0'
    KUZNECHIK_V_NERO_V0 = 'KUZNECHIK_V_NERO_V0'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def encrypt(self, src: bytes, key: Optional[bytes]) -> bytes:
        assert isinstance(src, bytes), f'src decrypt must be type of {bytes}, got type {type(src)} '

        if self is EncryptionType.NO_ENCRYPTION:
            assert key is None
            return src

        assert isinstance(key, bytes), f'key decrypt must be type of {bytes}, got type {type(key)} '

        if self is EncryptionType.XTEA_V_NERO_V0:
            return xtea_encrypt(src, key)

        if self is EncryptionType.AES_ECB_V_NERO_V0:
            return aes_ecb_encryption(src, key)

        if self is EncryptionType.KUZNECHIK_V_NERO_V0:
            return kuznechik_encryption(src, key)

        raise NotImplementedError(f'Unsupported type. {self} was given')

    def decrypt(self, src: bytes, key: Optional[bytes]) -> bytes:
        assert isinstance(src, bytes), f'src decrypt must be type of {bytes}, got type {type(src)} '

        if self is EncryptionType.NO_ENCRYPTION:
            assert not key, f'key decrypt must be empty on {EncryptionType.NO_ENCRYPTION}, got type {type(key)} '
            return src

        assert isinstance(key, bytes), f'key decrypt must be type of {bytes}, got type {type(key)} '

        if self is EncryptionType.XTEA_V_NERO_V0:
            return xtea_decrypt(src, key)

        if self is EncryptionType.AES_ECB_V_NERO_V0:
            return aes_ecb_decryption(src, key)

        if self is EncryptionType.KUZNECHIK_V_NERO_V0:
            return kuznechik_decryption(src, key)

        raise NotImplementedError(f'Unsupported type. {self} was given')
