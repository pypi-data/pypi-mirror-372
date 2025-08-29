from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_04b_event import SmpmUlDeviceWaterMeter04BEventData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_water_meter_04b_event() -> None:
    case_serialized = bytes.fromhex("0ce13a06")
    assert SmpmUlDeviceWaterMeter04BEventData(battery_volts=3.3, event_low_battery_level=True, event_temperature_limits=True, temperature=23, event_case_was_opened=False, event_magnet=False, event_reset=True, event_sensor_error=True) == SmpmUlDeviceWaterMeter04BEventData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter04BEventData.serialize(SmpmUlDeviceWaterMeter04BEventData(battery_volts=3.3, event_low_battery_level=True, event_temperature_limits=True, temperature=23, event_case_was_opened=False, event_magnet=False, event_reset=True, event_sensor_error=True))  # noqa: E501
    case_serialized = bytes.fromhex("0cc0ff07")  # overflow
    assert SmpmUlDeviceWaterMeter04BEventData(battery_volts=0.0, event_low_battery_level=True, event_temperature_limits=True, temperature=92, event_case_was_opened=True, event_magnet=True, event_reset=True, event_sensor_error=True) == SmpmUlDeviceWaterMeter04BEventData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter04BEventData.serialize(SmpmUlDeviceWaterMeter04BEventData(battery_volts=0.0, event_case_was_opened=True, event_low_battery_level=True, event_magnet=True, event_reset=True, event_sensor_error=True, event_temperature_limits=True, temperature=92))  # noqa: E501
    case_serialized = bytes.fromhex("0cc08007")  # overflow
    assert SmpmUlDeviceWaterMeter04BEventData(battery_volts=0.0, event_low_battery_level=True, event_temperature_limits=True, temperature=-35, event_case_was_opened=True, event_magnet=True, event_reset=True, event_sensor_error=True) == SmpmUlDeviceWaterMeter04BEventData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter04BEventData.serialize(SmpmUlDeviceWaterMeter04BEventData(battery_volts=0.0, event_case_was_opened=True, event_low_battery_level=True, event_magnet=True, event_reset=True, event_sensor_error=True, event_temperature_limits=True, temperature=-35))  # noqa: E501
    case_serialized = bytes.fromhex("0cffff07")  # overflow
    assert SmpmUlDeviceWaterMeter04BEventData(battery_volts=6.3, event_low_battery_level=True, event_temperature_limits=True, temperature=92, event_case_was_opened=True, event_magnet=True, event_reset=True, event_sensor_error=True) == SmpmUlDeviceWaterMeter04BEventData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter04BEventData.serialize(SmpmUlDeviceWaterMeter04BEventData(battery_volts=6.3, event_case_was_opened=True, event_low_battery_level=True, event_magnet=True, event_reset=True, event_sensor_error=True, event_temperature_limits=True, temperature=92))  # noqa: E501
    case_serialized = bytes.fromhex("0cff8007")  # overflow
    assert SmpmUlDeviceWaterMeter04BEventData(battery_volts=6.3, event_low_battery_level=True, event_temperature_limits=True, temperature=-35, event_case_was_opened=True, event_magnet=True, event_reset=True, event_sensor_error=True) == SmpmUlDeviceWaterMeter04BEventData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceWaterMeter04BEventData.serialize(SmpmUlDeviceWaterMeter04BEventData(battery_volts=6.3, event_case_was_opened=True, event_low_battery_level=True, event_magnet=True, event_reset=True, event_sensor_error=True, event_temperature_limits=True, temperature=-35))  # noqa: E501
