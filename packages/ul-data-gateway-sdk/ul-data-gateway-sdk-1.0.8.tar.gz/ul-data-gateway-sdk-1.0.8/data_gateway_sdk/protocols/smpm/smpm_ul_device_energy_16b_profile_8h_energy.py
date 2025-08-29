from datetime import timedelta, time, datetime, tzinfo
from enum import IntEnum, unique
from typing import Dict, Tuple, List, Any, Optional

from data_aggregator_sdk.integration_message import ProfileKind, IntegrationV0MessageData, GRANULATION_TO_END_OF_DATETIME_MAP, ProfileGranulation, IntegrationV0MessageProfile
from data_aggregator_sdk.utils.round_dt import round_dt

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_profile_8h_energy
#
# RESULT int:        290799050787508182044066107677279152
# RESULT bin:  MSB   00000000 00111000 00000001 10000000 00001010 00000000 01000000 00000001 10000000 00001000 00000000 00100000 00000000 01010101 00000011 10110000   LSB
# RESULT hex:  LE    b0 03 55 00 20 00 08 80 01 40 00 0a 80 01 38 00
#
# name                       type       size  value(int)                                                                                                                        data(bits)  # noqa: E501
# -------------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------  # noqa: E501
# packet_type_id_enum.0.VAL  u7            7          48                                                                                                                           0110000  # noqa: E501
# packet_type_id_enum.0.DFF  bool          1           1                                                                                                                          1
# packet_type_id_enum.1.VAL  u2            2           3                                                                                                                        11
# packet_type_id_enum.1.DFF  bool          1           0                                                                                                                       0
# days_ago                   timedelta     5           0                                                                                                                  00000
# valid.0.value_valid        bool          1           1                                                                                                                 1
# valid.1.value_valid        bool          1           0                                                                                                                0
# valid.2.value_valid        bool          1           1                                                                                                               1
# valid.3.value_valid        bool          1           0                                                                                                              0
# valid.4.value_valid        bool          1           1                                                                                                             1
# valid.5.value_valid        bool          1           0                                                                                                            0
# valid.6.value_valid        bool          1           1                                                                                                           1
# valid.7.value_valid        bool          1           0                                                                                                          0
# profile.0.point            u13          13           0                                                                                             0000000000000
# profile.1.point            u13          13           1                                                                                0000000000001
# profile.2.point            u13          13           2                                                                   0000000000010
# profile.3.point            u13          13           3                                                      0000000000011
# profile.4.point            u13          13           4                                         0000000000100
# profile.5.point            u13          13           5                            0000000000101
# profile.6.point            u13          13           6               0000000000110
# profile.7.point            u13          13           7  0000000000111

@unique
class SmpmUlDeviceEnergy16bProfile8hEnergyIds(IntEnum):
    UL_DATA_16B__PROFILE_ENERGY_ACTIVE_CONSUMED_H8_1 = 432
    UL_DATA_16B__PROFILE_ENERGY_ACTIVE_CONSUMED_H8_2 = 433
    UL_DATA_16B__PROFILE_ENERGY_ACTIVE_CONSUMED_H8_3 = 434
    UL_DATA_16B__PROFILE_ENERGY_ACTIVE_GENERATED_H8_1 = 435
    UL_DATA_16B__PROFILE_ENERGY_ACTIVE_GENERATED_H8_2 = 436
    UL_DATA_16B__PROFILE_ENERGY_ACTIVE_GENERATED_H8_3 = 437
    UL_DATA_16B__PROFILE_ENERGY_REACTIVE_CONSUMED_H8_1 = 438
    UL_DATA_16B__PROFILE_ENERGY_REACTIVE_CONSUMED_H8_2 = 439
    UL_DATA_16B__PROFILE_ENERGY_REACTIVE_CONSUMED_H8_3 = 440
    UL_DATA_16B__PROFILE_ENERGY_REACTIVE_GENERATED_H8_1 = 441
    UL_DATA_16B__PROFILE_ENERGY_REACTIVE_GENERATED_H8_2 = 442
    UL_DATA_16B__PROFILE_ENERGY_REACTIVE_GENERATED_H8_3 = 443


PROFILE_H8_ENERGY_MAP = {
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_ACTIVE_CONSUMED_H8_1: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_ACTIVE_CONSUMED_H8_2: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_ACTIVE_CONSUMED_H8_3: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_ACTIVE_GENERATED_H8_1: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_ACTIVE_GENERATED_H8_2: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_ACTIVE_GENERATED_H8_3: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_REACTIVE_CONSUMED_H8_1: ProfileKind.ENERGY_R_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_REACTIVE_CONSUMED_H8_2: ProfileKind.ENERGY_R_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_REACTIVE_CONSUMED_H8_3: ProfileKind.ENERGY_R_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_REACTIVE_GENERATED_H8_1: ProfileKind.ENERGY_R_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_REACTIVE_GENERATED_H8_2: ProfileKind.ENERGY_R_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8hEnergyIds.UL_DATA_16B__PROFILE_ENERGY_REACTIVE_GENERATED_H8_3: ProfileKind.ENERGY_R_N_DELTA,
}


class SmpmUlDeviceEnergy16BProfile8HEnergyData(Packet):
    packet_type_id_enum: SmpmUlDeviceEnergy16bProfile8hEnergyIds
    days_ago: timedelta
    valid: Tuple[bool, bool, bool, bool, bool, bool, bool, bool]
    profile: Tuple[int, int, int, int, int, int, int, int]

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        packet_type_id_enum__value_int_tmp1 = 0
        packet_type_id_enum__value_size_tmp2 = 0
        assert isinstance(data.packet_type_id_enum, SmpmUlDeviceEnergy16bProfile8hEnergyIds)
        packet_type_id_enum__value_int_tmp1 |= ((data.packet_type_id_enum.value) & (2 ** (11) - 1)) << packet_type_id_enum__value_size_tmp2
        packet_type_id_enum__value_size_tmp2 += 11
        packet_type_id_enum__max_size_tmp3 = 0
        packet_type_id_enum__steps_tmp4 = [8, 3, 3, 3]
        for packet_type_id_enum__j_tmp5 in range(32):
            packet_type_id_enum__step_tmp6 = packet_type_id_enum__steps_tmp4[packet_type_id_enum__j_tmp5] if packet_type_id_enum__j_tmp5 < len(packet_type_id_enum__steps_tmp4) else packet_type_id_enum__steps_tmp4[-1]
            packet_type_id_enum__max_size_tmp3 += packet_type_id_enum__step_tmp6
            packet_type_id_enum__current_part_value_tmp7 = packet_type_id_enum__value_int_tmp1 & (2 ** packet_type_id_enum__step_tmp6 - 1)
            packet_type_id_enum__value_int_tmp1 = packet_type_id_enum__value_int_tmp1 >> (packet_type_id_enum__step_tmp6 - 1)
            result |= ((packet_type_id_enum__current_part_value_tmp7) & (2 ** ((packet_type_id_enum__step_tmp6 - 1)) - 1)) << size
            size += (packet_type_id_enum__step_tmp6 - 1)
            assert isinstance((packet_type_id_enum__value_int_tmp1 != 0), bool)
            result |= ((int((packet_type_id_enum__value_int_tmp1 != 0))) & (2 ** (1) - 1)) << size
            size += 1
            if packet_type_id_enum__value_int_tmp1 == 0:
                break
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp8 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp8 <= 31
        result |= ((days_ago_tmp8) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.valid, tuple) and len(data.valid) == 8
        assert isinstance(data.valid[0], bool)
        result |= ((int(data.valid[0])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[1], bool)
        result |= ((int(data.valid[1])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[2], bool)
        result |= ((int(data.valid[2])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[3], bool)
        result |= ((int(data.valid[3])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[4], bool)
        result |= ((int(data.valid[4])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[5], bool)
        result |= ((int(data.valid[5])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[6], bool)
        result |= ((int(data.valid[6])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.valid[7], bool)
        result |= ((int(data.valid[7])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.profile, tuple) and len(data.profile) == 8
        assert isinstance(data.profile[0], int)
        assert 0 <= data.profile[0] <= 8191
        result |= ((data.profile[0]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[1], int)
        assert 0 <= data.profile[1] <= 8191
        result |= ((data.profile[1]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[2], int)
        assert 0 <= data.profile[2] <= 8191
        result |= ((data.profile[2]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[3], int)
        assert 0 <= data.profile[3] <= 8191
        result |= ((data.profile[3]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[4], int)
        assert 0 <= data.profile[4] <= 8191
        result |= ((data.profile[4]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[5], int)
        assert 0 <= data.profile[5] <= 8191
        result |= ((data.profile[5]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[6], int)
        assert 0 <= data.profile[6] <= 8191
        result |= ((data.profile[6]) & (2 ** (13) - 1)) << size
        size += 13
        assert isinstance(data.profile[7], int)
        assert 0 <= data.profile[7] <= 8191
        result |= ((data.profile[7]) & (2 ** (13) - 1)) << size
        size += 13
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BProfile8HEnergyData':
        result__el_tmp9: Dict[str, Any] = dict()
        packet_type_id_enum__res_tmp10 = 0
        packet_type_id_enum__steps_tmp11 = (8, 3, 3, 3)
        packet_type_id_enum__res_size_tmp12 = 0
        packet_type_id_enum__step_tmp13 = 0
        for packet_type_id_enum__i_tmp15 in range(32):
            packet_type_id_enum__step_tmp13 = (packet_type_id_enum__steps_tmp11[packet_type_id_enum__i_tmp15] if packet_type_id_enum__i_tmp15 < len(
                packet_type_id_enum__steps_tmp11) else packet_type_id_enum__steps_tmp11[-1]) - 1
            packet_type_id_enum__res_tmp10 |= buf.shift(packet_type_id_enum__step_tmp13) << packet_type_id_enum__res_size_tmp12
            packet_type_id_enum__res_size_tmp12 += packet_type_id_enum__step_tmp13
            packet_type_id_enum__dff_tmp14 = bool(buf.shift(1))
            if not packet_type_id_enum__dff_tmp14:
                break
        packet_type_id_enum__buf_tmp16 = buf
        buf = BufRef(packet_type_id_enum__res_tmp10, stop_on_buffer_end=True)
        result__el_tmp9["packet_type_id_enum"] = SmpmUlDeviceEnergy16bProfile8hEnergyIds(buf.shift(11))
        buf = packet_type_id_enum__buf_tmp16
        result__el_tmp9["days_ago"] = timedelta(seconds=buf.shift(5) * 86400)
        valid_tmp17: List[bool] = []
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        valid__item_tmp18 = bool(buf.shift(1))
        valid_tmp17.append(valid__item_tmp18)
        result__el_tmp9["valid"] = tuple(valid_tmp17)
        profile_tmp19: List[int] = []
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        profile__item_tmp20 = buf.shift(13) + 0
        profile_tmp19.append(profile__item_tmp20)
        result__el_tmp9["profile"] = tuple(profile_tmp19)
        result = SmpmUlDeviceEnergy16BProfile8HEnergyData(**result__el_tmp9)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        values: Tuple[Optional[float], ...]
        profiles = (
            self.profile[0] if self.valid[0] else None,
            self.profile[1] if self.valid[1] else None,
            self.profile[2] if self.valid[2] else None,
            self.profile[3] if self.valid[3] else None,
            self.profile[4] if self.valid[4] else None,
            self.profile[5] if self.valid[5] else None,
            self.profile[6] if self.valid[6] else None,
            self.profile[7] if self.valid[7] else None,
        )
        if self.packet_type_id_enum in {432, 435, 438, 441}:
            values = (
                *profiles,
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
            )
        elif self.packet_type_id_enum in {433, 436, 439, 442}:
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
                        type=PROFILE_H8_ENERGY_MAP[self.packet_type_id_enum],
                        granulation=ProfileGranulation.MINUTE_60,
                        values=values,
                    ),
                ],
            ),
        ]
