from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, CounterType, ResourceType, IntegrationV0MessageGeneration, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_water_meter_08b_info
#
# RESULT int:        340451689
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00010100 01001010 11100001 01101001   LSB
# RESULT hex:  LE    69 e1 4a 14 00 00 00 00
#
# name                  type    size  value(int)                                                        data(bits)
# --------------------  ------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL  u7         7         105                                                           1101001
# packet_type_id.0.DFF  bool       1           0                                                          0
# battery_volts         uf6p1      6          33                                                    100001
# event_battery_low     bool       1           1                                                   1
# event_battery_warn    bool       1           1                                                  1
# reverse_flow_volume   uf12p2    12        1098                                      010001001010
# event_flow_reverse    bool       1           1                                     1
# RESERVED              u35       35           0  00000000000000000000000000000000000


class SmpmUlDeviceWaterMeter08BInfoData(Packet):
    battery_volts: float
    event_battery_low: bool
    event_battery_warn: bool
    reverse_flow_volume: float
    event_flow_reverse: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((105) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.battery_volts, (int, float))
        assert 0.0 <= data.battery_volts <= 6.3
        result |= ((int(round(float(data.battery_volts) * 10.0, 0))) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.event_battery_low, bool)
        result |= ((int(data.event_battery_low)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_battery_warn, bool)
        result |= ((int(data.event_battery_warn)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.reverse_flow_volume, (int, float))
        result |= ((int(round(float(data.reverse_flow_volume) * 100.0, 0)) & 4095) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.event_flow_reverse, bool)
        result |= ((int(data.event_flow_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceWaterMeter08BInfoData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 105 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["battery_volts"] = round(buf.shift(6) / 10.0, 1)
        result__el_tmp1["event_battery_low"] = bool(buf.shift(1))
        result__el_tmp1["event_battery_warn"] = bool(buf.shift(1))
        result__el_tmp1["reverse_flow_volume"] = round(buf.shift(12) / 100.0, 2)
        result__el_tmp1["event_flow_reverse"] = bool(buf.shift(1))
        result = SmpmUlDeviceWaterMeter08BInfoData(**result__el_tmp1)
        buf.shift(35)
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
                ],
                generation=[
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.reverse_flow_volume)),
                        overloading_value=Decimal(str(40.95)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.FLOW_REVERSE] if self.event_flow_reverse else []),
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_battery_low else []),
                    *([IntegrationV0MessageEvent.BATTERY_WARNING] if self.event_battery_warn else []),
                ],
            ),
        ]
