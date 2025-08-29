from typing import Dict, Any, Tuple, List
from datetime import datetime, tzinfo

from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_internal_info
#
# RESULT int:        9187201950435737471
# RESULT bin:  MSB   01111111 01111111 01111111 01111111 01111111 01111111 01111111 01111111   LSB
# RESULT hex:  LE    7f 7f 7f 7f 7f 7f 7f 7f
#
# name                  type  size  value(int)                                                        data(bits)
# --------------------  ----  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL  u7       7         127                                                           1111111
# packet_type_id.0.DFF  bool     1           0                                                          0
# data.0.byte           u8       8         127                                                  01111111
# data.1.byte           u8       8         127                                          01111111
# data.2.byte           u8       8         127                                  01111111
# data.3.byte           u8       8         127                          01111111
# data.4.byte           u8       8         127                  01111111
# data.5.byte           u8       8         127          01111111
# data.6.byte           u8       8         127  01111111


class SmpmUlDeviceInternalInfoData(Packet):
    data: Tuple[int, int, int, int, int, int, int]

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((127) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.data, tuple) and len(data.data) == 7
        assert isinstance(data.data[0], int)
        assert 0 <= data.data[0] <= 255
        result |= ((data.data[0]) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.data[1], int)
        assert 0 <= data.data[1] <= 255
        result |= ((data.data[1]) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.data[2], int)
        assert 0 <= data.data[2] <= 255
        result |= ((data.data[2]) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.data[3], int)
        assert 0 <= data.data[3] <= 255
        result |= ((data.data[3]) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.data[4], int)
        assert 0 <= data.data[4] <= 255
        result |= ((data.data[4]) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.data[5], int)
        assert 0 <= data.data[5] <= 255
        result |= ((data.data[5]) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.data[6], int)
        assert 0 <= data.data[6] <= 255
        result |= ((data.data[6]) & (2 ** (8) - 1)) << size
        size += 8
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceInternalInfoData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 127 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        data_tmp2: List[int] = []
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        data__item_tmp3 = buf.shift(8) + 0
        data_tmp2.append(data__item_tmp3)
        result__el_tmp1["data"] = tuple(data_tmp2)
        result = SmpmUlDeviceInternalInfoData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(dt=received_at),
        ]
