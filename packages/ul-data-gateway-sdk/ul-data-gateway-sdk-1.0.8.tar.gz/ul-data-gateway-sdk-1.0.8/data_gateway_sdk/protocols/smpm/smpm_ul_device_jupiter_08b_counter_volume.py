from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    CounterType, ResourceType

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet

# PACKET (64 bits)   smpm_ul_device_jupiter_08b_counter_volume
#
# RESULT int:        16140901081675726957
# RESULT bin:  MSB   11100000 00000000 00000000 00000100 00000000 00000000 00000000 01101101   LSB
# RESULT hex:  LE    6d 00 00 00 04 00 00 e0
#
# name                     type    size  value(int)                                                        data(bits)
# -----------------------  ------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL     u7         7         109                                                           1101101
# packet_type_id.0.DFF     bool       1           0                                                          0
# volume_channel_1         uf27p3    27    67108864                               100000000000000000000000000
# volume_channel_2         uf27p3    27    67108864    100000000000000000000000000
# event_reset              bool       1           1   1
# event_low_battery_level  bool       1           1  1


class SmpmUlDeviceJupiter08BCounterVolumeData(Packet):
    volume_channel_1: float
    volume_channel_2: float
    event_reset: bool
    event_low_battery_level: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((109) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.volume_channel_1, (int, float))
        result |= ((int(round(float(data.volume_channel_1) * 1000.0, 0)) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        assert isinstance(data.volume_channel_2, (int, float))
        result |= ((int(round(float(data.volume_channel_2) * 1000.0, 0)) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_low_battery_level, bool)
        result |= ((int(data.event_low_battery_level)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceJupiter08BCounterVolumeData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 109 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["volume_channel_1"] = round(buf.shift(27) / 1000.0, 3)
        result__el_tmp1["volume_channel_2"] = round(buf.shift(27) / 1000.0, 3)
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result = SmpmUlDeviceJupiter08BCounterVolumeData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.volume_channel_1)),
                        channel=1,
                        overloading_value=Decimal(str(268435455.0)),
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.volume_channel_2)),
                        channel=2,
                        overloading_value=Decimal(str(268435455.0)),
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.RESET] if self.event_reset else []),
                    *([IntegrationV0MessageEvent.BATTERY_IS_LOW] if self.event_low_battery_level else []),
                ],
            ),
        ]
