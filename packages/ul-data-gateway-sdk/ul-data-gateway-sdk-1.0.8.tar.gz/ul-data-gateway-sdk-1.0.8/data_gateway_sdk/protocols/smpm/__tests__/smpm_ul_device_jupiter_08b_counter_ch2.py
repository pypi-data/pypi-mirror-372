from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_ch2 import SmpmUlDeviceJupiter08BCounterCh2Data
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_jupiter_08b_counter_ch2() -> None:
    case_serialized = bytes.fromhex("67ffffff7fa16e00")
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=2147483647, battery_volts=3.3, temperature=23, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(value=2147483647, battery_volts=3.3, temperature=23, event_reset=True, event_low_battery_level=True))  # noqa: E501
    case_serialized = bytes.fromhex("6700000000c07f00")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=0.0, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=92, value=0))  # noqa: E501
    case_serialized = bytes.fromhex("6700000000c07f00")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=0.0, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=92, value=8589934592))  # noqa: E501
    case_serialized = bytes.fromhex("6700000000006000")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=0.0, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=-35, value=0))  # noqa: E501
    case_serialized = bytes.fromhex("6700000000006000")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=0.0, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=-35, value=8589934592))  # noqa: E501
    case_serialized = bytes.fromhex("6700000000ff7f00")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=6.3, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=92, value=0))  # noqa: E501
    case_serialized = bytes.fromhex("6700000000ff7f00")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=6.3, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=92, value=8589934592))  # noqa: E501
    case_serialized = bytes.fromhex("67000000003f6000")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=6.3, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=-35, value=0))  # noqa: E501
    case_serialized = bytes.fromhex("67000000003f6000")  # overflow
    assert SmpmUlDeviceJupiter08BCounterCh2Data(value=0, battery_volts=6.3, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterCh2Data.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterCh2Data.serialize(SmpmUlDeviceJupiter08BCounterCh2Data(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=-35, value=8589934592))  # noqa: E501
