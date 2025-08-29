from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_volume import \
    SmpmUlDeviceJupiter08BCounterVolumeData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_jupiter_08b_counter_volume() -> None:
    case_serialized = bytes.fromhex("6d000000040000e0")
    assert SmpmUlDeviceJupiter08BCounterVolumeData(volume_channel_1=67108.864, volume_channel_2=67108.864, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterVolumeData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterVolumeData.serialize(SmpmUlDeviceJupiter08BCounterVolumeData(volume_channel_1=67108.864, volume_channel_2=67108.864, event_reset=True, event_low_battery_level=True))  # noqa: E501
    case_serialized = bytes.fromhex("6d000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterVolumeData(volume_channel_1=0.0, volume_channel_2=0.0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterVolumeData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterVolumeData.serialize(SmpmUlDeviceJupiter08BCounterVolumeData(event_low_battery_level=True, event_reset=True, volume_channel_1=0.0, volume_channel_2=0.0))  # noqa: E501
    case_serialized = bytes.fromhex("6d000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterVolumeData(volume_channel_1=0.0, volume_channel_2=0.0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterVolumeData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterVolumeData.serialize(SmpmUlDeviceJupiter08BCounterVolumeData(event_low_battery_level=True, event_reset=True, volume_channel_1=0.0, volume_channel_2=268435.456))  # noqa: E501
    case_serialized = bytes.fromhex("6d000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterVolumeData(volume_channel_1=0.0, volume_channel_2=0.0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterVolumeData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterVolumeData.serialize(SmpmUlDeviceJupiter08BCounterVolumeData(event_low_battery_level=True, event_reset=True, volume_channel_1=268435.456, volume_channel_2=0.0))  # noqa: E501
    case_serialized = bytes.fromhex("6d000000000000c0")  # overflow
    assert SmpmUlDeviceJupiter08BCounterVolumeData(volume_channel_1=0.0, volume_channel_2=0.0, event_reset=True, event_low_battery_level=True) == SmpmUlDeviceJupiter08BCounterVolumeData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceJupiter08BCounterVolumeData.serialize(SmpmUlDeviceJupiter08BCounterVolumeData(event_low_battery_level=True, event_reset=True, volume_channel_1=268435.456, volume_channel_2=268435.456))  # noqa: E501
