from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_8b_set_clock import SmpmDlDeviceEnergy8BSetClockData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_dl_device_energy_8b_set_clock() -> None:
    case_serialized = bytes.fromhex("02ffffff7fffff00")
    assert SmpmDlDeviceEnergy8BSetClockData(time=timedelta(seconds=2147483647.0), time_zone_offset_s=timedelta(seconds=65535.0), time_zone_offset_is_negative=False) == SmpmDlDeviceEnergy8BSetClockData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("0200000000000002")  # overflow
    assert SmpmDlDeviceEnergy8BSetClockData(time=timedelta(seconds=0.0), time_zone_offset_s=timedelta(seconds=0.0), time_zone_offset_is_negative=True) == SmpmDlDeviceEnergy8BSetClockData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("0200000000ffff03")  # overflow
    assert SmpmDlDeviceEnergy8BSetClockData(time=timedelta(seconds=0.0), time_zone_offset_s=timedelta(seconds=131071.0), time_zone_offset_is_negative=True) == SmpmDlDeviceEnergy8BSetClockData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("02ffffffff000002")  # overflow
    assert SmpmDlDeviceEnergy8BSetClockData(time=timedelta(seconds=4294967295.0), time_zone_offset_s=timedelta(seconds=0.0), time_zone_offset_is_negative=True) == SmpmDlDeviceEnergy8BSetClockData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("02ffffffffffff03")  # overflow
    assert SmpmDlDeviceEnergy8BSetClockData(time=timedelta(seconds=4294967295.0), time_zone_offset_s=timedelta(seconds=131071.0), time_zone_offset_is_negative=True) == SmpmDlDeviceEnergy8BSetClockData.parse(BufRef(case_serialized))  # noqa: E501
