from decimal import Decimal
from datetime import timedelta, datetime, tzinfo
from typing import List, Any, Dict
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, \
    IntegrationV0MessageRelay, IntegrationV0MessageClock, IntegrationV0MessageSensor
from data_aggregator_sdk.constants.enums import SensorType
from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_info
#
# RESULT int:        38094212464183996
# RESULT bin:  MSB   00000000000000000000000000000000000000000000000000000000000000000000000010000111010101100111110000000001111011010000101010111100   LSB                             # noqa: E501
# RESULT hex:  LE    bc 0a ed 01 7c 56 87 00 00 00 00 00 00 00 00 00
#
#
# name                  type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7            7          60                                                                                                                           0111100   # noqa: E501
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1          # noqa: E501
# packet_type_id.1.VAL  u2            2           2                                                                                                                        10           # noqa: E501
# packet_type_id.1.DFF  bool          1           0                                                                                                                       0             # noqa: E501
# battery_volts         uf7p1         7          33                                                                                                                0100001              # noqa: E501
# temperature           u8            8         123                                                                                                        01111011                     # noqa: E501
# datetime              timedelta    31   567648000                                                                         0100001110101011001111100000000                             # noqa: E501
# relay_is_active       bool          1           0                                                                        0                                                            # noqa: E501
# RESERVED              u70          70           0  0000000000000000000000000000000000000000000000000000000000000000000000                                                             # noqa: E501


class SmpmUlDeviceEnergy16BInfoData(Packet):
    battery_volts: float
    temperature: int
    date_time: timedelta
    relay_is_active: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((60) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((2) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 12.7
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.temperature, int)
        assert -100 <= data.temperature <= 155
        result |= (((data.temperature + 100)) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.date_time, (int, timedelta))
        datetime_tmp1 = int(data.date_time.total_seconds() // 1 if isinstance(data.date_time, timedelta) else data.date_time // 1)
        assert 0 <= datetime_tmp1 <= 2147483647
        result |= ((datetime_tmp1) & (2 ** (31) - 1)) << size
        size += 31
        assert isinstance(data.relay_is_active, bool)
        result |= ((int(data.relay_is_active)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BInfoData':
        result__el_tmp2: Dict[str, Any] = dict()
        if 60 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 2 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp2["battery_volts"] = round(buf.shift(7) / 10.0, 1)
        result__el_tmp2["temperature"] = buf.shift(8) + -100
        result__el_tmp2["date_time"] = timedelta(seconds=buf.shift(31) * 1)
        result__el_tmp2["relay_is_active"] = bool(buf.shift(1))
        result = SmpmUlDeviceEnergy16BInfoData(**result__el_tmp2)
        buf.shift(70)
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
                relay=[
                    IntegrationV0MessageRelay(
                        value=self.relay_is_active,
                    ),
                ],
                clock=[
                    IntegrationV0MessageClock(
                        value=datetime(year=2020, month=1, day=1) + self.date_time,
                    ),
                ],
            ),
        ]
