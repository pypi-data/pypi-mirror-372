from decimal import Decimal
from typing import Dict, List, Any
from datetime import datetime, tzinfo

from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    CounterType, ResourceType

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_info_ch2
#
# RESULT int:        4172905
# RESULT bin:  MSB   0000000000000000000000000000000000000000001111111010110001101001   LSB
# RESULT hex:  LE    69 ac 3f 00 00 00 00 00
#
#
# name      type    size  value(int)                                                        data(bits)
# ----------------------------------------------------------------------------------------------------
# pack_id   u8         8         105                                                          01101001
# value     uf32p3    32       16300                          00000000000000000011111110101100
# RESERVED  u24       24           0  000000000000000000000000


class Water5DeviceInfoCh2Data(Packet):
    value: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((105) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.value, (int, float))
        assert 0.0 <= data.value <= 4294967.295
        result |= ((int(round(float(data.value) * 1000.0, 0))) & (2 ** (32) - 1)) << size
        size += 32
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceInfoCh2Data':
        result__el_tmp1: Dict[str, Any] = dict()
        if 105 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        result__el_tmp1["value"] = round(buf.shift(32) / 1000.0 - 0.0, 3)
        buf.shift(24)
        result = Water5DeviceInfoCh2Data(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=2,
                        value=Decimal(str(self.value)),
                        overloading_value=None,
                    ),
                    # : List[IntegrationV0MessageConsumption]
                ],
            ),
        ]
