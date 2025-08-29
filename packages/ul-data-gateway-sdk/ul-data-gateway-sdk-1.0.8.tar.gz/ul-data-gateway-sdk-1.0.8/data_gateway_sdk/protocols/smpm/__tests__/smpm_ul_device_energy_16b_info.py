from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_info import SmpmUlDeviceEnergy16BInfoData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_info() -> None:
    case_serialized = bytes.fromhex("bc0aed017c5687000000000000000000")
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=3.3, temperature=23, date_time=timedelta(seconds=567648000.0), relay_is_active=False) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=3.3, temperature=23, date_time=timedelta(seconds=567648000.0), relay_is_active=False))  # noqa: E501
    case_serialized = bytes.fromhex("bc02fcffffffff030000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, temperature=155, date_time=timedelta(seconds=2147483647.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, date_time=timedelta(seconds=2147483647.0), relay_is_active=True, temperature=155))  # noqa: E501
    case_serialized = bytes.fromhex("bc0200fcffffff030000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, temperature=-100, date_time=timedelta(seconds=2147483647.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, date_time=timedelta(seconds=2147483647.0), relay_is_active=True, temperature=-100))  # noqa: E501
    case_serialized = bytes.fromhex("bc02fc03000000020000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, temperature=155, date_time=timedelta(seconds=0.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, date_time=timedelta(seconds=0.0), relay_is_active=True, temperature=155))  # noqa: E501
    case_serialized = bytes.fromhex("bc020000000000020000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, temperature=-100, date_time=timedelta(seconds=0.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=0.0, date_time=timedelta(seconds=0.0), relay_is_active=True, temperature=-100))  # noqa: E501
    case_serialized = bytes.fromhex("bcfaffffffffff030000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, temperature=155, date_time=timedelta(seconds=2147483647.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, date_time=timedelta(seconds=2147483647.0), relay_is_active=True, temperature=155))  # noqa: E501
    case_serialized = bytes.fromhex("bcfa03fcffffff030000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, temperature=-100, date_time=timedelta(seconds=2147483647.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, date_time=timedelta(seconds=2147483647.0), relay_is_active=True, temperature=-100))  # noqa: E501
    case_serialized = bytes.fromhex("bcfaff03000000020000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, temperature=155, date_time=timedelta(seconds=0.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, date_time=timedelta(seconds=0.0), relay_is_active=True, temperature=155))  # noqa: E501
    case_serialized = bytes.fromhex("bcfa0300000000020000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, temperature=-100, date_time=timedelta(seconds=0.0), relay_is_active=True) == SmpmUlDeviceEnergy16BInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BInfoData.serialize(SmpmUlDeviceEnergy16BInfoData(battery_volts=12.7, date_time=timedelta(seconds=0.0), relay_is_active=True, temperature=-100))  # noqa: E501
