from data_gateway_sdk.protocols.water5_v_nero.water5_device_info_ch1 import Water5DeviceInfoCh1Data
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_info_ch1() -> None:
    case = Water5DeviceInfoCh1Data(value=16.3)  # noqa: E501
    assert case == Water5DeviceInfoCh1Data.parse(BufRef(case.serialize()))
    case = Water5DeviceInfoCh1Data(value=0.0)  # noqa: E501
    assert case == Water5DeviceInfoCh1Data.parse(BufRef(case.serialize()))
    case = Water5DeviceInfoCh1Data(value=16.3)  # noqa: E501
    assert case == Water5DeviceInfoCh1Data.parse(BufRef(case.serialize()))
    case = Water5DeviceInfoCh1Data(value=4294967.295)  # noqa: E501
    assert case == Water5DeviceInfoCh1Data.parse(BufRef(case.serialize()))
