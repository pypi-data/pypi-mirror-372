import zlib
from typing import NamedTuple, Dict, Any, List

from data_gateway_sdk.errors import DataGatewayDeviceProtocolParsingError
from data_gateway_sdk.utils.buf_ref import BufRef


# PACKET (N/A bits)   unbp_uplink_len
#
# RESULT int:        230523608866647489049872409590682171
# RESULT bin:  MSB   00101100 01100101 10110001 00000001 00010110 00111111 01111111 00000011 00000000 00000000 00000000 00000000 00100010 11010010 00111011   LSB
# RESULT hex:  LE    3b d2 22 00 00 00 00 03 7f 3f 16 01 b1 65 2c
#
# name            type  size  value(int)                                                                                                                data(bits)
# --------------  ----  ----  ----------  ------------------------------------------------------------------------------------------------------------------------
# identifier      u16     16       53819                                                                                                          1101001000111011
# mac             u32     32          34                                                                          00000000000000000000000000100010
# RESERVED        u3       3           0                                                                       000
# message_id      u5       5           0                                                                  00000
# payload.LEN     u8       8           3                                                          00000011
# payload.0.byte  u8       8         127                                                  01111111
# payload.1.byte  u8       8          63                                          00111111
# payload.2.byte  u8       8          22                                  00010110
# crc             u32     32   744861953  00101100011001011011000100000001


class UnbpUplinkLenData(NamedTuple):
    mac: int
    message_id: int
    payload: List[int]
    crc: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((53819) & (2 ** (16) - 1)) << size
        size += 16
        assert isinstance(data.mac, int)
        assert 0 <= data.mac <= 4294967295
        result |= ((data.mac) & (2 ** (32) - 1)) << size
        size += 32
        result |= ((0) & (2 ** (3) - 1)) << size
        size += 3
        assert isinstance(data.message_id, int)
        assert 0 <= data.message_id <= 31
        result |= ((data.message_id) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.payload, list)
        assert isinstance(len(data.payload), int)
        assert 0 <= len(data.payload) <= 255
        result |= ((len(data.payload)) & (2 ** (8) - 1)) << size
        size += 8
        for payload__item_tmp1 in data.payload[:255]:
            assert isinstance(payload__item_tmp1, int)
            assert 0 <= payload__item_tmp1 <= 255
            result |= ((payload__item_tmp1) & (2 ** (8) - 1)) << size
            size += 8
        assert isinstance(data.crc, int)
        assert 0 <= data.crc <= 4294967295
        result |= ((data.crc) & (2 ** (32) - 1)) << size
        size += 32
        return result.to_bytes(size // 8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'UnbpUplinkLenData':
        result__el_tmp2: Dict[str, Any] = dict()
        prev_ends_at = buf.ends_at

        try:
            if 53819 != buf.shift(16):
                raise DataGatewayDeviceProtocolParsingError("identifier: buffer doesn't match value")
        except ValueError:
            raise DataGatewayDeviceProtocolParsingError("identifier: buffer doesn't match value")

        try:
            result__el_tmp2["mac"] = buf.shift(32) + 0
        except ValueError:
            raise DataGatewayDeviceProtocolParsingError("mac: buffer doesn't match value")

        try:
            if 0 != buf.shift(3):
                raise DataGatewayDeviceProtocolParsingError("RESERVED: buffer doesn't match value")
        except ValueError:
            raise DataGatewayDeviceProtocolParsingError("RESERVED: buffer doesn't match value")

        try:
            result__el_tmp2["message_id"] = buf.shift(5) + 0
        except ValueError:
            raise DataGatewayDeviceProtocolParsingError("message_id: buffer doesn't match value")
        payload__res_tmp5: List[int] = []

        try:
            length_tmp6 = buf.shift(8) + 0
            for _payload__i_tmp3 in range(length_tmp6):
                payload__item_tmp4 = buf.shift(8) + 0
                payload__res_tmp5.append(payload__item_tmp4)
            result__el_tmp2["payload"] = payload__res_tmp5
        except ValueError:
            raise DataGatewayDeviceProtocolParsingError("payload: buffer doesn't match value")

        try:
            result__el_tmp2["crc"] = buf.shift(32) + 0
            if result__el_tmp2["crc"] in [0, 4294967295]:
                raise DataGatewayDeviceProtocolParsingError("CRC: CRC invalid ")
        except ValueError:
            raise DataGatewayDeviceProtocolParsingError("CRC: buffer doesn't match value")
        else:
            size = 8 + len(result__el_tmp2["payload"])
            array_without_crc: bytes = buf.get_bits(size=size * 8, start=-(buf.ends_at - prev_ends_at)).to_bytes(byteorder="big", length=size)
            crc = zlib.crc32(array_without_crc[::-1])
            if result__el_tmp2["crc"] != crc:
                raise DataGatewayDeviceProtocolParsingError("CRC: CRC sum mismatched ")
            result = UnbpUplinkLenData(**result__el_tmp2)
        return result
