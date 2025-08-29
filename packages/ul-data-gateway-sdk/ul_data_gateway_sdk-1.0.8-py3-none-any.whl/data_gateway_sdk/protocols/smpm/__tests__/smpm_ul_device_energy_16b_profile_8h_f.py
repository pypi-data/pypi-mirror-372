from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_f import SmpmUlDeviceEnergy16BProfile8HFData, SmpmUlDeviceEnergy16bProfile8hFIds
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_profile_8h_f() -> None:
    case_serialized = bytes.fromhex("b40ee001144010fa10d482fcb80b0000")
    assert SmpmUlDeviceEnergy16BProfile8HFData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG, days_ago=timedelta(seconds=0.0), profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)) == SmpmUlDeviceEnergy16BProfile8HFData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HFData.serialize(SmpmUlDeviceEnergy16BProfile8HFData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG, days_ago=timedelta(seconds=0.0), profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)))  # noqa: E501
    case_serialized = bytes.fromhex("b40ee001144010fa10d482fcb80b0000")
    assert SmpmUlDeviceEnergy16BProfile8HFData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG, days_ago=timedelta(seconds=0.0), profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)) == SmpmUlDeviceEnergy16BProfile8HFData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HFData.serialize(SmpmUlDeviceEnergy16BProfile8HFData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG, profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)))  # noqa: E501
    case_serialized = bytes.fromhex("d70ee001144010fa10d482fcb80b0000")
    assert SmpmUlDeviceEnergy16BProfile8HFData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_C, days_ago=timedelta(seconds=0.0), profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)) == SmpmUlDeviceEnergy16BProfile8HFData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HFData.serialize(SmpmUlDeviceEnergy16BProfile8HFData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_C, profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)))  # noqa: E501
    case_serialized = bytes.fromhex("b4ceef01144010fa10d482fcb80b0000")
    assert SmpmUlDeviceEnergy16BProfile8HFData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG, days_ago=timedelta(seconds=5443200.0), profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)) == SmpmUlDeviceEnergy16BProfile8HFData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HFData.serialize(SmpmUlDeviceEnergy16BProfile8HFData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG, profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)))  # noqa: E501
    case_serialized = bytes.fromhex("d7ceef01144010fa10d482fcb80b0000")
    assert SmpmUlDeviceEnergy16BProfile8HFData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_C, days_ago=timedelta(seconds=5443200.0), profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)) == SmpmUlDeviceEnergy16BProfile8HFData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HFData.serialize(SmpmUlDeviceEnergy16BProfile8HFData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_C, profile=(45.3, 45.4, 55.4, 65.0, 55.4, 45.9, 55.1, 60.0)))  # noqa: E501
