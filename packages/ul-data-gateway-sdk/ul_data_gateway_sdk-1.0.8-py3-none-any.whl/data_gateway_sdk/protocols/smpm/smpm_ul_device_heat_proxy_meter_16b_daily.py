from decimal import Decimal
from datetime import datetime, tzinfo
from typing import Any, Dict, List

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, CounterType, ResourceType, \
    BatteryId, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_heat_proxy_meter_16b_daily
#
# RESULT int:        13453363668248021446286294801998980
# RESULT bin:  MSB   00000000 00000010 10010111 01001101 01010010 10000000 00000000 00000011 00000000 00000000 00001100 11100100 00000000 00000000 01100100 10000100   LSB
# RESULT hex:  LE    84 64 00 00 e4 0c 00 00 03 00 80 52 4d 97 02 00
#
# name                       type    size  value(int)                                                                                                                        data(bits)     # noqa: E501
# -------------------------  ------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------     # noqa: E501
# packet_type_id.0.VAL       u7         7           4                                                                                                                           0000100     # noqa: E501
# packet_type_id.0.DFF       bool       1           1                                                                                                                          1
# packet_type_id.1.VAL       u2         2           0                                                                                                                        00
# packet_type_id.1.DFF       bool       1           1                                                                                                                       1
# packet_type_id.2.VAL       u2         2           0                                                                                                                     00
# packet_type_id.2.DFF       bool       1           1                                                                                                                    1
# packet_type_id.3.VAL       u2         2           1                                                                                                                  01
# packet_type_id.3.DFF       bool       1           0                                                                                                                 0
# UNUSED                     -         15           0                                                                                                  000000000000000
# value                      uf27p3    27        3300                                                                       000000000000000110011100100
# UNUSED                     -          5           0                                                                  00000
# uptime_min                 u22       22           3                                            0000000000000000000011
# meter_battery_volts        uf9p2      9         330                                   101001010
# UNUSED                     -          1           0                                  0
# capacitor_volts            uf9p2      9         333                         101001101
# radio_proxy_battery_volts  uf9p2      9         331                101001011
# error_meter_sync           bool       1           0               0
# error_reset                bool       1           0              0
# RESERVED                   u12       12           0  000000000000


class SmpmUlDeviceHeatProxyMeter16BDailyData(Packet):
    value: float
    uptime_min: int
    meter_battery_volts: float
    capacitor_volts: float
    radio_proxy_battery_volts: float
    error_meter_sync: bool
    error_reset: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((4) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (2) - 1)) << size
        size += 2
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
        result |= ((0) & (2 ** (15) - 1)) << size
        size += 15
        assert isinstance(data.value, (int, float))
        result |= ((int(round(float(data.value) * 1000.0, 0)) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        result |= ((0) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.uptime_min, int)
        result |= (((data.uptime_min) & 4194303) & (2 ** (22) - 1)) << size
        size += 22
        assert isinstance(data.meter_battery_volts, (int, float))
        result |= ((int(round(max(min(5.11, float(data.meter_battery_volts)), 0.0) * 100.0, 0))) & (2 ** (9) - 1)) << size
        size += 9
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.capacitor_volts, (int, float))
        result |= ((int(round(max(min(5.11, float(data.capacitor_volts)), 0.0) * 100.0, 0))) & (2 ** (9) - 1)) << size
        size += 9
        assert isinstance(data.radio_proxy_battery_volts, (int, float))
        result |= ((int(round(max(min(5.11, float(data.radio_proxy_battery_volts)), 0.0) * 100.0, 0))) & (2 ** (9) - 1)) << size
        size += 9
        assert isinstance(data.error_meter_sync, bool)
        result |= ((int(data.error_meter_sync)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_reset, bool)
        result |= ((int(data.error_reset)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceHeatProxyMeter16BDailyData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 4 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(2):
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
        buf.shift(15)
        result__el_tmp1["value"] = round(buf.shift(27) / 1000.0, 3)
        buf.shift(5)
        result__el_tmp1["uptime_min"] = buf.shift(22) + 0
        result__el_tmp1["meter_battery_volts"] = round(buf.shift(9) / 100.0, 2)
        buf.shift(1)
        result__el_tmp1["capacitor_volts"] = round(buf.shift(9) / 100.0, 2)
        result__el_tmp1["radio_proxy_battery_volts"] = round(buf.shift(9) / 100.0, 2)
        result__el_tmp1["error_meter_sync"] = bool(buf.shift(1))
        result__el_tmp1["error_reset"] = bool(buf.shift(1))
        result = SmpmUlDeviceHeatProxyMeter16BDailyData(**result__el_tmp1)
        buf.shift(12)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        if self.error_meter_sync:
            return [
                IntegrationV0MessageData(
                    dt=received_at,
                    sensors=[
                        IntegrationV0MessageSensor(
                            value=Decimal(str(self.capacitor_volts)),
                            sensor_type=SensorType.BATTERY,
                            sensor_id=BatteryId.CAPACITOR,
                        ),
                        IntegrationV0MessageSensor(
                            value=Decimal(str(self.radio_proxy_battery_volts)),
                            sensor_type=SensorType.BATTERY,
                            sensor_id=BatteryId.RADIO_MODULE,
                        ),
                    ],
                    events=[
                        *([IntegrationV0MessageEvent.ERROR_RESET] if self.error_reset else []),
                        *([IntegrationV0MessageEvent.ERROR_METER_SYNC] if self.error_meter_sync else []),
                    ],
                ),
            ]
        return [
            IntegrationV0MessageData(
                dt=received_at,
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.meter_battery_volts)),
                        sensor_type=SensorType.BATTERY,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.capacitor_volts)),
                        sensor_type=SensorType.BATTERY,
                        sensor_id=BatteryId.CAPACITOR,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.radio_proxy_battery_volts)),
                        sensor_type=SensorType.BATTERY,
                        sensor_id=BatteryId.RADIO_MODULE,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.uptime_min * 60)),
                        sensor_type=SensorType.UPTIME,
                        channel_id=1,
                    ),
                ],
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(self.value)),
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        overloading_value=Decimal(str(134217.727)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.ERROR_RESET] if self.error_reset else []),
                    *([IntegrationV0MessageEvent.ERROR_METER_SYNC] if self.error_meter_sync else []),
                ],
            ),
        ]
