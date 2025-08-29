from decimal import Decimal
from datetime import timedelta, tzinfo, datetime
from typing import Dict, Any, List

from data_aggregator_sdk.constants.enums import SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageRelay, IntegrationV0MessageClock, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_status_info
#
# RESULT int:        114624888726607593574237117
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000000 01011110 11010000 11000011 10101011 00111110 00000001 00001110 10101100 11111000 00000011 10111101   LSB
# RESULT hex:  LE    bd 03 f8 ac 0e 01 3e ab c3 d0 5e 00 00 00 00 00
#
# name                  type       size  value(int)                                                                                                                        data(bits)
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL  u7            7          61                                                                                                                           0111101
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1
# packet_type_id.1.VAL  u2            2           3                                                                                                                        11
# packet_type_id.1.DFF  bool          1           0                                                                                                                       0
# datetime              timedelta    30   567648000                                                                                         100001110101011001111100000000
# uptime_s              timedelta    30   567648000                                                           100001110101011001111100000000
# battery_volts         uf7p1         7          33                                                    0100001
# temperature           u8            8         123                                            01111011
# relay_switch          u2            2           1                                          01
# relay_is_active       bool          1           0                                         0
# RESERVED              u39          39           0  000000000000000000000000000000000000000


class SmpmUlDeviceEnergy16BStatusInfoData(Packet):
    date_time: timedelta
    uptime_s: timedelta
    battery_volts: float
    temperature: int
    relay_switch: int
    relay_is_active: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((61) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((3) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.date_time, (int, timedelta))
        datetime_tmp1 = int(data.date_time.total_seconds() // 1 if isinstance(data.date_time, timedelta) else data.date_time // 1)
        assert 0 <= datetime_tmp1 <= 1073741823
        result |= ((datetime_tmp1) & (2 ** (30) - 1)) << size
        size += 30
        isinstance(data.uptime_s, (int, timedelta))
        value_int_tmp2 = int(data.uptime_s.total_seconds() // 1 if isinstance(data.uptime_s, timedelta) else data.uptime_s // 1) & 1073741823
        result |= ((value_int_tmp2) & (2 ** (30) - 1)) << size
        size += 30
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 12.7
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.temperature, int)
        assert -100 <= data.temperature <= 155
        result |= (((data.temperature + 100)) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.relay_switch, int)
        assert 0 <= data.relay_switch <= 3
        result |= ((data.relay_switch) & (2 ** (2) - 1)) << size
        size += 2
        assert isinstance(data.relay_is_active, bool)
        result |= ((int(data.relay_is_active)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BStatusInfoData':
        result__el_tmp3: Dict[str, Any] = dict()
        if 61 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 3 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp3["date_time"] = timedelta(seconds=buf.shift(30) * 1)
        result__el_tmp3["uptime_s"] = timedelta(seconds=buf.shift(30) * 1)
        result__el_tmp3["battery_volts"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp3["temperature"] = buf.shift(8) + -100
        result__el_tmp3["relay_switch"] = buf.shift(2) + 0
        result__el_tmp3["relay_is_active"] = bool(buf.shift(1))
        result = SmpmUlDeviceEnergy16BStatusInfoData(**result__el_tmp3)
        buf.shift(39)
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
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.uptime_s.total_seconds())),
                        sensor_type=SensorType.UPTIME,
                    ),
                ],
                relay=[
                    IntegrationV0MessageRelay(value=self.relay_is_active),
                ],
                clock=[
                    IntegrationV0MessageClock(value=datetime(year=2020, month=1, day=1) + self.date_time),
                ],
            ),
        ]
