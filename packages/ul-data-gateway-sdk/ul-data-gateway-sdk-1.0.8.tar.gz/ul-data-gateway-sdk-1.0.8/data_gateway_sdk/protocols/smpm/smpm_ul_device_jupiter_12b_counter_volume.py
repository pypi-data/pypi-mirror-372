from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_jupiter_12b_counter_volume
#
# RESULT int:        9234096531137368374233790933
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00011101 11010110 01000011 11111111 11111111 11111111 11111011 11111111 11111111 11111111 11111001 11010101   LSB
# RESULT hex:  LE    d5 f9 ff ff ff fb ff ff ff 43 d6 1d 00 00 00 00
#
# name                           type    size  value(int)                                                                                                                        data(bits)
# -----------------------------  ------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL           u7         7          85                                                                                                                           1010101
# packet_type_id.0.DFF           bool       1           1                                                                                                                          1
# packet_type_id.1.VAL           u2         2           1                                                                                                                        01
# packet_type_id.1.DFF           bool       1           0                                                                                                                       0
# volume_channel_1               uf32p3    32  2147483647                                                                                       01111111111111111111111111111111
# volume_channel_2               uf32p3    32  2147483647                                                       01111111111111111111111111111111
# battery_volts                  uf8p2      8         200                                               11001000
# temperature                    u7         7          58                                        0111010
# event_reset                    bool       1           1                                       1
# event_low_battery_level        bool       1           1                                      1
# event_low_ambient_temperature  bool       1           1                                     1
# RESERVED                       u35       35           0  00000000000000000000000000000000000


class SmpmUlDeviceJupiter12BCounterVolumeData(Packet):
    volume_channel_1: float
    volume_channel_2: float
    battery_volts: float
    temperature: int
    event_reset: bool
    event_low_battery_level: bool
    event_low_ambient_temperature: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((85) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.volume_channel_1, (int, float))
        result |= ((int(round(float(data.volume_channel_1) * 1000.0, 0)) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.volume_channel_2, (int, float))
        result |= ((int(round(float(data.volume_channel_2) * 1000.0, 0)) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 2.55
        result |= ((int(round(float(data.battery_volts) * 100.0, 0))) & (2 ** (8) - 1)) << size
        size += 8
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
        assert isinstance(data.event_low_ambient_temperature, bool)
        result |= ((int(data.event_low_ambient_temperature)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceJupiter12BCounterVolumeData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 85 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["volume_channel_1"] = round(buf.shift(32) / 1000.0, 3)
        result__el_tmp1["volume_channel_2"] = round(buf.shift(32) / 1000.0, 3)
        result__el_tmp1["battery_volts"] = round(buf.shift(8) / 100.0, 2)
        result__el_tmp1["temperature"] = buf.shift(7) + -35
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result__el_tmp1["event_low_ambient_temperature"] = bool(buf.shift(1))
        result = SmpmUlDeviceJupiter12BCounterVolumeData(**result__el_tmp1)
        buf.shift(35)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.battery_volts)) + Decimal(str(1.8)),
                        sensor_type=SensorType.BATTERY,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.temperature)) + Decimal(str(35)),
                        sensor_type=SensorType.TEMPERATURE,
                    ),
                ],
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(self.volume_channel_1)),
                        overloading_value=Decimal(str(17179869183.0)),
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=2,
                        value=Decimal(str(self.volume_channel_2)),
                        overloading_value=Decimal(str(17179869183.0)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.LOW_AMBIENT_TEMPERATURE] if self.event_low_ambient_temperature else []),
                ],
            ),
        ]
