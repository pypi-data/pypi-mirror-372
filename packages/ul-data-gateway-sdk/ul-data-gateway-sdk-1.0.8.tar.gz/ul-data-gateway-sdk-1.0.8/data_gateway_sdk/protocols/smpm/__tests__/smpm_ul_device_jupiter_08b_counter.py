from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter import SmpmUlDeviceJupiter08BCounterData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_jupiter_08b_counter() -> None:
    case_serialized = bytes.fromhex("65fffffffbffffdf")
    assert SmpmUlDeviceJupiter08BCounterData(value_channel_1=67108863, value_channel_2=67108863, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterData.serialize(SmpmUlDeviceJupiter08BCounterData(value_channel_1=67108863, value_channel_2=67108863, event_reset=True, event_low_battery_level=True))  # noqa: E501
    case_serialized = bytes.fromhex("65000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterData(value_channel_1=0, value_channel_2=0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterData.serialize(SmpmUlDeviceJupiter08BCounterData(event_low_battery_level=True, event_reset=True, value_channel_1=0, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("65000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterData(value_channel_1=0, value_channel_2=0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterData.serialize(SmpmUlDeviceJupiter08BCounterData(event_low_battery_level=True, event_reset=True, value_channel_1=0, value_channel_2=268435456))  # noqa: E501
    case_serialized = bytes.fromhex("65000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterData(value_channel_1=0, value_channel_2=0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterData.serialize(SmpmUlDeviceJupiter08BCounterData(event_low_battery_level=True, event_reset=True, value_channel_1=268435456, value_channel_2=0))  # noqa: E501
    case_serialized = bytes.fromhex("65000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterData(value_channel_1=0, value_channel_2=0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterData.serialize(SmpmUlDeviceJupiter08BCounterData(event_low_battery_level=True, event_reset=True, value_channel_1=268435456, value_channel_2=268435456))  # noqa: E501
