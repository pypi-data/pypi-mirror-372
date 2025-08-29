from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_metano_a import \
    Water5DeviceWarmResetVMetanoAData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_water5_device_warm_reset_v_metano_a() -> None:
    case = Water5DeviceWarmResetVMetanoAData(watchdog_reset=True, low_voltage=True, software_reset=False, pin_reset=True, hard_fault_error=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=False, low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=False, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=False, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=False, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=True, software_reset=False, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=False)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
    case = Water5DeviceWarmResetVMetanoAData(hard_fault_error=True, low_voltage=True, pin_reset=True, software_reset=True, watchdog_reset=True)  # noqa: E501
    assert case == Water5DeviceWarmResetVMetanoAData.parse(BufRef(case.serialize()))
