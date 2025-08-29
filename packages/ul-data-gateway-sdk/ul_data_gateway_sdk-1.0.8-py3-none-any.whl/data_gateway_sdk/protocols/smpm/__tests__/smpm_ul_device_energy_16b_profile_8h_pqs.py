# from datetime import timedelta
#
# from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_pqs import SmpmUlDeviceEnergy16BProfile8HPqsData, SmpmUlDeviceEnergy16bProfile8hPQSIds
# from data_gateway_sdk.utils.buf_ref import BufRef
#
#
# def test_smpm_ul_device_energy_16b_profile_8h_pqs() -> None:
#     case_serialized = bytes.fromhex("b10c008000086000042880010e200300")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0))  # noqa: E501
#     case_serialized = bytes.fromhex("b10c008000086000042880010e000000")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("b10c008000086000042880010ef0ff00")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("9c0d008000086000042880010e000000")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("9c0d008000086000042880010ef0ff00")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=0.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("b1cc0f8000086000042880010e000000")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("b1cc0f8000086000042880010ef0ff00")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("9ccd0f8000086000042880010e000000")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, point_factor=0.0, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
#     case_serialized = bytes.fromhex("9ccd0f8000086000042880010ef0ff00")
#     assert SmpmUlDeviceEnergy16BProfile8HPqsData(packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=409.5) == SmpmUlDeviceEnergy16BProfile8HPqsData.parse(BufRef(case_serialized))  # noqa: E501
#     assert case_serialized == SmpmUlDeviceEnergy16BProfile8HPqsData.serialize(SmpmUlDeviceEnergy16BProfile8HPqsData(days_ago=timedelta(seconds=5443200.0), packet_type_id=SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C, point_factor=409.5, profile=(0, 1, 2, 3, 4, 5, 6, 7)))  # noqa: E501
