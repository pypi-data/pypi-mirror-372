from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (96 bits)   smpm_ul_device_jupiter_12b_counter
#
# RESULT int:        17119296300107842493534435796
# RESULT bin:  MSB   00110111 01010000 10111111 11111111 11111111 11111111 11101111 11111111 11111111 11111111 11111001 11010100   LSB
# RESULT hex:  LE    d4 f9 ff ff ff ef ff ff ff bf 50 37
#
# name                     type   size  value(int)                                                                                        data(bits)
# -----------------------  -----  ----  ----------  ------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL     u7        7          84                                                                                           1010100
# packet_type_id.0.DFF     bool      1           1                                                                                          1
# packet_type_id.1.VAL     u2        2           1                                                                                        01
# packet_type_id.1.DFF     bool      1           0                                                                                       0
# value_channel_1          u34      34  8589934591                                                     0111111111111111111111111111111111
# value_channel_2          u34      34  8589934591                   0111111111111111111111111111111111
# battery_volts            uf6p1     6          33             100001
# temperature              u7        7          58      0111010
# event_reset              bool      1           1     1
# event_low_battery_level  bool      1           1    1
# RESERVED                 u2        2           0  00


class SmpmUlDeviceJupiter12BCounterData(Packet):
    value_channel_1: int
    value_channel_2: int
    battery_volts: float
    temperature: int
    event_reset: bool
    event_low_battery_level: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((84) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value_channel_1, int)
        result |= (((data.value_channel_1) & 17179869183) & (2 ** (34) - 1)) << size
        size += 34
        assert isinstance(data.value_channel_2, int)
        result |= (((data.value_channel_2) & 17179869183) & (2 ** (34) - 1)) << size
        size += 34
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 6.3
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.temperature, int)
        assert -35 <= data.temperature <= 92
        result |= (((data.temperature + 35)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_low_battery_level, bool)
        result |= ((int(data.event_low_battery_level)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(12, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceJupiter12BCounterData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 84 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["value_channel_1"] = buf.shift(34) + 0
        result__el_tmp1["value_channel_2"] = buf.shift(34) + 0
        result__el_tmp1["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp1["temperature"] = buf.shift(7) + -35
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result = SmpmUlDeviceJupiter12BCounterData(**result__el_tmp1)
        buf.shift(2)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.battery_volts)),
                        sensor_type=SensorType.BATTERY,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.temperature)),
                        sensor_type=SensorType.TEMPERATURE,
                    ),
                ],
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(self.value_channel_1)),
                        overloading_value=Decimal(str(17179869183.0)),
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=2,
                        value=Decimal(str(self.value_channel_2)),
                        overloading_value=Decimal(str(17179869183.0)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                ],
            ),
        ]
