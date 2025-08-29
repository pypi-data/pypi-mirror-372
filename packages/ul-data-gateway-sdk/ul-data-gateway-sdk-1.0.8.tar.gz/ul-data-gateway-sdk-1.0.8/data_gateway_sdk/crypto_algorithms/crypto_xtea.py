from typing import List, Tuple

from data_gateway_sdk.crypto_algorithms.extensions.errors import XteaError

delta: int = 2654435769
num_iterations = 64
key_length_bytes = 32
block_length_bytes = 8
mask = 0xffffffff


def decrypt(src: str, key_bytes: bytes) -> bytes:
    assert isinstance(src, str), f'src decrypt must be type of {str}, got type {type(src)} '
    assert isinstance(key_bytes, bytes), f'key_bytes decrypt must be type of {bytes}, got type {type(key_bytes)} '
    data = bytearray.fromhex(src)

    valid_key(key_bytes)
    tmp_decrypts = _decrypt_xtea(data, key_bytes[16:32])
    return _decrypt_xtea(tmp_decrypts, key_bytes[0:16])


def xtea_decrypt(src: bytes, key_bytes: bytes) -> bytes:
    assert isinstance(src, bytes), f'src decrypt must be type of {bytes}, got type {type(src)} '
    assert isinstance(key_bytes, bytes), f'key_bytes decrypt must be type of {bytes}, got type {type(key_bytes)} '
    valid_key(key_bytes)
    tmp_decrypts = _decrypt_xtea(src, key_bytes[16:32])

    return _decrypt_xtea(tmp_decrypts, key_bytes[0:16])


def encrypt(src: str, key_bytes: bytes) -> bytes:
    assert isinstance(src, str), f'src encrypt must be type of {str}, got type {type(src)} '
    assert isinstance(key_bytes, bytes), f'key_bytes encrypt must be type of {bytes}, got type {type(key_bytes)} '
    data = bytearray.fromhex(src)

    valid_key(key_bytes)
    tmp_decrypts = _encrypt_xtea(data, key_bytes[0:16])
    return _encrypt_xtea(tmp_decrypts, key_bytes[16:32])


def xtea_encrypt(src: bytes, key_bytes: bytes) -> bytes:
    assert isinstance(src, bytes), f'src decrypt must be type of {bytes}, got type {type(src)} '
    assert isinstance(key_bytes, bytes), f'key_bytes decrypt must be type of {bytes}, got type {type(key_bytes)} '

    valid_key(key_bytes)
    tmp_decrypts = _encrypt_xtea(src, key_bytes[0:16])
    return _encrypt_xtea(tmp_decrypts, key_bytes[16:32])


def _decrypt_xtea(src: bytes, key_bytes: bytes) -> bytes:
    dst: bytes = b""
    blocks_num, key = _preparation_block(src, key_bytes)
    for i in range(blocks_num):
        block_start = i * block_length_bytes
        dst += _decrypt_block(src[block_start:block_start + block_length_bytes], key)
    return dst


def _encrypt_xtea(src: bytes, key_bytes: bytes) -> bytes:
    dst: bytes = b""
    blocks_num, key = _preparation_block(src, key_bytes)
    for i in range(blocks_num):
        block_start = i * block_length_bytes
        dst += _encrypt_block(src[block_start:block_start + block_length_bytes], key)
    return dst


def _preparation_block(src: bytes, key_bytes: bytes) -> Tuple[int, List[int]]:
    key: List[int] = []
    key.insert(0, (int.from_bytes(bytes=key_bytes[0:4], byteorder="little")))
    key.insert(1, (int.from_bytes(bytes=key_bytes[4:8], byteorder="little")))
    key.insert(2, (int.from_bytes(bytes=key_bytes[8:12], byteorder="little")))
    key.insert(3, (int.from_bytes(bytes=key_bytes[12:16], byteorder="little")))

    blocks_num: int = int(len(src) / block_length_bytes)
    return blocks_num, key


def _decrypt_block(src: bytes, key: List[int]) -> bytes:
    amount = (delta * num_iterations) & mask
    x1, x2 = _block_to_int32(src)
    for _ in range(num_iterations):
        x2 = (x2 - (((x1 << 4 ^ x1 >> 5) + x1) ^ (amount + key[(amount >> 11) & 3])) & mask)
        amount = (amount - delta) & mask
        x1 = (x1 - (((x2 << 4 ^ x2 >> 5) + x2) ^ (amount + key[amount & 3])) & mask)
    result = _uint32_to_block(x1, x2)
    return result


def _encrypt_block(src: bytes, key: List[int]) -> bytes:
    amount = 0
    x1, x2 = _block_to_int32(src)
    for _ in range(num_iterations):
        x1 = (x1 + (((x2 << 4 ^ x2 >> 5) + x2) ^ (amount + key[amount & 3]))) & mask
        amount = (amount + delta) & mask
        x2 = (x2 + (((x1 << 4 ^ x1 >> 5) + x1) ^ (amount + key[amount >> 11 & 3]))) & mask
    result = _uint32_to_block(x1, x2)
    return result


def _block_to_int32(block: bytes) -> Tuple[int, int]:
    x1 = int.from_bytes(block[0:4], "little")
    x2 = int.from_bytes(block[4:8], "little")
    return x1, x2


def _uint32_to_block(x1: int, x2: int) -> bytes:
    return x1.to_bytes(length=4, byteorder="little") + x2.to_bytes(length=4, byteorder="little")


def valid_key(key_bytes: bytes) -> None:
    if len(key_bytes) != key_length_bytes:
        raise XteaError(f"invalid length KEY '{len(key_bytes)}' was given, must '{key_length_bytes}'")
