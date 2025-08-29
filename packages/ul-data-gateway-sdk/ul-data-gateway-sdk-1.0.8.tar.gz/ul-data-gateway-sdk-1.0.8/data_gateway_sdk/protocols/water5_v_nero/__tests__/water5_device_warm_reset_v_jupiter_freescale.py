from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_jupiter_freescale import \
    Water5DeviceWarmResetVJupiterFreescaleData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_warm_reset_v_jupiter_freescale() -> None:
    case = Water5DeviceWarmResetVJupiterFreescaleData(power_on_reset=True, watchdog_reset=True, low_voltage=True, software_reset=False, pin_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=False, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=False, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterFreescaleData(low_voltage=True, pin_reset=True, power_on_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterFreescaleData.parse(BufRef(case.serialize()))
