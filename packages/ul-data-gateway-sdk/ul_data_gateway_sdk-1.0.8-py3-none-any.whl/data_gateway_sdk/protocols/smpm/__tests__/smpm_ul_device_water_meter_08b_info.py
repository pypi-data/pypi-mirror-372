from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_info import SmpmUlDeviceWaterMeter08BInfoData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_water_meter_08b_info() -> None:
    case_serialized = bytes.fromhex("69e14a1400000000")  # overflow
    assert SmpmUlDeviceWaterMeter08BInfoData(battery_volts=3.3, event_battery_low=True, event_battery_warn=True, reverse_flow_volume=10.98, event_flow_reverse=True) == SmpmUlDeviceWaterMeter08BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter08BInfoData.serialize(SmpmUlDeviceWaterMeter08BInfoData(battery_volts=3.3, event_battery_low=True, event_battery_warn=True, reverse_flow_volume=112323.3, event_flow_reverse=True))  # noqa: E501
    case_serialized = bytes.fromhex("69c0001000000000")  # overflow
    assert SmpmUlDeviceWaterMeter08BInfoData(battery_volts=0.0, event_battery_low=True, event_battery_warn=True, reverse_flow_volume=0.0, event_flow_reverse=True) == SmpmUlDeviceWaterMeter08BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter08BInfoData.serialize(SmpmUlDeviceWaterMeter08BInfoData(battery_volts=0.0, event_battery_low=True, event_battery_warn=True, event_flow_reverse=True, reverse_flow_volume=0.0))  # noqa: E501
    case_serialized = bytes.fromhex("69c0001000000000")  # overflow
    assert SmpmUlDeviceWaterMeter08BInfoData(battery_volts=0.0, event_battery_low=True, event_battery_warn=True, reverse_flow_volume=0.0, event_flow_reverse=True) == SmpmUlDeviceWaterMeter08BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter08BInfoData.serialize(SmpmUlDeviceWaterMeter08BInfoData(battery_volts=0.0, event_battery_low=True, event_battery_warn=True, event_flow_reverse=True, reverse_flow_volume=81.92))  # noqa: E501
    case_serialized = bytes.fromhex("69ff001000000000")  # overflow
    assert SmpmUlDeviceWaterMeter08BInfoData(battery_volts=6.3, event_battery_low=True, event_battery_warn=True, reverse_flow_volume=0.0, event_flow_reverse=True) == SmpmUlDeviceWaterMeter08BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter08BInfoData.serialize(SmpmUlDeviceWaterMeter08BInfoData(battery_volts=6.3, event_battery_low=True, event_battery_warn=True, event_flow_reverse=True, reverse_flow_volume=0.0))  # noqa: E501
    case_serialized = bytes.fromhex("69ff001000000000")  # overflow
    assert SmpmUlDeviceWaterMeter08BInfoData(battery_volts=6.3, event_battery_low=True, event_battery_warn=True, reverse_flow_volume=0.0, event_flow_reverse=True) == SmpmUlDeviceWaterMeter08BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter08BInfoData.serialize(SmpmUlDeviceWaterMeter08BInfoData(battery_volts=6.3, event_battery_low=True, event_battery_warn=True, event_flow_reverse=True, reverse_flow_volume=81.92))  # noqa: E501
