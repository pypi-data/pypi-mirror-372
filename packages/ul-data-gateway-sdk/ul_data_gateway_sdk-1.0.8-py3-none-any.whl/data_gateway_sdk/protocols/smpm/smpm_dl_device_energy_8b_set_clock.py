import random
import typing
from datetime import timedelta

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_dl_device_energy_8b_set_clock
#
# RESULT int:        72057044282113794
# RESULT bin:  MSB   00000000 11111111 11111111 01111111 11111111 11111111 11111111 00000010   LSB
# RESULT hex:  LE    02 ff ff ff 7f ff ff 00
#
# name                          type       size  value(int)                                                        data(bits)
# ----------------------------  ---------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL          u7            7           2                                                           0000010
# packet_type_id.0.DFF          bool          1           0                                                          0
# time                          timedelta    32  2147483647                          01111111111111111111111111111111
# time_zone_offset_s            timedelta    17       65535         01111111111111111
# time_zone_offset_is_negative  bool          1           0        0
# RESERVED                      u6            6           0  000000
# Reserved space is filled with random bits in DOWNLINK packets !


class SmpmDlDeviceEnergy8BSetClockData(Packet):
    time: timedelta
    time_zone_offset_s: timedelta
    time_zone_offset_is_negative: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((2) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.time, (int, timedelta))
        time_tmp1 = int(data.time.total_seconds() // 1 if isinstance(data.time, timedelta) else data.time // 1)
        assert 0 <= time_tmp1 <= 4294967295
        result |= ((time_tmp1) & (2 ** (32) - 1)) << size
        size += 32
        isinstance(data.time_zone_offset_s, (int, timedelta))
        time_zone_offset_s_tmp2 = int(data.time_zone_offset_s.total_seconds() // 1 if isinstance(data.time_zone_offset_s, timedelta) else data.time_zone_offset_s // 1)
        assert 0 <= time_zone_offset_s_tmp2 <= 131071
        result |= ((time_zone_offset_s_tmp2) & (2 ** (17) - 1)) << size
        size += 17
        assert isinstance(data.time_zone_offset_is_negative, bool)
        result |= ((int(data.time_zone_offset_is_negative)) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((random.getrandbits(6)) & (2 ** 6 - 1)) << size
        size += 6
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmDlDeviceEnergy8BSetClockData':
        result__el_tmp3: typing.Dict[str, typing.Any] = dict()
        if 2 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp3["time"] = timedelta(seconds=buf.shift(32) * 1)
        result__el_tmp3["time_zone_offset_s"] = timedelta(seconds=buf.shift(17) * 1)
        result__el_tmp3["time_zone_offset_is_negative"] = bool(buf.shift(1))
        result = SmpmDlDeviceEnergy8BSetClockData(**result__el_tmp3)
        buf.shift(6)
        return result
