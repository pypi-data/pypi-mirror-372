from decimal import Decimal
from typing import Dict, List, Any
from datetime import datetime, tzinfo

from data_aggregator_sdk.constants.enums import SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_weekly_ch1
#
# RESULT int:        14051230840548075635
# RESULT bin:  MSB   1100001100000000000000000000000010111011111000011010100001110011   LSB
# RESULT hex:  LE    73 a8 e1 bb 00 00 00 c3
#
#
# name           type    size  value(int)                                                        data(bits)
# ---------------------------------------------------------------------------------------------------------
# pack_id        u8         8         115                                                          01110011
# value          uf27p3    27    12313000                               000101110111110000110101000
# UNUSED         -         21           0          000000000000000000000
# battery_fract  u7         7          67   1000011
# battery_int    u1         1           1  1


class Water5DeviceWeeklyCh1Data(Packet):
    value: float
    battery_int: int
    battery_fract: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((115) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.value, (int, float))
        assert 0.0 <= data.value
        result |= ((int(round(float(data.value) * 1000.0, 0))) & (2 ** (27) - 1)) << size
        size += 27
        result |= ((0) & (2 ** (21) - 1)) << size
        size += 21
        assert isinstance(data.battery_fract, int)
        assert 0 <= data.battery_fract <= 127
        result |= ((data.battery_fract) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.battery_int, int)
        assert 2 <= data.battery_int <= 3
        result |= (((data.battery_int + -2)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceWeeklyCh1Data':
        result__el_tmp1: Dict[str, Any] = dict()
        if 115 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        result__el_tmp1["value"] = round(buf.shift(27) / 1000.0 - 0.0, 3)
        buf.shift(21)
        result__el_tmp1["battery_fract"] = buf.shift(7) + 0
        result__el_tmp1["battery_int"] = buf.shift(1) + 2
        result = Water5DeviceWeeklyCh1Data(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.battery_int + self.battery_fract / 100)),
                        sensor_type=SensorType.BATTERY,
                    ),
                ],
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(self.value)),
                        overloading_value=Decimal(str(134217.727)),
                    ),
                    # : List[IntegrationV0MessageConsumption]
                ],
            ),
        ]
