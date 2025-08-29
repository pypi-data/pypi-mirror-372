from typing import Dict, List, Any
from datetime import datetime, tzinfo

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_magnet
#
# RESULT int:        81
# RESULT bin:  MSB   0000000000000000000000000000000000000000000000000000000001010001   LSB
# RESULT hex:  LE    51 00 00 00 00 00 00 00
#
#
# name      type  size  value(int)                                                        data(bits)
# --------------------------------------------------------------------------------------------------
# pack_id   u8       8          81                                                          01010001
# RESERVED  u56     56           0  00000000000000000000000000000000000000000000000000000000


class Water5DeviceMagnetData(Packet):
    def serialize(self) -> bytes:
        result = 0
        size = 0
        result |= ((81) & (2 ** (8) - 1)) << size
        size += 8
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceMagnetData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 81 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        buf.shift(56)
        result = Water5DeviceMagnetData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                events=[IntegrationV0MessageEvent.MAGNET_WAS_DETECTED],
            ),
        ]
