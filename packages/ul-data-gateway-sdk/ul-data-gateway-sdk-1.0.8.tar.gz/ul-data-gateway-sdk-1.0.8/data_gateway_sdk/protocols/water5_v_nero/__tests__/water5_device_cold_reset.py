from data_gateway_sdk.protocols.water5_v_nero.water5_device_cold_reset import Water5DeviceColdResetData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_cold_reset() -> None:
    case = Water5DeviceColdResetData(value=16.123)  # noqa: E501
    assert case == Water5DeviceColdResetData.parse(BufRef(case.serialize()))
    case = Water5DeviceColdResetData(value=0.0)  # noqa: E501
    assert case == Water5DeviceColdResetData.parse(BufRef(case.serialize()))
    case = Water5DeviceColdResetData(value=16.123)  # noqa: E501
    assert case == Water5DeviceColdResetData.parse(BufRef(case.serialize()))
    case = Water5DeviceColdResetData(value=4294967.295)  # noqa: E501
    assert case == Water5DeviceColdResetData.parse(BufRef(case.serialize()))
