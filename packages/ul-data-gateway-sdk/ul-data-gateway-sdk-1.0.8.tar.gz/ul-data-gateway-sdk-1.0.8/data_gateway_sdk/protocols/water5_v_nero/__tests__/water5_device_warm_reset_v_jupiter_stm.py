from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_jupiter_stm import \
    Water5DeviceWarmResetVJupiterStmData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_warm_reset_v_jupiter_stm() -> None:
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=True, watchdog_reset=True, software_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVJupiterStmData(low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVJupiterStmData.parse(BufRef(case.serialize()))
