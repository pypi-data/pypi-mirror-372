from decimal import Decimal
from datetime import timedelta, datetime, time, tzinfo
from typing import List, Any, Dict

from data_aggregator_sdk.constants.enums import JournalDataType, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageEvent, IntegrationV0MessageData, \
    IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageGeneration, IntegrationV0MessageClock, IntegrationV0MessageSensor
from pytz import timezone

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet
from data_gateway_sdk.utils.timestamp_calculation import timestamp_calculation


# PACKET (128 bits)   smpm_ul_device_gaz_flow_16b_daily
#
# RESULT int:        10686500159077697549616551971514223746
# RESULT bin:  MSB   00001000 00001010 00100101 00100011 00000110 10110001 11101010 11100100 10010000 10111010 01111111 11111111 11111111 11000000 00001100 10000010   LSB
# RESULT hex:  LE    82 0c c0 ff ff 7f ba 90 e4 ea b1 06 23 25 0a 08
#
# name                            type       size  value(int)                                                                                                                        data(bits)     # noqa: E501
# ------------------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------     # noqa: E501
# packet_type_id.0.VAL            u7            7           2                                                                                                                           0000010     # noqa: E501
# packet_type_id.0.DFF            bool          1           1                                                                                                                          1            # noqa: E501
# packet_type_id.1.VAL            u2            2           0                                                                                                                        00             # noqa: E501
# packet_type_id.1.DFF            bool          1           1                                                                                                                       1               # noqa: E501
# packet_type_id.2.VAL            u2            2           1                                                                                                                     01
# packet_type_id.2.DFF            bool          1           0                                                                                                                    0
# days_ago                        timedelta     5           0                                                                                                               00000
# sync_time_days_ago              timedelta     3           0                                                                                                            000
# timestamp_s                     timedelta    26    33554431                                                                                  01111111111111111111111111
# temperature                     u7            7          58                                                                           0111010
# battery_volts                   uf6p1         6          33                                                                     100001
# event_reset                     bool          1           0                                                                    0
# event_low_battery_level         bool          1           0                                                                   0
# event_temperature_limits        bool          1           1                                                                  1
# direct_flow_volume              uf32p3       32   112323300                                  00000110101100011110101011100100
# direct_flow_volume_day_ago      uf7p1         7          35                           0100011
# reverse_flow_volume             uf12p2       12        1098               010001001010
# event_battery_warn              bool          1           1              1
# event_system_error              bool          1           0             0
# event_flow_reverse              bool          1           0            0
# event_flow_speed_is_over_limit  bool          1           0           0
# event_sensor_error              bool          1           0          0
# event_sensor_error_temperature  bool          1           0         0
# event_case_was_opened           bool          1           0        0
# event_continuous_consumption    bool          1           0       0
# event_no_resource               bool          1           1      1
# RESERVED                        u4            4           0  0000


class SmpmUlDeviceGazFlow16BDailyData(Packet):
    days_ago: timedelta
    sync_time_days_ago: timedelta
    timestamp_s: timedelta
    temperature: int
    battery_volts: float
    event_reset: bool
    event_low_battery_level: bool
    event_temperature_limits: bool
    direct_flow_volume: float
    direct_flow_volume_day_ago: float
    reverse_flow_volume: float
    event_battery_warn: bool
    event_system_error: bool
    event_flow_reverse: bool
    event_flow_speed_is_over_limit: bool
    event_sensor_error: bool
    event_sensor_error_temperature: bool
    event_case_was_opened: bool
    event_continuous_consumption: bool
    event_no_resource: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((2) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 31
        result |= ((days_ago_tmp1) & (2 ** (5) - 1)) << size
        size += 5
        isinstance(data.sync_time_days_ago, (int, timedelta))
        result |= ((max(min(7, int(data.sync_time_days_ago.total_seconds() // 86400 if isinstance(data.sync_time_days_ago, timedelta) else data.sync_time_days_ago // 86400)), 0)) & (2 ** (3) - 1)) << size    # noqa: E501
        size += 3
        isinstance(data.timestamp_s, (int, timedelta))
        value_int_tmp2 = int(data.timestamp_s.total_seconds() // 1 if isinstance(data.timestamp_s, timedelta) else data.timestamp_s // 1) & 67108863
        result |= ((value_int_tmp2) & (2 ** (26) - 1)) << size
        size += 26
        assert isinstance(data.temperature, int)
        assert -35 <= data.temperature <= 92
        result |= (((data.temperature + 35)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 6.3
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_low_battery_level, bool)
        result |= ((int(data.event_low_battery_level)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_temperature_limits, bool)
        result |= ((int(data.event_temperature_limits)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.direct_flow_volume, (int, float))
        result |= ((int(round(float(data.direct_flow_volume) * 1000.0, 0)) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.direct_flow_volume_day_ago, (int, float))
        result |= ((int(round(max(min(12.7, float(data.direct_flow_volume_day_ago)), 0.0) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.reverse_flow_volume, (int, float))
        result |= ((int(round(float(data.reverse_flow_volume) * 100.0, 0)) & 4095) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.event_battery_warn, bool)
        result |= ((int(data.event_battery_warn)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_system_error, bool)
        result |= ((int(data.event_system_error)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_reverse, bool)
        result |= ((int(data.event_flow_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_flow_speed_is_over_limit, bool)
        result |= ((int(data.event_flow_speed_is_over_limit)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error, bool)
        result |= ((int(data.event_sensor_error)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_sensor_error_temperature, bool)
        result |= ((int(data.event_sensor_error_temperature)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_case_was_opened, bool)
        result |= ((int(data.event_case_was_opened)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_continuous_consumption, bool)
        result |= ((int(data.event_continuous_consumption)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_no_resource, bool)
        result |= ((int(data.event_no_resource)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceGazFlow16BDailyData':
        result__el_tmp3: Dict[str, Any] = dict()
        if 2 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp3["days_ago"] = timedelta(seconds=buf.shift(5) * 86400)
        result__el_tmp3["sync_time_days_ago"] = timedelta(seconds=buf.shift(3) * 86400)
        result__el_tmp3["timestamp_s"] = timedelta(seconds=buf.shift(26) * 1)
        result__el_tmp3["temperature"] = buf.shift(7) + -35
        result__el_tmp3["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp3["event_reset"] = bool(buf.shift(1))
        result__el_tmp3["event_low_battery_level"] = bool(buf.shift(1))
        result__el_tmp3["event_temperature_limits"] = bool(buf.shift(1))
        result__el_tmp3["direct_flow_volume"] = round(buf.shift(32) / 1000.0, 3)
        result__el_tmp3["direct_flow_volume_day_ago"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp3["reverse_flow_volume"] = round(buf.shift(12) / 100.0, 2)
        result__el_tmp3["event_battery_warn"] = bool(buf.shift(1))
        result__el_tmp3["event_system_error"] = bool(buf.shift(1))
        result__el_tmp3["event_flow_reverse"] = bool(buf.shift(1))
        result__el_tmp3["event_flow_speed_is_over_limit"] = bool(buf.shift(1))
        result__el_tmp3["event_sensor_error"] = bool(buf.shift(1))
        result__el_tmp3["event_sensor_error_temperature"] = bool(buf.shift(1))
        result__el_tmp3["event_case_was_opened"] = bool(buf.shift(1))
        result__el_tmp3["event_continuous_consumption"] = bool(buf.shift(1))
        result__el_tmp3["event_no_resource"] = bool(buf.shift(1))
        result = SmpmUlDeviceGazFlow16BDailyData(**result__el_tmp3)
        buf.shift(4)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        messages = []
        error_volume = 127  # by documentation
        v = int(self.direct_flow_volume_day_ago * 10)
        c = self.direct_flow_volume - self.direct_flow_volume_day_ago
        if v != 0 and v != error_volume and c > 0:
            messages.append(IntegrationV0MessageData(
                dt=datetime.combine(received_at.astimezone(device_tz).date(), time(0)).astimezone(timezone('UTC')),
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
        return [
            *messages,
            IntegrationV0MessageData(
                dt=days_ago_calculation(received_at, device_tz, time(0), self.days_ago),
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
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.TEMPERATURE_LIMIT] if self.event_temperature_limits else []),
                    *([IntegrationV0MessageEvent.BATTERY_WARNING] if self.event_battery_warn else []),
                    *([IntegrationV0MessageEvent.ERROR_SYSTEM] if self.event_system_error else []),
                    *([IntegrationV0MessageEvent.FLOW_REVERSE] if self.event_flow_reverse else []),
                    *([IntegrationV0MessageEvent.FLOW_SPEED_OVER_LIMIT] if self.event_flow_speed_is_over_limit else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR] if self.event_sensor_error else []),
                    *([IntegrationV0MessageEvent.ERROR_SENSOR_TEMPERATURE] if self.event_sensor_error_temperature else []),
                    *([IntegrationV0MessageEvent.CASE_WAS_OPENED] if self.event_case_was_opened else []),
                    *([IntegrationV0MessageEvent.CONTINUES_CONSUMPTION] if self.event_continuous_consumption else []),
                    *([IntegrationV0MessageEvent.NO_RESOURCE] if self.event_no_resource else []),
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
                clock=[IntegrationV0MessageClock(value=timestamp_calculation(received_at, self.timestamp_s, timedelta(seconds=67108863)))] if self.timestamp_s else [],
            ),
        ]
