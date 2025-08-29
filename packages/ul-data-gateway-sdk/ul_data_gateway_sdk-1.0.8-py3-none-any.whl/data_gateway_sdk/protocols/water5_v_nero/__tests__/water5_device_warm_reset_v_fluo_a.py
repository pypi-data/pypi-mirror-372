from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_fluo_a import Water5DeviceWarmResetVFluoAData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_warm_reset_v_fluo_a() -> None:
    case = Water5DeviceWarmResetVFluoAData(pin_reset=True, low_voltage=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoAData(low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoAData.parse(BufRef(case.serialize()))
