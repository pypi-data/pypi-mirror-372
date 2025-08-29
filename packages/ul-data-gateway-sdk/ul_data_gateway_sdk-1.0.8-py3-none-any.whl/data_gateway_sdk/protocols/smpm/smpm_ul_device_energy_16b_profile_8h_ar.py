from datetime import timedelta, datetime, tzinfo, time
from enum import IntEnum, unique
from typing import Tuple, Any, Dict, List, Optional

from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageProfile, ProfileGranulation, GRANULATION_TO_END_OF_DATETIME_MAP, ProfileKind
from data_aggregator_sdk.utils.round_dt import round_dt

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet
from data_gateway_sdk.utils.true_round import true_round


# PACKET (128 bits)   smpm_ul_device_energy_16b_profile_8h_ar
#
# RESULT int:        4153979493411694417272393125779737729
# RESULT bin:  MSB   00000011 00100000 00000111 00000000 01100000 00000101 00000000 01000000 00000011 00000000 00100000 00000001 00000000 00000000 00001100 10000001   LSB
# RESULT hex:  LE    81 0c 00 00 01 20 00 03 40 00 05 60 00 07 20 03
#
# name                  type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7            7           1                                                                                                                           0000001   # noqa: E501
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1
# packet_type_id.1.VAL  u2            2           0                                                                                                                        00
# packet_type_id.1.DFF  bool          1           1                                                                                                                       1
# packet_type_id.2.VAL  u2            2           1                                                                                                                     01
# packet_type_id.2.DFF  bool          1           0                                                                                                                    0
# days_ago              timedelta     6           0                                                                                                              000000
# profile.0.point       u12          12           0                                                                                                  000000000000
# profile.1.point       u12          12           1                                                                                      000000000001
# profile.2.point       u12          12           2                                                                          000000000010
# profile.3.point       u12          12           3                                                              000000000011
# profile.4.point       u12          12           4                                                  000000000100
# profile.5.point       u12          12           5                                      000000000101
# profile.6.point       u12          12           6                          000000000110
# profile.7.point       u12          12           7              000000000111
# point_factor          uf12p1       12          50  000000110010
@unique
class SmpmUlDeviceEnergy16bProfile8hARIds(IntEnum):
    UL_DATA_16B__PROFILE_H8_1_AP = 513
    UL_DATA_16B__PROFILE_H8_1_AP__PHASE_A = 514
    UL_DATA_16B__PROFILE_H8_1_AP__PHASE_B = 515
    UL_DATA_16B__PROFILE_H8_1_AP__PHASE_C = 516
    UL_DATA_16B__PROFILE_H8_1_AN = 517
    UL_DATA_16B__PROFILE_H8_1_AN__PHASE_A = 518
    UL_DATA_16B__PROFILE_H8_1_AN__PHASE_B = 519
    UL_DATA_16B__PROFILE_H8_1_AN__PHASE_C = 520
    UL_DATA_16B__PROFILE_H8_1_RP = 521
    UL_DATA_16B__PROFILE_H8_1_RP__PHASE_A = 522
    UL_DATA_16B__PROFILE_H8_1_RP__PHASE_B = 523
    UL_DATA_16B__PROFILE_H8_1_RP__PHASE_C = 524
    UL_DATA_16B__PROFILE_H8_1_RN = 525
    UL_DATA_16B__PROFILE_H8_1_RN__PHASE_A = 526
    UL_DATA_16B__PROFILE_H8_1_RN__PHASE_B = 527
    UL_DATA_16B__PROFILE_H8_1_RN__PHASE_C = 528
    UL_DATA_16B__PROFILE_H8_2_AP = 529
    UL_DATA_16B__PROFILE_H8_2_AP__PHASE_A = 530
    UL_DATA_16B__PROFILE_H8_2_AP__PHASE_B = 531
    UL_DATA_16B__PROFILE_H8_2_AP__PHASE_C = 532
    UL_DATA_16B__PROFILE_H8_2_AN = 533
    UL_DATA_16B__PROFILE_H8_2_AN__PHASE_A = 534
    UL_DATA_16B__PROFILE_H8_2_AN__PHASE_B = 535
    UL_DATA_16B__PROFILE_H8_2_AN__PHASE_C = 536
    UL_DATA_16B__PROFILE_H8_2_RP = 537
    UL_DATA_16B__PROFILE_H8_2_RP__PHASE_A = 538
    UL_DATA_16B__PROFILE_H8_2_RP__PHASE_B = 539
    UL_DATA_16B__PROFILE_H8_2_RP__PHASE_C = 540
    UL_DATA_16B__PROFILE_H8_2_RN = 541
    UL_DATA_16B__PROFILE_H8_2_RN__PHASE_A = 542
    UL_DATA_16B__PROFILE_H8_2_RN__PHASE_B = 543
    UL_DATA_16B__PROFILE_H8_2_RN__PHASE_C = 544
    UL_DATA_16B__PROFILE_H8_3_AP = 545
    UL_DATA_16B__PROFILE_H8_3_AP__PHASE_A = 546
    UL_DATA_16B__PROFILE_H8_3_AP__PHASE_B = 547
    UL_DATA_16B__PROFILE_H8_3_AP__PHASE_C = 548
    UL_DATA_16B__PROFILE_H8_3_AN = 549
    UL_DATA_16B__PROFILE_H8_3_AN__PHASE_A = 550
    UL_DATA_16B__PROFILE_H8_3_AN__PHASE_B = 551
    UL_DATA_16B__PROFILE_H8_3_AN__PHASE_C = 552
    UL_DATA_16B__PROFILE_H8_3_RP = 553
    UL_DATA_16B__PROFILE_H8_3_RP__PHASE_A = 554
    UL_DATA_16B__PROFILE_H8_3_RP__PHASE_B = 555
    UL_DATA_16B__PROFILE_H8_3_RP__PHASE_C = 556
    UL_DATA_16B__PROFILE_H8_3_RN = 557
    UL_DATA_16B__PROFILE_H8_3_RN__PHASE_A = 558
    UL_DATA_16B__PROFILE_H8_3_RN__PHASE_B = 559
    UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C = 560


PROFILE_H8_AR_TYPE_MAP = {
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP__PHASE_A: ProfileKind.ENERGY_A_P_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP__PHASE_B: ProfileKind.ENERGY_A_P_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AP__PHASE_C: ProfileKind.ENERGY_A_P_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AN: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AN__PHASE_A: ProfileKind.ENERGY_A_N_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AN__PHASE_B: ProfileKind.ENERGY_A_N_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_AN__PHASE_C: ProfileKind.ENERGY_A_N_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RP: ProfileKind.ENERGY_R_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RP__PHASE_A: ProfileKind.ENERGY_R_P_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RP__PHASE_B: ProfileKind.ENERGY_R_P_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RP__PHASE_C: ProfileKind.ENERGY_R_P_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RN: ProfileKind.ENERGY_R_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RN__PHASE_A: ProfileKind.ENERGY_R_N_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RN__PHASE_B: ProfileKind.ENERGY_R_N_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_1_RN__PHASE_C: ProfileKind.ENERGY_R_N_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AP: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AP__PHASE_A: ProfileKind.ENERGY_A_P_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AP__PHASE_B: ProfileKind.ENERGY_A_P_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AP__PHASE_C: ProfileKind.ENERGY_A_P_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AN: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AN__PHASE_A: ProfileKind.ENERGY_A_N_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AN__PHASE_B: ProfileKind.ENERGY_A_N_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_AN__PHASE_C: ProfileKind.ENERGY_A_N_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RP: ProfileKind.ENERGY_R_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RP__PHASE_A: ProfileKind.ENERGY_R_P_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RP__PHASE_B: ProfileKind.ENERGY_R_P_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RP__PHASE_C: ProfileKind.ENERGY_R_P_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RN: ProfileKind.ENERGY_R_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RN__PHASE_A: ProfileKind.ENERGY_R_N_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RN__PHASE_B: ProfileKind.ENERGY_R_N_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_2_RN__PHASE_C: ProfileKind.ENERGY_R_N_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AP: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AP__PHASE_A: ProfileKind.ENERGY_A_P_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AP__PHASE_B: ProfileKind.ENERGY_A_P_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AP__PHASE_C: ProfileKind.ENERGY_A_P_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AN: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AN__PHASE_A: ProfileKind.ENERGY_A_N_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AN__PHASE_B: ProfileKind.ENERGY_A_N_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_AN__PHASE_C: ProfileKind.ENERGY_A_N_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RP: ProfileKind.ENERGY_R_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RP__PHASE_A: ProfileKind.ENERGY_R_P_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RP__PHASE_B: ProfileKind.ENERGY_R_P_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RP__PHASE_C: ProfileKind.ENERGY_R_P_C_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN: ProfileKind.ENERGY_R_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_A: ProfileKind.ENERGY_R_N_A_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_B: ProfileKind.ENERGY_R_N_B_DELTA,
    SmpmUlDeviceEnergy16bProfile8hARIds.UL_DATA_16B__PROFILE_H8_3_RN__PHASE_C: ProfileKind.ENERGY_R_N_C_DELTA,
}


class SmpmUlDeviceEnergy16BProfile8HArData(Packet):
    packet_type_id: SmpmUlDeviceEnergy16bProfile8hARIds
    days_ago: timedelta
    profile: Tuple[int, int, int, int, int, int, int, int]
    point_factor: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        packet_type_id__value_int_tmp1 = 0
        packet_type_id__value_size_tmp2 = 0
        assert isinstance(data.packet_type_id, SmpmUlDeviceEnergy16bProfile8hARIds)
        packet_type_id__value_int_tmp1 |= ((data.packet_type_id.value) & (2 ** (10) - 1)) << packet_type_id__value_size_tmp2
        packet_type_id__value_size_tmp2 += 10
        packet_type_id__max_size_tmp3 = 0
        packet_type_id__steps_tmp4 = [8, 3, 3, 3]
        for packet_type_id__j_tmp5 in range(32):
            packet_type_id__step_tmp6 = packet_type_id__steps_tmp4[packet_type_id__j_tmp5] if packet_type_id__j_tmp5 < len(packet_type_id__steps_tmp4) else packet_type_id__steps_tmp4[-1]  # noqa: E501
            packet_type_id__max_size_tmp3 += packet_type_id__step_tmp6
            packet_type_id__current_part_value_tmp7 = packet_type_id__value_int_tmp1 & (2 ** packet_type_id__step_tmp6 - 1)
            packet_type_id__value_int_tmp1 = packet_type_id__value_int_tmp1 >> (packet_type_id__step_tmp6 - 1)
            result |= ((packet_type_id__current_part_value_tmp7) & (2 ** ((packet_type_id__step_tmp6 - 1)) - 1)) << size
            size += (packet_type_id__step_tmp6 - 1)
            assert isinstance((packet_type_id__value_int_tmp1 != 0), bool)
            result |= ((int((packet_type_id__value_int_tmp1 != 0))) & (2 ** (1) - 1)) << size
            size += 1
            if packet_type_id__value_int_tmp1 == 0:
                break
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp8 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp8 <= 63
        result |= ((days_ago_tmp8) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.profile, tuple) and len(data.profile) == 8
        assert isinstance(data.profile[0], int)
        assert 0 <= data.profile[0] <= 4095
        result |= ((data.profile[0]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[1], int)
        assert 0 <= data.profile[1] <= 4095
        result |= ((data.profile[1]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[2], int)
        assert 0 <= data.profile[2] <= 4095
        result |= ((data.profile[2]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[3], int)
        assert 0 <= data.profile[3] <= 4095
        result |= ((data.profile[3]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[4], int)
        assert 0 <= data.profile[4] <= 4095
        result |= ((data.profile[4]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[5], int)
        assert 0 <= data.profile[5] <= 4095
        result |= ((data.profile[5]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[6], int)
        assert 0 <= data.profile[6] <= 4095
        result |= ((data.profile[6]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[7], int)
        assert 0 <= data.profile[7] <= 4095
        result |= ((data.profile[7]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.point_factor, (int, float))
        assert 0.0 <= data.point_factor <= 409.5
        result |= ((int(round(float(data.point_factor) * 10.0, 0))) & (2 ** (12) - 1)) << size
        size += 12
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BProfile8HArData':
        result__el_tmp9: Dict[str, Any] = dict()
        packet_type_id__res_tmp10 = 0
        packet_type_id__steps_tmp11 = (8, 3, 3, 3)
        packet_type_id__res_size_tmp12 = 0
        packet_type_id__step_tmp13 = 0
        for packet_type_id__i_tmp15 in range(32):
            packet_type_id__step_tmp13 = (packet_type_id__steps_tmp11[packet_type_id__i_tmp15] if packet_type_id__i_tmp15 < len(packet_type_id__steps_tmp11) else packet_type_id__steps_tmp11[-1]) - 1  # noqa: E501
            packet_type_id__res_tmp10 |= buf.shift(packet_type_id__step_tmp13) << packet_type_id__res_size_tmp12
            packet_type_id__res_size_tmp12 += packet_type_id__step_tmp13
            packet_type_id__dff_tmp14 = bool(buf.shift(1))
            if not packet_type_id__dff_tmp14:
                break
        packet_type_id__buf_tmp16 = buf
        buf = BufRef(packet_type_id__res_tmp10, stop_on_buffer_end=True)
        result__el_tmp9["packet_type_id"] = SmpmUlDeviceEnergy16bProfile8hARIds(buf.shift(10))
        buf = packet_type_id__buf_tmp16
        result__el_tmp9["days_ago"] = timedelta(seconds=buf.shift(6) * 86400)
        profile_tmp17: List[int] = []
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        result__el_tmp9["profile"] = tuple(profile_tmp17)
        result__el_tmp9["point_factor"] = round(buf.shift(12) / 10.0, 1)
        result = SmpmUlDeviceEnergy16BProfile8HArData(**result__el_tmp9)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        values: Tuple[Optional[float], ...]
        precision = 2
        profiles = (
            true_round(self.profile[0] * self.point_factor, precision) / 1000,
            true_round(self.profile[1] * self.point_factor, precision) / 1000,
            true_round(self.profile[2] * self.point_factor, precision) / 1000,
            true_round(self.profile[3] * self.point_factor, precision) / 1000,
            true_round(self.profile[4] * self.point_factor, precision) / 1000,
            true_round(self.profile[5] * self.point_factor, precision) / 1000,
            true_round(self.profile[6] * self.point_factor, precision) / 1000,
            true_round(self.profile[7] * self.point_factor, precision) / 1000,
        )
        if self.packet_type_id in {513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528}:
            values = (
                *profiles,
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
            )
        elif self.packet_type_id in {529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544}:
            values = (
                None, None, None, None, None, None, None, None,
                *profiles,
                None, None, None, None, None, None, None, None,
            )
        else:
            values = (
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
                *profiles,
            )
        return [
            IntegrationV0MessageData(
                dt=round_dt(
                    days_ago_calculation(
                        received_at,
                        device_tz,
                        time(0),
                        self.days_ago,
                    ),
                    GRANULATION_TO_END_OF_DATETIME_MAP[ProfileGranulation.MINUTE_60],
                ),
                profiles=[
                    IntegrationV0MessageProfile(
                        type=PROFILE_H8_AR_TYPE_MAP[self.packet_type_id],
                        granulation=ProfileGranulation.MINUTE_60,
                        values=values,
                    ),
                ],
            ),
        ]
