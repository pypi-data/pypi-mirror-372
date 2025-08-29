import random
import typing
from enum import IntEnum, unique

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_dl_device_energy_8b_set_relay
#
# RESULT int:        426
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000000 00000000 00000001 10101010   LSB
# RESULT hex:  LE    aa 01 00 00 00 00 00 00
#
# name                  type                            size  value(int)                                                        data(bits)
# --------------------  ------------------------------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL  u7                                 7          42                                                           0101010
# packet_type_id.0.DFF  bool                               1           1                                                          1
# packet_type_id.1.VAL  u2                                 2           1                                                        01
# packet_type_id.1.DFF  bool                               1           0                                                       0
# state                 bool                               1           0                                                      0
# relay_id              SmpmDlDeviceEnergy8bSetRelayId     8           0                                              00000000
# RESERVED              u44                               44           0  00000000000000000000000000000000000000000000
# Reserved space is filled with random bits in DOWNLINK packets !


@unique
class SmpmDlDeviceEnergy8bSetRelayId(IntEnum):
    ALL = 0
    RELAY_ID_1 = 1
    RELAY_ID_2 = 2
    RELAY_ID_3 = 3
    RELAY_ID_4 = 4
    RELAY_ID_5 = 5
    RELAY_ID_6 = 6
    RELAY_ID_7 = 7


class SmpmDlDeviceEnergy8BSetRelayData(Packet):
    state: bool
    relay_id: SmpmDlDeviceEnergy8bSetRelayId

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((42) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.state, bool)
        result |= ((int(data.state)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.relay_id, SmpmDlDeviceEnergy8bSetRelayId)
        result |= ((data.relay_id.value) & (2 ** (8) - 1)) << size
        size += 8
        result |= ((random.getrandbits(44)) & (2 ** 44 - 1)) << size
        size += 44
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmDlDeviceEnergy8BSetRelayData':
        result__el_tmp1: typing.Dict[str, typing.Any] = dict()
        if 42 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["state"] = bool(buf.shift(1))
        result__el_tmp1["relay_id"] = SmpmDlDeviceEnergy8bSetRelayId(buf.shift(8))
        result = SmpmDlDeviceEnergy8BSetRelayData(**result__el_tmp1)
        buf.shift(44)
        return result
