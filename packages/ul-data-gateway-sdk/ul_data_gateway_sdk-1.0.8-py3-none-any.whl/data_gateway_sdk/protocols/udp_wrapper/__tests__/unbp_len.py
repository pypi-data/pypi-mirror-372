from data_gateway_sdk.protocols.udp_wrapper.unbp_len import UnbpUplinkLenData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_unbp_uplink_len() -> None:
    case_serialized = bytes.fromhex("3bd22200000000037f3f160b973d76")
    assert UnbpUplinkLenData(mac=34, message_id=0, payload=[127, 63, 22], crc=1983747851) == UnbpUplinkLenData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == UnbpUplinkLenData.serialize(UnbpUplinkLenData(mac=34, message_id=0, payload=[127, 63, 22], crc=1983747851))  # noqa: E501
    case_serialized = bytes.fromhex("3bd20000000000002e82d981")  # overflow
    assert UnbpUplinkLenData(mac=0, message_id=0, payload=[], crc=2178515502) == UnbpUplinkLenData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == UnbpUplinkLenData.serialize(UnbpUplinkLenData(crc=2178515502, mac=0, message_id=0, payload=[]))  # noqa: E501
    case_serialized = bytes.fromhex("3bd222000000000868e4eab106a33a78a6258953")  # overflow
    assert UnbpUplinkLenData(mac=34, message_id=0, payload=[104, 228, 234, 177, 6, 163, 58, 120], crc=1401496998) == UnbpUplinkLenData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == UnbpUplinkLenData.serialize(UnbpUplinkLenData(crc=1401496998, mac=34, message_id=0, payload=[104, 228, 234, 177, 6, 163, 58, 120]))  # noqa: E501


def test_unbp_uplink_len_multiple() -> None:
    case_serialized = bytes.fromhex("3bd298248000001068e4eab106a33a7868e4eab106a33a78ebad25df")  # overflow
    assert UnbpUplinkLenData(mac=8397976, message_id=0, payload=[104, 228, 234, 177, 6, 163, 58, 120, 104, 228, 234, 177, 6, 163, 58, 120], crc=3743788523) == UnbpUplinkLenData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == UnbpUplinkLenData.serialize(UnbpUplinkLenData(crc=3743788523, mac=8397976, message_id=0, payload=[104, 228, 234, 177, 6, 163, 58, 120, 104, 228, 234, 177, 6, 163, 58, 120]))  # noqa: E501
