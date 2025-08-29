from datetime import datetime, tzinfo
from typing import Dict, Any, List

from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_device_info
#
# RESULT int:        1228249668322633963475565502
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000011 11110111 11111011 11111011 11101111 11111111 11111111 11111111 11111111 11111111 11111011 10111110   LSB
# RESULT hex:  LE    be fb ff ff ff ff ff ef fb fb f7 03 00 00 00 00
#
# name                  type  size       value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ----  ----  ---------------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7       7               62                                                                                                                           0111110   # noqa: E501
# packet_type_id.0.DFF  bool     1                1                                                                                                                          1
# packet_type_id.1.VAL  u2       2                3                                                                                                                        11
# packet_type_id.1.DFF  bool     1                0                                                                                                                       0
# manufacturer_number   u50     50  562949953421311                                                                     01111111111111111111111111111111111111111111111111
# device_type           u6       6               31                                                               011111
# firmware_version      u8       8              127                                                       01111111
# ktt                   u9       9              255                                              011111111
# ktn                   u7       7               63                                       0111111
# RESERVED              u37     37                0  0000000000000000000000000000000000000


class SmpmUlDeviceEnergy16BDeviceInfoData(Packet):
    manufacturer_number: int
    device_type: int
    firmware_version: int
    ktt: int
    ktn: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((62) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((3) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.manufacturer_number, int)
        assert 0 <= data.manufacturer_number <= 1125899906842623
        result |= ((data.manufacturer_number) & (2 ** (50) - 1)) << size
        size += 50
        assert isinstance(data.device_type, int)
        assert 0 <= data.device_type <= 63
        result |= ((data.device_type) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.firmware_version, int)
        assert 0 <= data.firmware_version <= 255
        result |= ((data.firmware_version) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.ktt, int)
        assert 0 <= data.ktt <= 511
        result |= ((data.ktt) & (2 ** (9) - 1)) << size
        size += 9
        assert isinstance(data.ktn, int)
        assert 0 <= data.ktn <= 127
        result |= ((data.ktn) & (2 ** (7) - 1)) << size
        size += 7
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BDeviceInfoData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 62 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 3 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["manufacturer_number"] = buf.shift(50) + 0
        result__el_tmp1["device_type"] = buf.shift(6) + 0
        result__el_tmp1["firmware_version"] = buf.shift(8) + 0
        result__el_tmp1["ktt"] = buf.shift(9) + 0
        result__el_tmp1["ktn"] = buf.shift(7) + 0
        result = SmpmUlDeviceEnergy16BDeviceInfoData(**result__el_tmp1)
        buf.shift(37)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                # TODO: extend integration message with new structure for device info and fill it out here
            ),
        ]
