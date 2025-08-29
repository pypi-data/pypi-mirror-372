from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch1_impulse_v2 import \
    Water5DeviceWeeklyCh1ImpulseV2Data
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_weekly_ch1_impulse_v2() -> None:
    case = Water5DeviceWeeklyCh1ImpulseV2Data(value=12313, battery_fract=67, battery_int=3)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=0, battery_int=2, value=0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=0, battery_int=2, value=12313)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=0, battery_int=2, value=16777215)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=0, battery_int=3, value=0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=0, battery_int=3, value=12313)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=0, battery_int=3, value=16777215)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=67, battery_int=2, value=0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=67, battery_int=2, value=12313)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=67, battery_int=2, value=16777215)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=67, battery_int=3, value=0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=67, battery_int=3, value=12313)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=67, battery_int=3, value=16777215)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=127, battery_int=2, value=0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=127, battery_int=2, value=12313)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=127, battery_int=2, value=16777215)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=127, battery_int=3, value=0)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=127, battery_int=3, value=12313)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
    case = Water5DeviceWeeklyCh1ImpulseV2Data(battery_fract=127, battery_int=3, value=16777215)  # noqa: E501
    assert case == Water5DeviceWeeklyCh1ImpulseV2Data.parse(BufRef(case.serialize()))
