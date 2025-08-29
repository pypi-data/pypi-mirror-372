from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (32 bits)   smpm_ul_device_water_meter_04b_event
#
# RESULT int:        104521996
# RESULT bin:  MSB   00000110 00111010 11100001 00001100   LSB
# RESULT hex:  LE    0c e1 3a 06
#
# name                      type   size  value(int)                        data(bits)
# ------------------------  -----  ----  ----------  --------------------------------
# packet_type_id.0.VAL      u7        7          12                           0001100
# packet_type_id.0.DFF      bool      1           0                          0
# battery_volts             uf6p1     6          33                    100001
# event_low_battery_level   bool      1           1                   1
# event_temperature_limits  bool      1           1                  1
# temperature               u7        7          58           0111010
# event_case_was_opened     bool      1           0          0
# event_magnet              bool      1           0         0
# event_reset               bool      1           1        1
# event_sensor_error        bool      1           1       1
# RESERVED                  u5        5           0  00000


class SmpmUlDeviceWaterMeter04BEventData(Packet):
    battery_volts: float
    event_low_battery_level: bool
    event_temperature_limits: bool
    temperature: int
    event_case_was_opened: bool
    event_magnet: bool
    event_reset: bool
    event_sensor_error: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((12) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
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
        assert isinstance(data.temperature, int)
        assert -35 <= data.temperature <= 92
        result |= (((data.temperature + 35)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_case_was_opened, bool)
        result |= ((int(data.event_case_was_opened)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_magnet, bool)
        result |= ((int(data.event_magnet)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error, bool)
        result |= ((int(data.event_sensor_error)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(4, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceWaterMeter04BEventData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 12 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result__el_tmp1["event_temperature_limits"] = bool(buf.shift(1))
        result__el_tmp1["temperature"] = buf.shift(7) + -35
        result__el_tmp1["event_case_was_opened"] = bool(buf.shift(1))
        result__el_tmp1["event_magnet"] = bool(buf.shift(1))
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_sensor_error"] = bool(buf.shift(1))
        result = SmpmUlDeviceWaterMeter04BEventData(**result__el_tmp1)
        buf.shift(5)
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
                events=[
                    *([IntegrationV0MessageEvent.MAGNET_WAS_DETECTED] if self.event_magnet else []),
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.CASE_WAS_OPENED] if self.event_case_was_opened else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR] if self.event_sensor_error else []),
                    *([IntegrationV0MessageEvent.TEMPERATURE_LIMIT] if self.event_temperature_limits else []),
                ],
            ),
        ]
