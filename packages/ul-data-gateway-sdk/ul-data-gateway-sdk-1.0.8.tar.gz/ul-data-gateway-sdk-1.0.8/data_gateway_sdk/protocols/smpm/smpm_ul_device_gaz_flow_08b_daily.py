from datetime import datetime, tzinfo
from decimal import Decimal
from typing import List, Any, Dict

from data_aggregator_sdk.constants.enums import SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageEvent, IntegrationV0MessageData, \
    IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_gaz_flow_08b_daily
#
# RESULT int:        9423942916432996
# RESULT bin:  MSB   00000000 00100001 01111011 00000110 10110001 11101010 11100100 01100100   LSB
# RESULT hex:  LE    64 e4 ea b1 06 7b 21 00
#
#
# name                            type    size  value(int)                                                        data(bits)
# --------------------------------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL            u7         7         100                                                           1100100
# packet_type_id.0.DFF            bool       1           0                                                          0
# cumulative_volume               uf32p3    32   112323300                          00000110101100011110101011100100
# temperature                     u8         8         123                  01111011
# battery_volts                   uf7p1      7          33           0100001
# event_reset                     bool       1           0          0
# event_case_was_opened           bool       1           0         0
# event_flow_reverse              bool       1           0        0
# event_flow_speed_is_over_limit  bool       1           0       0
# event_sensor_error_measurement  bool       1           0      0
# event_sensor_error_temperature  bool       1           0     0
# event_low_battery_level         bool       1           0    0
# event_system_error              bool       1           0   0
# RESERVED                        u1         1           0  0


class SmpmUlDeviceGazFlow08BDailyData(Packet):
    cumulative_volume: float
    temperature: int
    battery_volts: float
    event_reset: bool
    event_case_was_opened: bool
    event_flow_reverse: bool
    event_flow_speed_is_over_limit: bool
    event_sensor_error_measurement: bool
    event_sensor_error_temperature: bool
    event_low_battery_level: bool
    event_system_error: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((100) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.cumulative_volume, (int, float))
        result |= ((int(round(float(data.cumulative_volume) * 1000.0, 0)) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.temperature, int)
        assert -100 <= data.temperature <= 155
        result |= (((data.temperature + 100)) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 12.7
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_case_was_opened, bool)
        result |= ((int(data.event_case_was_opened)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_reverse, bool)
        result |= ((int(data.event_flow_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_speed_is_over_limit, bool)
        result |= ((int(data.event_flow_speed_is_over_limit)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error_measurement, bool)
        result |= ((int(data.event_sensor_error_measurement)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error_temperature, bool)
        result |= ((int(data.event_sensor_error_temperature)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_low_battery_level, bool)
        result |= ((int(data.event_low_battery_level)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_system_error, bool)
        result |= ((int(data.event_system_error)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceGazFlow08BDailyData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 100 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["cumulative_volume"] = round(buf.shift(32) / 1000.0, 3)
        result__el_tmp1["temperature"] = buf.shift(8) + -100
        result__el_tmp1["battery_volts"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_case_was_opened"] = bool(buf.shift(1))
        result__el_tmp1["event_flow_reverse"] = bool(buf.shift(1))
        result__el_tmp1["event_flow_speed_is_over_limit"] = bool(buf.shift(1))
        result__el_tmp1["event_sensor_error_measurement"] = bool(buf.shift(1))
        result__el_tmp1["event_sensor_error_temperature"] = bool(buf.shift(1))
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result__el_tmp1["event_system_error"] = bool(buf.shift(1))
        result = SmpmUlDeviceGazFlow08BDailyData(**result__el_tmp1)
        buf.shift(1)
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
                        value=Decimal(str(self.cumulative_volume)),
                        overloading_value=Decimal(str(4294967.295)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.CASE_WAS_OPENED] if self.event_case_was_opened else []),
                    *([IntegrationV0MessageEvent.TEMPERATURE_LIMIT] if self.event_sensor_error_temperature else []),
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.FLOW_REVERSE] if self.event_flow_reverse else []),
                    *([IntegrationV0MessageEvent.FLOW_SPEED_OVER_LIMIT] if self.event_flow_speed_is_over_limit else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR_MEASUREMENT] if self.event_sensor_error_measurement else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR_TEMPERATURE] if self.event_system_error else []),
                ],
            ),
        ]
