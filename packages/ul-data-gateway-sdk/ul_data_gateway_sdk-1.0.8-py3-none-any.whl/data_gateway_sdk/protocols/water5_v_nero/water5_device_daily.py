from decimal import Decimal
from typing import Dict, List, Any
from datetime import datetime, tzinfo

from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    CounterType, ResourceType

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_daily
#
# RESULT int:        16600
# RESULT bin:  MSB   0000000000000000000000000000000000000000000000000100000011011000   LSB
# RESULT hex:  LE    d8 40 00 00 00 00 00 00
#
#
# name      type    size  value(int)                                                        data(bits)
# ----------------------------------------------------------------------------------------------------
# pack_id   u1         1           0                                                                 0
# value     uf15p3    15        8300                                                  010000001101100
# RESERVED  u48       48           0  000000000000000000000000000000000000000000000000


class Water5DeviceDailyData(Packet):
    value: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value, (int, float))
        assert 0.0 <= data.value
        result |= ((int(round(float(data.value) * 1000.0, 0))) & (2 ** (15) - 1)) << size
        size += 15
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceDailyData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 0 != buf.shift(1):
            raise ValueError("pack_id: buffer doesn't match value")
        result__el_tmp1["value"] = round(buf.shift(15) / 1000.0 - 0.0, 3)
        buf.shift(48)
        result = Water5DeviceDailyData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(self.value)),
                        overloading_value=Decimal(str(32.767))),
                ],
            ),
        ]
