from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, \
    IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_jupiter_08b_counter_ch1
#
# RESULT int:        31139818566057830
# RESULT bin:  MSB   00000000 01101110 10100001 01111111 11111111 11111111 11111111 01100110   LSB
# RESULT hex:  LE    66 ff ff ff 7f a1 6e 00
#
# name                     type   size  value(int)                                                        data(bits)
# -----------------------  -----  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL     u7        7         102                                                           1100110
# packet_type_id.0.DFF     bool      1           0                                                          0
# value                    u32      32  2147483647                          01111111111111111111111111111111
# battery_volts            uf6p1     6          33                    100001
# temperature              u7        7          58             0111010
# event_reset              bool      1           1            1
# event_low_battery_level  bool      1           1           1
# RESERVED                 u9        9           0  000000000


class SmpmUlDeviceJupiter08BCounterCh1Data(Packet):
    value: int
    battery_volts: float
    temperature: int
    event_reset: bool
    event_low_battery_level: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((102) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value, int)
        result |= (((data.value) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
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
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceJupiter08BCounterCh1Data':
        result__el_tmp1: Dict[str, Any] = dict()
        if 102 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["value"] = buf.shift(32) + 0
        result__el_tmp1["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp1["temperature"] = buf.shift(7) + -35
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result = SmpmUlDeviceJupiter08BCounterCh1Data(**result__el_tmp1)
        buf.shift(9)
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
                        value=Decimal(str(self.value)),
                        overloading_value=Decimal(str(1099511627775.0)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                ],
            ),
        ]
