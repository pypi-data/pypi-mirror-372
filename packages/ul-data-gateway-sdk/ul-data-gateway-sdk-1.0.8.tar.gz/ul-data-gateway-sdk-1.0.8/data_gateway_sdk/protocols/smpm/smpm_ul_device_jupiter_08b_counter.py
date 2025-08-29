from decimal import Decimal
from typing import List, Any, Dict
from datetime import datetime, tzinfo
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    CounterType, ResourceType

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet

# PACKET (64 bits)   smpm_ul_device_jupiter_08b_counter
#
# RESULT int:        16140901047315988325
# RESULT bin:  MSB   11011111 11111111 11111111 11111011 11111111 11111111 11111111 01100101   LSB
# RESULT hex:  LE    65 ff ff ff fb ff ff df
#
# name                     type  size  value(int)                                                        data(bits)
# -----------------------  ----  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL     u7       7         101                                                           1100101
# packet_type_id.0.DFF     bool     1           0                                                          0
# value_channel_1          u27     27    67108863                               011111111111111111111111111
# value_channel_2          u27     27    67108863    011111111111111111111111111
# event_reset              bool     1           1   1
# event_low_battery_level  bool     1           1  1


class SmpmUlDeviceJupiter08BCounterData(Packet):
    value_channel_1: int
    value_channel_2: int
    event_reset: bool
    event_low_battery_level: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((101) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.value_channel_1, int)
        result |= (((data.value_channel_1) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        assert isinstance(data.value_channel_2, int)
        result |= (((data.value_channel_2) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        assert isinstance(data.event_reset, bool)
        result |= ((int(data.event_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_low_battery_level, bool)
        result |= ((int(data.event_low_battery_level)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceJupiter08BCounterData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 101 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["value_channel_1"] = buf.shift(27) + 0
        result__el_tmp1["value_channel_2"] = buf.shift(27) + 0
        result__el_tmp1["event_reset"] = bool(buf.shift(1))
        result__el_tmp1["event_low_battery_level"] = bool(buf.shift(1))
        result = SmpmUlDeviceJupiter08BCounterData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.value_channel_1)),
                        channel=1,
                        overloading_value=Decimal(str(268435455.0)),
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        value=Decimal(str(self.value_channel_2)),
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
