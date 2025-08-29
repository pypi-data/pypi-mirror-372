from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_12b_counter import SmpmUlDeviceJupiter12BCounterData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_jupiter_12b_counter() -> None:
    case_serialized = bytes.fromhex("d4f9ffffffefffffffbf5037")
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=8589934591, value_channel_2=8589934591, battery_volts=3.3, temperature=23, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(value_channel_1=8589934591, value_channel_2=8589934591, battery_volts=3.3, temperature=23, event_reset=True, event_low_battery_level=True))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000000e03f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=0, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000000e03f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=0, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000000e03f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=34359738368, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000000e03f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=34359738368, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000000030")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=0, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000000030")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=0, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000000030")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=34359738368, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000000030")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=0.0, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=0.0, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=34359738368, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000080ff3f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=0, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000080ff3f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=0, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000080ff3f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=34359738368, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d4010000000000000080ff3f")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=92, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=92, value_channel_1=34359738368, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000801f30")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=0, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000801f30")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=0, value_channel_2=34359738368))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000801f30")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=34359738368, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("d40100000000000000801f30")  # overflow
    assert SmpmUlDeviceJupiter12BCounterData(value_channel_1=0, value_channel_2=0, battery_volts=6.3, temperature=-35, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter12BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter12BCounterData.serialize(SmpmUlDeviceJupiter12BCounterData(battery_volts=6.3, event_low_battery_level=True, event_reset=True, temperature=-35, value_channel_1=34359738368, value_channel_2=34359738368))  # noqa: E501
