from data_gateway_sdk.protocols.water5_v_nero.water5_device_magnet import Water5DeviceMagnetData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_magnet() -> None:
    case = Water5DeviceMagnetData()  # noqa: E501
    assert case == Water5DeviceMagnetData.parse(BufRef(case.serialize()))
    case = Water5DeviceMagnetData()  # noqa: E501
    assert case == Water5DeviceMagnetData.parse(BufRef(case.serialize()))
