from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_ar import SmpmUlDeviceEnergy16BProfile8HArData, SmpmUlDeviceEnergy16bProfile8hARIds
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_profile_8h_ar() -> None:
    case_serialized = bytes.fromhex("810c0000012000034000056000072003")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0))  # noqa: E501
    case_serialized = bytes.fromhex("b00c0000012000034000056000070000")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("b00c000001200003400005600007f0ff")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("810c0000012000034000056000070000")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("810c000001200003400005600007f0ff")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("b0cc0f00012000034000056000070000")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("b0cc0f0001200003400005600007f0ff")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("81cc0f00012000034000056000070000")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
    case_serialized = bytes.fromhex("81cc0f0001200003400005600007f0ff")
    assert SmpmUlDeviceEnergy16BProfile8HArData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HArData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8HArData.serialize(SmpmUlDeviceEnergy16BProfile8HArData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
