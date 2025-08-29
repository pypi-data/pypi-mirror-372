from datetime import timedelta, datetime, time, tzinfo
from enum import IntEnum, unique
from typing import List, Any, Dict, Tuple, Optional

from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageProfile, ProfileGranulation, ProfileKind, GRANULATION_TO_END_OF_DATETIME_MAP
from data_aggregator_sdk.utils.round_dt import round_dt

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet
from data_gateway_sdk.utils.true_round import true_round


# PACKET (128 bits)   smpm_ul_device_energy_16b_profile_8h_f
#
# RESULT int:        237762635927079402885851130105524
# RESULT bin:  MSB   00000000 00000000 00001011 10111000 11111100 10000010 11010100 00010000 11111010 00010000 01000000 00010100 00000001 11100000 00001110 10110100   LSB
# RESULT hex:  LE    b4 0e e0 01 14 40 10 fa 10 d4 82 fc b8 0b 00 00
#
# name                  type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7            7          52                                                                                                                           0110100   # noqa: E501
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1
# packet_type_id.1.VAL  u2            2           2                                                                                                                        10
# packet_type_id.1.DFF  bool          1           1                                                                                                                       1
# packet_type_id.2.VAL  u2            2           1                                                                                                                     01
# packet_type_id.2.DFF  bool          1           0                                                                                                                    0
# days_ago              timedelta     6           0                                                                                                              000000
# profile.0.point       uf11p2       11          30                                                                                                   00000011110
# profile.1.point       uf11p2       11          40                                                                                        00000101000
# profile.2.point       uf11p2       11        1040                                                                             10000010000
# profile.3.point       uf11p2       11        2000                                                                  11111010000
# profile.4.point       uf11p2       11        1040                                                       10000010000
# profile.5.point       uf11p2       11          90                                            00001011010
# profile.6.point       uf11p2       11        1010                                 01111110010
# profile.7.point       uf11p2       11        1500                      10111011100
# RESERVED              u20          20           0  00000000000000000000
@unique
class SmpmUlDeviceEnergy16bProfile8hFIds(IntEnum):
    UL_DATA_16B__PROFILE_H8_1_F_AVG = 820
    UL_DATA_16B__PROFILE_H8_1_F_MIN = 821
    UL_DATA_16B__PROFILE_H8_1_F_MAX = 822
    UL_DATA_16B__PROFILE_H8_2_F_AVG = 823
    UL_DATA_16B__PROFILE_H8_2_F_MIN = 824
    UL_DATA_16B__PROFILE_H8_2_F_MAX = 825
    UL_DATA_16B__PROFILE_H8_3_F_AVG = 826
    UL_DATA_16B__PROFILE_H8_3_F_MIN = 827
    UL_DATA_16B__PROFILE_H8_3_F_MAX = 828
    UL_DATA_16B__PROFILE_H8_1_F_AVG__PHASE_A = 829
    UL_DATA_16B__PROFILE_H8_1_F_MIN__PHASE_A = 830
    UL_DATA_16B__PROFILE_H8_1_F_MAX__PHASE_A = 831
    UL_DATA_16B__PROFILE_H8_2_F_AVG__PHASE_A = 832
    UL_DATA_16B__PROFILE_H8_2_F_MIN__PHASE_A = 833
    UL_DATA_16B__PROFILE_H8_2_F_MAX__PHASE_A = 834
    UL_DATA_16B__PROFILE_H8_3_F_AVG__PHASE_A = 835
    UL_DATA_16B__PROFILE_H8_3_F_MIN__PHASE_A = 836
    UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_A = 837
    UL_DATA_16B__PROFILE_H8_1_F_AVG__PHASE_B = 838
    UL_DATA_16B__PROFILE_H8_1_F_MIN__PHASE_B = 839
    UL_DATA_16B__PROFILE_H8_1_F_MAX__PHASE_B = 840
    UL_DATA_16B__PROFILE_H8_2_F_AVG__PHASE_B = 841
    UL_DATA_16B__PROFILE_H8_2_F_MIN__PHASE_B = 842
    UL_DATA_16B__PROFILE_H8_2_F_MAX__PHASE_B = 843
    UL_DATA_16B__PROFILE_H8_3_F_AVG__PHASE_B = 844
    UL_DATA_16B__PROFILE_H8_3_F_MIN__PHASE_B = 845
    UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_B = 846
    UL_DATA_16B__PROFILE_H8_1_F_AVG__PHASE_C = 847
    UL_DATA_16B__PROFILE_H8_1_F_MIN__PHASE_C = 848
    UL_DATA_16B__PROFILE_H8_1_F_MAX__PHASE_C = 849
    UL_DATA_16B__PROFILE_H8_2_F_AVG__PHASE_C = 850
    UL_DATA_16B__PROFILE_H8_2_F_MIN__PHASE_C = 851
    UL_DATA_16B__PROFILE_H8_2_F_MAX__PHASE_C = 852
    UL_DATA_16B__PROFILE_H8_3_F_AVG__PHASE_C = 853
    UL_DATA_16B__PROFILE_H8_3_F_MIN__PHASE_C = 854
    UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_C = 855


PROFILE_H8_F_TYPE_MAP = {
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG: ProfileKind.FREQUENCY_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MIN: ProfileKind.FREQUENCY_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MAX: ProfileKind.FREQUENCY_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_AVG: ProfileKind.FREQUENCY_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MIN: ProfileKind.FREQUENCY_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MAX: ProfileKind.FREQUENCY_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_AVG: ProfileKind.FREQUENCY_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MIN: ProfileKind.FREQUENCY_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX: ProfileKind.FREQUENCY_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG__PHASE_A: ProfileKind.FREQUENCY_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MIN__PHASE_A: ProfileKind.FREQUENCY_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MAX__PHASE_A: ProfileKind.FREQUENCY_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_AVG__PHASE_A: ProfileKind.FREQUENCY_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MIN__PHASE_A: ProfileKind.FREQUENCY_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MAX__PHASE_A: ProfileKind.FREQUENCY_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_AVG__PHASE_A: ProfileKind.FREQUENCY_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MIN__PHASE_A: ProfileKind.FREQUENCY_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_A: ProfileKind.FREQUENCY_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG__PHASE_B: ProfileKind.FREQUENCY_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MIN__PHASE_B: ProfileKind.FREQUENCY_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MAX__PHASE_B: ProfileKind.FREQUENCY_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_AVG__PHASE_B: ProfileKind.FREQUENCY_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MIN__PHASE_B: ProfileKind.FREQUENCY_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MAX__PHASE_B: ProfileKind.FREQUENCY_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_AVG__PHASE_B: ProfileKind.FREQUENCY_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MIN__PHASE_B: ProfileKind.FREQUENCY_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_B: ProfileKind.FREQUENCY_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_AVG__PHASE_C: ProfileKind.FREQUENCY_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MIN__PHASE_C: ProfileKind.FREQUENCY_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_1_F_MAX__PHASE_C: ProfileKind.FREQUENCY_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_AVG__PHASE_C: ProfileKind.FREQUENCY_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MIN__PHASE_C: ProfileKind.FREQUENCY_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_2_F_MAX__PHASE_C: ProfileKind.FREQUENCY_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_AVG__PHASE_C: ProfileKind.FREQUENCY_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MIN__PHASE_C: ProfileKind.FREQUENCY_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hFIds.UL_DATA_16B__PROFILE_H8_3_F_MAX__PHASE_C: ProfileKind.FREQUENCY_MAX_C,
}

assert set(PROFILE_H8_F_TYPE_MAP.keys()) == set(v for v in SmpmUlDeviceEnergy16bProfile8hFIds)


class SmpmUlDeviceEnergy16BProfile8HFData(Packet):
    packet_type_id: SmpmUlDeviceEnergy16bProfile8hFIds
    days_ago: timedelta
    profile: Tuple[float, float, float, float, float, float, float, float]

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        packet_type_id__value_int_tmp1 = 0
        packet_type_id__value_size_tmp2 = 0
        assert isinstance(data.packet_type_id, SmpmUlDeviceEnergy16bProfile8hFIds)
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
        assert isinstance(data.profile[0], (int, float))
        assert 45.0 <= data.profile[0] <= 65.47
        result |= ((int(round(float(data.profile[0] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[1], (int, float))
        assert 45.0 <= data.profile[1] <= 65.47
        result |= ((int(round(float(data.profile[1] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[2], (int, float))
        assert 45.0 <= data.profile[2] <= 65.47
        result |= ((int(round(float(data.profile[2] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[3], (int, float))
        assert 45.0 <= data.profile[3] <= 65.47
        result |= ((int(round(float(data.profile[3] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[4], (int, float))
        assert 45.0 <= data.profile[4] <= 65.47
        result |= ((int(round(float(data.profile[4] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[5], (int, float))
        assert 45.0 <= data.profile[5] <= 65.47
        result |= ((int(round(float(data.profile[5] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[6], (int, float))
        assert 45.0 <= data.profile[6] <= 65.47
        result |= ((int(round(float(data.profile[6] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        assert isinstance(data.profile[7], (int, float))
        assert 45.0 <= data.profile[7] <= 65.47
        result |= ((int(round(float(data.profile[7] - 45.0) * 100.0, 0))) & (2 ** (11) - 1)) << size
        size += 11
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BProfile8HFData':
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
        result__el_tmp9["packet_type_id"] = SmpmUlDeviceEnergy16bProfile8hFIds(buf.shift(10))
        buf = packet_type_id__buf_tmp16
        result__el_tmp9["days_ago"] = timedelta(seconds=buf.shift(6) * 86400)
        profile_tmp17: List[float] = []
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = round(buf.shift(11) / 100.0 + 45.0, 2)
        profile_tmp17.append(profile__item_tmp18)
        result__el_tmp9["profile"] = tuple(profile_tmp17)
        result = SmpmUlDeviceEnergy16BProfile8HFData(**result__el_tmp9)
        buf.shift(20)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        values: Tuple[Optional[float], ...]
        precision = 2
        profiles = (
            true_round(self.profile[0], precision),
            true_round(self.profile[1], precision),
            true_round(self.profile[2], precision),
            true_round(self.profile[3], precision),
            true_round(self.profile[4], precision),
            true_round(self.profile[5], precision),
            true_round(self.profile[6], precision),
            true_round(self.profile[7], precision),
        )
        if self.packet_type_id in {820, 821, 822, 829, 830, 831, 838, 839, 840, 847, 848, 849}:
            values = (
                *profiles,
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
            )
        elif self.packet_type_id in {823, 824, 825, 832, 833, 834, 841, 842, 843, 850, 851, 852}:
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
                        type=PROFILE_H8_F_TYPE_MAP[self.packet_type_id],
                        granulation=ProfileGranulation.MINUTE_60,
                        values=values,
                    ),
                ],
            ),
        ]
