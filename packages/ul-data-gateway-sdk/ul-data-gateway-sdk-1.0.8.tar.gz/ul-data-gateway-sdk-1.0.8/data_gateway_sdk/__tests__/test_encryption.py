from data_gateway_sdk.device_data_encryption import EncryptionType


def test_decrypt_xtea_v_nero_v0() -> None:
    assert EncryptionType.XTEA_V_NERO_V0.decrypt(bytes.fromhex('8725024c66319b82'), bytes.fromhex('19208f5fd151c0b7e7c7890610f994b5c4fe697620b67e509b0ea2bd942b1fd6')) == bytes.fromhex('73086e0a000000a5')  # noqa: W391
    assert EncryptionType.XTEA_V_NERO_V0.decrypt(bytes.fromhex('461dee8050910076'), bytes.fromhex('6b4095ae9e35c7f4cbbd31de33a023e3f2d01d7c6041a885a13d202643118812')) == bytes.fromhex('7b3a00000000001f')  # noqa: W391
    assert EncryptionType.XTEA_V_NERO_V0.decrypt(bytes.fromhex('1ff19c361fd435cb'), bytes.fromhex('21dfdaae138b13c4c40fa2a560e51cbeca849f5b0d5b02232c27559125ddb124')) == bytes.fromhex('54c2000000000000')  # noqa: W391


def test_encrypt_xtea_v_nero_v0() -> None:
    assert EncryptionType.XTEA_V_NERO_V0.encrypt(bytes.fromhex('73086e0a000000a5'), bytes.fromhex('19208f5fd151c0b7e7c7890610f994b5c4fe697620b67e509b0ea2bd942b1fd6')) == bytes.fromhex('8725024c66319b82')  # noqa: W391
    assert EncryptionType.XTEA_V_NERO_V0.encrypt(bytes.fromhex('7b3a00000000001f'), bytes.fromhex('6b4095ae9e35c7f4cbbd31de33a023e3f2d01d7c6041a885a13d202643118812')) == bytes.fromhex('461dee8050910076')  # noqa: W391
    assert EncryptionType.XTEA_V_NERO_V0.encrypt(bytes.fromhex('54c2000000000000'), bytes.fromhex('21dfdaae138b13c4c40fa2a560e51cbeca849f5b0d5b02232c27559125ddb124')) == bytes.fromhex('1ff19c361fd435cb')  # noqa: W391
