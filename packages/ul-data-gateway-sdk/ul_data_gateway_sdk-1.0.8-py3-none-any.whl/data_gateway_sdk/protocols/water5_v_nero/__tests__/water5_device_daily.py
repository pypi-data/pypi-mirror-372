from data_gateway_sdk.protocols.water5_v_nero.water5_device_daily import Water5DeviceDailyData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_daily() -> None:
    case = Water5DeviceDailyData(value=8.3)  # noqa: E501
    assert case == Water5DeviceDailyData.parse(BufRef(case.serialize()))
    case = Water5DeviceDailyData(value=0.0)  # noqa: E501
    assert case == Water5DeviceDailyData.parse(BufRef(case.serialize()))
    case = Water5DeviceDailyData(value=8.3)  # noqa: E501
    assert case == Water5DeviceDailyData.parse(BufRef(case.serialize()))
    case = Water5DeviceDailyData(value=32.767)  # noqa: E501
    assert case == Water5DeviceDailyData.parse(BufRef(case.serialize()))
