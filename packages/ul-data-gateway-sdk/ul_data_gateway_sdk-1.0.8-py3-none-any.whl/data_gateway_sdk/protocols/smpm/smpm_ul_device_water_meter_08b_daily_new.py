from datetime import datetime, tzinfo
from decimal import Decimal
from typing import Any, List, Dict

from data_aggregator_sdk.constants.enums import SensorType, IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageSensor, \
    IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageGeneration

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_water_meter_08b_daily_new
#
# RESULT int:        9768173273944351860
# RESULT bin:  MSB   10000111 10001111 10000101 11010110 10110001 11101010 11100100 01110100   LSB
# RESULT hex:  LE    74 e4 ea b1 d6 85 8f 87
#
# name                      type    size  value(int)                                                        data(bits)
# ------------------------  ------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL      u7         7         116                                                           1110100
# packet_type_id.0.DFF      bool       1           0                                                          0
# value                     uf27p3    27   112323300                               110101100011110101011100100
# temperature               u7         7          58                        0111010
# battery_volts             uf6p1      6          33                  100001
# event_low_battery_level   bool       1           1                 1
# event_temperature_limits  bool       1           1                1
# event_reset               bool       1           1               1
# event_magnet              bool       1           1              1
# event_reverse_flow        bool       1           0             0
# value_reverse             uf11p3    11        1084  10000111100


class SmpmUlDeviceWaterMeter08BDailyNewData(Packet):
    value: float
    temperature: int
    battery_volts: float
    event_low_battery_level: bool
    event_temperature_limits: bool
    event_reset: bool
    event_magnet: bool
    event_reverse_flow: bool
    value_reverse: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((116) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value, (int, float))
        result |= ((int(round(float(data.value) * 1000.0, 0)) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        assert isinstance(data.temperature, int)
        assert -35 <= data.temperature <= 92
        result |= (((data.temperature + 35)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 6.3
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.event_low_battery_level, bool)
        result |= ((int(data.event_low_battery_level)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_temperature_limits, bool)
        result |= ((int(data.event_temperature_limits)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_magnet, bool)
        result |= ((int(data.event_magnet)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_reverse_flow, bool)
        result |= ((int(data.event_reverse_flow)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value_reverse, (int, float))
        result |= ((int(round(float(data.value_reverse) * 1000.0, 0)) & 2047) & (2 ** (11) - 1)) << size
        size += 11
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceWaterMeter08BDailyNewData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 116 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["value"] = round(buf.shift(27) / 1000.0, 3)
        result__el_tmp1["temperature"] = buf.shift(7) + -35
        result__el_tmp1["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result__el_tmp1["event_temperature_limits"] = bool(buf.shift(1))
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_magnet"] = bool(buf.shift(1))
        result__el_tmp1["event_reverse_flow"] = bool(buf.shift(1))
        result__el_tmp1["value_reverse"] = round(buf.shift(11) / 1000.0, 3)
        result = SmpmUlDeviceWaterMeter08BDailyNewData(**result__el_tmp1)
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
                        overloading_value=Decimal(str(134217.727)),
                    ),
                ],
                generation=[
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.value_reverse)),
                        overloading_value=Decimal(str(20.47)),
                    ),
                ],
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
                events=[
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.TEMPERATURE_LIMIT] if self.event_temperature_limits else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.MAGNET_WAS_DETECTED] if self.event_magnet else []),
                    *([IntegrationV0MessageEvent.FLOW_REVERSE] if self.event_reverse_flow else []),
                ],
            ),
        ]
