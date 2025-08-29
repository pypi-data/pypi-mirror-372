from datetime import datetime, tzinfo
from enum import IntEnum, unique
from typing import List, Any, Dict

from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_ul_device_dl_answer
#
# RESULT int:        540431955267682563
# RESULT bin:  MSB   00000111 01111111 11111111 11111111 11111111 00000000 00000001 00000011   LSB
# RESULT hex:  LE    03 01 00 ff ff ff 7f 07
#
# name                  type                                      size  value(int)                                                        data(bits)
# --------------------  ----------------------------------------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL  u7                                           7           3                                                           0000011
# packet_type_id.0.DFF  bool                                         1           0                                                          0
# downlink_packet_id    SmpmUlDeviceDlAnswerDataDownlinkPacketId    16           1                                          0000000000000001
# downlink_packet_crc   u32                                         32  2147483647          01111111111111111111111111111111
# answer_packets_count  u4                                           4           7      0111
# RESERVED              u4                                           4           0  0000


@unique
class SmpmUlDeviceDlAnswerDataDownlinkPacketId(IntEnum):
    GET_ECHO = 1
    SET_CLOCK = 2
    GET_DATA_SHORT = 128
    GET_DATA_LONG = 129
    SET_REGULAR_DATA_SENDING = 150
    SET_RELAY = 170


class SmpmUlDeviceDlAnswerData(Packet):
    downlink_packet_id: SmpmUlDeviceDlAnswerDataDownlinkPacketId
    downlink_packet_crc: int
    answer_packets_count: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((3) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.downlink_packet_id, SmpmUlDeviceDlAnswerDataDownlinkPacketId)
        result |= ((data.downlink_packet_id.value) & (2 ** (16) - 1)) << size
        size += 16
        assert isinstance(data.downlink_packet_crc, int)
        assert 0 <= data.downlink_packet_crc <= 4294967295
        result |= ((data.downlink_packet_crc) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.answer_packets_count, int)
        assert 0 <= data.answer_packets_count <= 15
        result |= ((data.answer_packets_count) & (2 ** (4) - 1)) << size
        size += 4
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceDlAnswerData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 3 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["downlink_packet_id"] = SmpmUlDeviceDlAnswerDataDownlinkPacketId(buf.shift(16))
        result__el_tmp1["downlink_packet_crc"] = buf.shift(32) + 0
        result__el_tmp1["answer_packets_count"] = buf.shift(4) + 0
        result = SmpmUlDeviceDlAnswerData(**result__el_tmp1)
        buf.shift(4)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                # TODO: handle packet info if it will be necessary
            ),
        ]
