from decimal import Decimal
from datetime import timedelta, datetime, time, tzinfo
from typing import List, Any, Dict

from data_aggregator_sdk.constants.enums import JournalDataType, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageEvent, IntegrationV0MessageData, \
    IntegrationV0MessageConsumption, CounterType, ResourceType, IntegrationV0MessageClock, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet
from data_gateway_sdk.utils.timestamp_calculation import timestamp_calculation


# PACKET (128 bits)   smpm_ul_device_jupiter_16b_counter
#
# RESULT int:        170141183381241069172511522525825469569
# RESULT bin:  MSB   01111111 11111111 11111111 11111110 11111111 11111111 11111111 11111101 10010000 10111010 01111111 11111111 11111111 11000000 00001100 10000001   LSB
# RESULT hex:  LE    81 0c c0 ff ff 7f ba 90 fd ff ff ff fe ff ff 7f
#
# name                      type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# ------------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL      u7            7           1                                                                                                                           0000001   # noqa: E501
# packet_type_id.0.DFF      bool          1           1                                                                                                                          1
# packet_type_id.1.VAL      u2            2           0                                                                                                                        00
# packet_type_id.1.DFF      bool          1           1                                                                                                                       1
# packet_type_id.2.VAL      u2            2           1                                                                                                                     01
# packet_type_id.2.DFF      bool          1           0                                                                                                                    0
# days_ago                  timedelta     5           0                                                                                                               00000
# sync_time_days_ago        timedelta     3           0                                                                                                            000
# timestamp_s               timedelta    26    33554431                                                                                  01111111111111111111111111
# temperature               u7            7          58                                                                           0111010
# battery_volts             uf6p1         6          33                                                                     100001
# event_reset               bool          1           0                                                                    0
# event_low_battery_level   bool          1           0                                                                   0
# event_temperature_limits  bool          1           1                                                                  1
# event_battery_warn        bool          1           1                                                                 1
# event_system_error        bool          1           0                                                                0
# value_channel_1           u31          31  1073741823                                 0111111111111111111111111111111
# value_channel_2           u31          31  1073741823  0111111111111111111111111111111


class SmpmUlDeviceJupiter16BCounterData(Packet):
    days_ago: timedelta
    sync_time_days_ago: timedelta
    timestamp_s: timedelta
    temperature: int
    battery_volts: float
    event_reset: bool
    event_low_battery_level: bool
    event_temperature_limits: bool
    event_battery_warn: bool
    event_system_error: bool
    value_channel_1: int
    value_channel_2: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((1) & (2 ** (7) - 1)) << size
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
        assert isinstance(data.event_battery_warn, bool)
        result |= ((int(data.event_battery_warn)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_system_error, bool)
        result |= ((int(data.event_system_error)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value_channel_1, int)
        result |= (((data.value_channel_1) & 2147483647) & (2 ** (31) - 1)) << size
        size += 31
        assert isinstance(data.value_channel_2, int)
        result |= (((data.value_channel_2) & 2147483647) & (2 ** (31) - 1)) << size
        size += 31
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceJupiter16BCounterData':
        result__el_tmp3: Dict[str, Any] = dict()
        if 1 != buf.shift(7):
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
        result__el_tmp3["event_battery_warn"] = bool(buf.shift(1))
        result__el_tmp3["event_system_error"] = bool(buf.shift(1))
        result__el_tmp3["value_channel_1"] = buf.shift(31) + 0
        result__el_tmp3["value_channel_2"] = buf.shift(31) + 0
        result = SmpmUlDeviceJupiter16BCounterData(**result__el_tmp3)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=days_ago_calculation(received_at, device_tz, time(0, 0, 0), self.days_ago),
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
                        overloading_value=Decimal(str(2147483647.0)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=2,
                        value=Decimal(str(self.value_channel_2)),
                        overloading_value=Decimal(str(2147483647.0)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                    *([IntegrationV0MessageEvent.BATTERY_WARNING] if self.event_battery_warn else []),
                    *([IntegrationV0MessageEvent.TEMPERATURE_LIMIT] if self.event_temperature_limits else []),
                    *([IntegrationV0MessageEvent.ERROR_SYSTEM] if self.event_system_error else []),
                ],
                clock=[IntegrationV0MessageClock(value=timestamp_calculation(received_at, self.timestamp_s, timedelta(seconds=67108863)))] if self.timestamp_s else [],
            ),
        ]
