from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_fluo_freescale import \
    Water5DeviceWarmResetVFluoFreescaleData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_warm_reset_v_fluo_freescale() -> None:
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, watchdog_reset=True, pin_reset=False, power_on_reset=False, software_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVFluoFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVFluoFreescaleData.parse(BufRef(case.serialize()))
