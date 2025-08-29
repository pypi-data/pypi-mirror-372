from decimal import Decimal
from datetime import timedelta, datetime, time, tzinfo
from typing import List, Any, Dict

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, JournalDataType, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, CounterType, ResourceType, \
    IntegrationV0MessageGeneration, IntegrationV0MessageSensor
from pytz import timezone

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (96 bits)   smpm_ul_device_water_meter_12b_daily
#
# RESULT int:        13275071466894698375914242147
# RESULT bin:  MSB   00101010 11100100 11100001 10111010 00110111 00100011 00000110 10110001 11101010 11100100 11000000 01100011   LSB
# RESULT hex:  LE    63 c0 e4 ea b1 06 23 37 ba e1 e4 2a
#
# name                            type       size  value(int)                                                                                        data(bits)
# ------------------------------  ---------  ----  ----------  ------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL            u7            7          99                                                                                           1100011
# packet_type_id.0.DFF            bool          1           0                                                                                          0
# days_ago                        timedelta     5           0                                                                                     00000
# event_case_was_opened           bool          1           0                                                                                    0
# event_reset                     bool          1           1                                                                                   1
# event_sensor_error              bool          1           1                                                                                  1
# direct_flow_volume              uf32p3       32   112323300                                                  00000110101100011110101011100100
# direct_flow_volume_day_ago      uf7p1         7          35                                           0100011
# event_magnet                    bool          1           0                                          0
# direct_flow_volume_2days_ago    uf7p1         7          55                                   0110111
# event_continues_consumption     bool          1           0                                  0
# temperature                     u7            7          58                           0111010
# event_temperature_limits        bool          1           1                          1
# battery_volts                   uf6p1         6          33                    100001
# event_battery_warn              bool          1           1                   1
# event_flow_speed_is_over_limit  bool          1           1                  1
# reverse_flow_volume             uf12p3       12        2788      101011100100
# event_flow_reverse              bool          1           0     0
# event_no_resource               bool          1           1    1
# event_system_error              bool          1           0   0
# RESERVED                        u1            1           0  0


class SmpmUlDeviceWaterMeter12BDailyData(Packet):
    days_ago: timedelta
    event_case_was_opened: bool
    event_reset: bool
    event_sensor_error: bool
    direct_flow_volume: float
    direct_flow_volume_day_ago: float
    event_magnet: bool
    direct_flow_volume_2days_ago: float
    event_continues_consumption: bool
    temperature: int
    event_temperature_limits: bool
    battery_volts: float
    event_battery_warn: bool
    event_flow_speed_is_over_limit: bool
    reverse_flow_volume: float
    event_flow_reverse: bool
    event_no_resource: bool
    event_system_error: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((99) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 31
        result |= ((days_ago_tmp1) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.event_case_was_opened, bool)
        result |= ((int(data.event_case_was_opened)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error, bool)
        result |= ((int(data.event_sensor_error)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.direct_flow_volume, (int, float))
        result |= ((int(round(float(data.direct_flow_volume) * 1000.0, 0)) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.direct_flow_volume_day_ago, (int, float))
        result |= ((int(round(max(min(12.7, float(data.direct_flow_volume_day_ago)), 0.0) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_magnet, bool)
        result |= ((int(data.event_magnet)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.direct_flow_volume_2days_ago, (int, float))
        result |= ((int(round(max(min(12.7, float(data.direct_flow_volume_2days_ago)), 0.0) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_continues_consumption, bool)
        result |= ((int(data.event_continues_consumption)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.temperature, int)
        assert -35 <= data.temperature <= 92
        result |= (((data.temperature + 35)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.event_temperature_limits, bool)
        result |= ((int(data.event_temperature_limits)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 6.3
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.event_battery_warn, bool)
        result |= ((int(data.event_battery_warn)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_speed_is_over_limit, bool)
        result |= ((int(data.event_flow_speed_is_over_limit)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.reverse_flow_volume, (int, float))
        result |= ((int(round(float(data.reverse_flow_volume) * 1000.0, 0)) & 4095) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.event_flow_reverse, bool)
        result |= ((int(data.event_flow_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_no_resource, bool)
        result |= ((int(data.event_no_resource)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_system_error, bool)
        result |= ((int(data.event_system_error)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(12, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceWaterMeter12BDailyData':
        result__el_tmp2: Dict[str, Any] = dict()
        if 99 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp2["days_ago"] = timedelta(seconds=buf.shift(5) * 86400)
        result__el_tmp2["event_case_was_opened"] = bool(buf.shift(1))
        result__el_tmp2["event_reset"] = bool(buf.shift(1))
        result__el_tmp2["event_sensor_error"] = bool(buf.shift(1))
        result__el_tmp2["direct_flow_volume"] = round(buf.shift(32) / 1000.0, 3)
        result__el_tmp2["direct_flow_volume_day_ago"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp2["event_magnet"] = bool(buf.shift(1))
        result__el_tmp2["direct_flow_volume_2days_ago"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp2["event_continues_consumption"] = bool(buf.shift(1))
        result__el_tmp2["temperature"] = buf.shift(7) + -35
        result__el_tmp2["event_temperature_limits"] = bool(buf.shift(1))
        result__el_tmp2["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp2["event_battery_warn"] = bool(buf.shift(1))
        result__el_tmp2["event_flow_speed_is_over_limit"] = bool(buf.shift(1))
        result__el_tmp2["reverse_flow_volume"] = round(buf.shift(12) / 1000.0, 3)
        result__el_tmp2["event_flow_reverse"] = bool(buf.shift(1))
        result__el_tmp2["event_no_resource"] = bool(buf.shift(1))
        result__el_tmp2["event_system_error"] = bool(buf.shift(1))
        result = SmpmUlDeviceWaterMeter12BDailyData(**result__el_tmp2)
        buf.shift(1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        messages = []
        error_volume = 127  # by documentation
        v = int(self.direct_flow_volume_day_ago * 10)
        c = self.direct_flow_volume - self.direct_flow_volume_day_ago
        if v != 0 and v != error_volume and c > 0:
            messages.append(IntegrationV0MessageData(
                dt=datetime.combine(received_at.astimezone(device_tz).date(), time(hour=0, minute=0, second=0), device_tz).astimezone(timezone('UTC')),
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(c)),
                        overloading_value=Decimal(str(4294967.295)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
            ))
        v2 = int(self.direct_flow_volume_2days_ago * 10)
        c2 = self.direct_flow_volume - self.direct_flow_volume_day_ago - self.direct_flow_volume_2days_ago
        if v2 != 0 and v2 != error_volume and c2 > 0 and v != error_volume:
            messages.append(IntegrationV0MessageData(
                dt=datetime.combine((received_at.astimezone(device_tz) - timedelta(days=1)).date(), time(hour=0, minute=0, second=0), device_tz).astimezone(timezone('UTC')),
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(c2)),
                        overloading_value=Decimal(str(4294967.295)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
            ))
        return [
            *messages,
            IntegrationV0MessageData(
                dt=datetime.combine(
                    (received_at.astimezone(device_tz) - self.days_ago).date(),
                    time(hour=0, minute=0, second=0),
                    device_tz,
                ).astimezone(timezone('UTC')) + timedelta(days=1) if self.days_ago.total_seconds() else received_at,
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
                        value=Decimal(str(self.direct_flow_volume)),
                        overloading_value=Decimal(str(4294967.295)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.MAGNET_WAS_DETECTED] if self.event_magnet else []),
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.FLOW_REVERSE] if self.event_flow_reverse else []),
                    *([IntegrationV0MessageEvent.ERROR_SYSTEM] if self.event_system_error else []),
                    *([IntegrationV0MessageEvent.CONTINUES_CONSUMPTION] if self.event_continues_consumption else []),
                    *([IntegrationV0MessageEvent.CASE_WAS_OPENED] if self.event_case_was_opened else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR] if self.event_sensor_error else []),
                    *([IntegrationV0MessageEvent.NO_RESOURCE] if self.event_no_resource else []),
                    *([IntegrationV0MessageEvent.FLOW_SPEED_OVER_LIMIT] if self.event_flow_speed_is_over_limit else []),
                    *([IntegrationV0MessageEvent.TEMPERATURE_LIMIT] if self.event_temperature_limits else []),
                    *([IntegrationV0MessageEvent.BATTERY_WARNING] if self.event_battery_warn else []),
                ],
                generation=[
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.reverse_flow_volume)),
                        overloading_value=Decimal(str(40.95)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
            ),
        ]
