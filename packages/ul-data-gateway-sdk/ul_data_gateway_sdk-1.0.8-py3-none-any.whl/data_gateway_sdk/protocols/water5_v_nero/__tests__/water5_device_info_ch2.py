from data_gateway_sdk.protocols.water5_v_nero.water5_device_info_ch2 import Water5DeviceInfoCh2Data
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_info_ch2() -> None:
    case = Water5DeviceInfoCh2Data(value=16.3)  # noqa: E501
    assert case == Water5DeviceInfoCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceInfoCh2Data(value=0.0)  # noqa: E501
    assert case == Water5DeviceInfoCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceInfoCh2Data(value=16.3)  # noqa: E501
    assert case == Water5DeviceInfoCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceInfoCh2Data(value=4294967.295)  # noqa: E501
    assert case == Water5DeviceInfoCh2Data.parse(BufRef(case.serialize()))
