from data_gateway_sdk.protocols.smpm.smpm_ul_device_dl_answer import SmpmUlDeviceDlAnswerData, \
    SmpmUlDeviceDlAnswerDataDownlinkPacketId
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_dl_answer() -> None:
    case_serialized = bytes.fromhex("030100ffffff7f07")
    assert SmpmUlDeviceDlAnswerData(downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.GET_ECHO, downlink_packet_crc=2147483647, answer_packets_count=7) == SmpmUlDeviceDlAnswerData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceDlAnswerData.serialize(SmpmUlDeviceDlAnswerData(downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.GET_ECHO, downlink_packet_crc=2147483647, answer_packets_count=7))  # noqa: E501
    case_serialized = bytes.fromhex("03aa000000000000")  # overflow
    assert SmpmUlDeviceDlAnswerData(downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY, downlink_packet_crc=0, answer_packets_count=0) == SmpmUlDeviceDlAnswerData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceDlAnswerData.serialize(SmpmUlDeviceDlAnswerData(answer_packets_count=0, downlink_packet_crc=0, downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY))  # noqa: E501
    case_serialized = bytes.fromhex("03aa00ffffffff00")  # overflow
    assert SmpmUlDeviceDlAnswerData(downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY, downlink_packet_crc=4294967295, answer_packets_count=0) == SmpmUlDeviceDlAnswerData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceDlAnswerData.serialize(SmpmUlDeviceDlAnswerData(answer_packets_count=0, downlink_packet_crc=4294967295, downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY))  # noqa: E501
    case_serialized = bytes.fromhex("03aa00000000000f")  # overflow
    assert SmpmUlDeviceDlAnswerData(downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY, downlink_packet_crc=0, answer_packets_count=15) == SmpmUlDeviceDlAnswerData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceDlAnswerData.serialize(SmpmUlDeviceDlAnswerData(answer_packets_count=15, downlink_packet_crc=0, downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY))  # noqa: E501
    case_serialized = bytes.fromhex("03aa00ffffffff0f")  # overflow
    assert SmpmUlDeviceDlAnswerData(downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY, downlink_packet_crc=4294967295, answer_packets_count=15) == SmpmUlDeviceDlAnswerData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceDlAnswerData.serialize(SmpmUlDeviceDlAnswerData(answer_packets_count=15, downlink_packet_crc=4294967295, downlink_packet_id=SmpmUlDeviceDlAnswerDataDownlinkPacketId.SET_RELAY))  # noqa: E501
