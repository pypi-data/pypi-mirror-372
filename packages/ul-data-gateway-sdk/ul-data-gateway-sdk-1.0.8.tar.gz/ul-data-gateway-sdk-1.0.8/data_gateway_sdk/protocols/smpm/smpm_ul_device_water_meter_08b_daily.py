from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, time, tzinfo
from pytz import timezone

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, \
    IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_water_meter_08b_daily
#
# RESULT int:        8663416082350662760
# RESULT bin:  MSB   01111000 00111010 10100011 00000110 10110001 11101010 11100100 01101000   LSB
# RESULT hex:  LE    68 e4 ea b1 06 a3 3a 78
#
# name                                 type    size  value(int)                                                        data(bits)   # noqa: E501
# -----------------------------------  ------  ----  ----------  ----------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL                 u7         7         104                                                           1101000   # noqa: E501
# packet_type_id.0.DFF                 bool       1           0                                                          0          # noqa: E501
# direct_flow_volume                   uf32p3    32   112323300                          00000110101100011110101011100100           # noqa: E501
# direct_flow_volume_day_ago           uf7p1      7          35                   0100011
# event_battery_or_temperature_limits  bool       1           1                  1
# temperature                          u7         7          58           0111010
# event_magnet                         bool       1           0          0
# event_continues_consumption          bool       1           0         0
# event_case_was_opened                bool       1           0        0
# event_system_error                   bool       1           0       0
# event_reset                          bool       1           1      1
# event_sensor_error                   bool       1           1     1
# event_no_resource                    bool       1           1    1
# event_flow_speed_is_over_limit       bool       1           1   1
# event_flow_reverse                   bool       1           0  0


class SmpmUlDeviceWaterMeter08BDailyData(Packet):
    direct_flow_volume: float
    direct_flow_volume_day_ago: float
    event_battery_or_temperature_limits: bool
    temperature: int
    event_magnet: bool
    event_continues_consumption: bool
    event_case_was_opened: bool
    event_system_error: bool
    event_reset: bool
    event_sensor_error: bool
    event_no_resource: bool
    event_flow_speed_is_over_limit: bool
    event_flow_reverse: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((104) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.direct_flow_volume, (int, float))
        result |= ((int(round(float(data.direct_flow_volume) * 1000.0, 0)) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.direct_flow_volume_day_ago, (int, float))
        result |= ((int(round(max(min(12.7, float(data.direct_flow_volume_day_ago)), 0.0) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_battery_or_temperature_limits, bool)
        result |= ((int(data.event_battery_or_temperature_limits)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.temperature, int)
        assert -35 <= data.temperature <= 92
        result |= (((data.temperature + 35)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_magnet, bool)
        result |= ((int(data.event_magnet)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_continues_consumption, bool)
        result |= ((int(data.event_continues_consumption)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_case_was_opened, bool)
        result |= ((int(data.event_case_was_opened)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_system_error, bool)
        result |= ((int(data.event_system_error)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error, bool)
        result |= ((int(data.event_sensor_error)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_no_resource, bool)
        result |= ((int(data.event_no_resource)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_speed_is_over_limit, bool)
        result |= ((int(data.event_flow_speed_is_over_limit)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_reverse, bool)
        result |= ((int(data.event_flow_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceWaterMeter08BDailyData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 104 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["direct_flow_volume"] = round(buf.shift(32) / 1000.0, 3)
        result__el_tmp1["direct_flow_volume_day_ago"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp1["event_battery_or_temperature_limits"] = bool(buf.shift(1))
        result__el_tmp1["temperature"] = buf.shift(7) + -35
        result__el_tmp1["event_magnet"] = bool(buf.shift(1))
        result__el_tmp1["event_continues_consumption"] = bool(buf.shift(1))
        result__el_tmp1["event_case_was_opened"] = bool(buf.shift(1))
        result__el_tmp1["event_system_error"] = bool(buf.shift(1))
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_sensor_error"] = bool(buf.shift(1))
        result__el_tmp1["event_no_resource"] = bool(buf.shift(1))
        result__el_tmp1["event_flow_speed_is_over_limit"] = bool(buf.shift(1))
        result__el_tmp1["event_flow_reverse"] = bool(buf.shift(1))
        result = SmpmUlDeviceWaterMeter08BDailyData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        messages = []
        v = int(self.direct_flow_volume_day_ago * 10)
        c = self.direct_flow_volume - self.direct_flow_volume_day_ago
        if v != 0 and v != 127 and c > 0:
            messages.append(IntegrationV0MessageData(
                dt=datetime.combine(received_at.astimezone(device_tz).date(), time(hour=0, minute=0, second=0), device_tz).astimezone(timezone('UTC')),
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(c)),
                        overloading_value=Decimal(str(4294967.295)),
                    ),
                ],
            ))
        return [
            *messages,
            IntegrationV0MessageData(
                dt=received_at,
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(self.direct_flow_volume)),
                        overloading_value=Decimal(str(4294967.295)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.MAGNET_WAS_DETECTED] if self.event_magnet else []),
                    *([IntegrationV0MessageEvent.BATTERY_OR_TEMPERATURE_LIMITS] if self.event_battery_or_temperature_limits else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.FLOW_REVERSE] if self.event_flow_reverse else []),
                    *([IntegrationV0MessageEvent.ERROR_SYSTEM] if self.event_system_error else []),
                    *([IntegrationV0MessageEvent.CONTINUES_CONSUMPTION] if self.event_continues_consumption else []),
                    *([IntegrationV0MessageEvent.CASE_WAS_OPENED] if self.event_case_was_opened else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR] if self.event_sensor_error else []),
                    *([IntegrationV0MessageEvent.NO_RESOURCE] if self.event_no_resource else []),
                    *([IntegrationV0MessageEvent.FLOW_SPEED_OVER_LIMIT] if self.event_flow_speed_is_over_limit else []),
                ],
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.temperature)),
                        sensor_type=SensorType.TEMPERATURE,
                    ),
                ],
            ),
        ]
