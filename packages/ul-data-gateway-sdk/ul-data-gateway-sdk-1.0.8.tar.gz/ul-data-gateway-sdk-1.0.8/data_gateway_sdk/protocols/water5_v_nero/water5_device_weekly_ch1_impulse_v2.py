from datetime import datetime, tzinfo
from decimal import Decimal
from typing import Dict, List, Any

from data_aggregator_sdk.constants.enums import SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_weekly_ch1_impulse_v2
#
# RESULT int:        14051230837399099763
# RESULT bin:  MSB   1100001100000000000000000000000000000000001100000001100101110011   LSB
# RESULT hex:  LE    73 19 30 00 00 00 00 c3
#
#
# name           type  size  value(int)                                                        data(bits)
# -------------------------------------------------------------------------------------------------------
# pack_id        u8       8         115                                                          01110011
# value          u24     24       12313                                  000000000011000000011001
# UNUSED         -       24           0          000000000000000000000000
# battery_fract  u7       7          67   1000011
# battery_int    u1       1           1  1


class Water5DeviceWeeklyCh1ImpulseV2Data(Packet):
    value: int
    battery_int: int
    battery_fract: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((115) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.value, int)
        val_tmp1 = data.value
        val_mod_tmp2 = val_tmp1 % 16777215
        result |= ((val_mod_tmp2 if val_mod_tmp2 else (val_tmp1 if not val_tmp1 else 16777215)
                    ) & (2 ** (24) - 1)) << size
        size += 24
        result |= ((0) & (2 ** (24) - 1)) << size
        size += 24
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
    def parse(cls, buf: BufRef) -> 'Water5DeviceWeeklyCh1ImpulseV2Data':
        result__el_tmp3: Dict[str, Any] = dict()
        if 115 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        result__el_tmp3["value"] = buf.shift(24) + 0
        buf.shift(24)
        result__el_tmp3["battery_fract"] = buf.shift(7) + 0
        result__el_tmp3["battery_int"] = buf.shift(1) + 2
        result = Water5DeviceWeeklyCh1ImpulseV2Data(**result__el_tmp3)
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
                        overloading_value=Decimal(str(16777215.0)),
                    ),
                    # : List[IntegrationV0MessageConsumption]
                ],
            ),
        ]
