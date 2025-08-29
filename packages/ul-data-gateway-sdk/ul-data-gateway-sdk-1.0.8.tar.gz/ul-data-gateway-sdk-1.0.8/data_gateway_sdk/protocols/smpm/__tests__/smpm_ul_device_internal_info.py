from data_gateway_sdk.protocols.smpm.smpm_ul_device_internal_info import SmpmUlDeviceInternalInfoData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_internal_info() -> None:
    case_serialized = bytes.fromhex("7f7f7f7f7f7f7f7f")
    assert SmpmUlDeviceInternalInfoData(data=(127, 127, 127, 127, 127, 127, 127)) == SmpmUlDeviceInternalInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceInternalInfoData.serialize(SmpmUlDeviceInternalInfoData(data=(127, 127, 127, 127, 127, 127, 127)))  # noqa: E501
    case_serialized = bytes.fromhex("7f7f7f7f7f7f7f7f")  # overflow
    assert SmpmUlDeviceInternalInfoData(data=(127, 127, 127, 127, 127, 127, 127)) == SmpmUlDeviceInternalInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceInternalInfoData.serialize(SmpmUlDeviceInternalInfoData(data=(127, 127, 127, 127, 127, 127, 127)))  # noqa: E501
