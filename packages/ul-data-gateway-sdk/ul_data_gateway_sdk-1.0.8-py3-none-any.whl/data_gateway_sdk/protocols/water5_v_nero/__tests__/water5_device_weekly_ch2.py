from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch2 import Water5DeviceWeeklyCh2Data
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_weekly_ch2() -> None:
    case = Water5DeviceWeeklyCh2Data(value=12313.0, battery_fract=67, battery_int=3)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=0, battery_int=2, value=0.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=0, battery_int=2, value=134217.727)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=0, battery_int=2, value=12313.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=0, battery_int=3, value=0.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=0, battery_int=3, value=134217.727)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=0, battery_int=3, value=12313.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=67, battery_int=2, value=0.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=67, battery_int=2, value=134217.727)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=67, battery_int=2, value=12313.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=67, battery_int=3, value=0.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=67, battery_int=3, value=134217.727)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=67, battery_int=3, value=12313.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=127, battery_int=2, value=0.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=127, battery_int=2, value=134217.727)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=127, battery_int=2, value=12313.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=127, battery_int=3, value=0.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=127, battery_int=3, value=134217.727)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh2Data(battery_fract=127, battery_int=3, value=12313.0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh2Data.parse(BufRef(case.serialize()))
