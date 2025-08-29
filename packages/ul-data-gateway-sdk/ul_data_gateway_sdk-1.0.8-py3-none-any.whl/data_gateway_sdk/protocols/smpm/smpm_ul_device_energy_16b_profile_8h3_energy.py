from datetime import timedelta, datetime, time, tzinfo
from enum import IntEnum, unique
from typing import List, Any, Dict, Tuple

import pytz
from data_aggregator_sdk.constants.enums import DeviceHack
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, ProfileKind, \
    IntegrationV0MessageProfile, ProfileGranulation, GRANULATION_TO_END_OF_DATETIME_MAP
from data_aggregator_sdk.utils.round_dt import round_dt

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet
from data_gateway_sdk.utils.true_round import true_round


# PACKET (128 bits)   smpm_ul_device_energy_16b_profile_8h3_energy
#
# RESULT int:        265850142892151729396105850589001287276
# RESULT bin:  MSB   11001000 00000000 11100000 00000110 00000000 00101000 00000001 00000000 00000110 00000000 00100000 00000000 10000000 00000000 00000110 01101100   LSB
# RESULT hex:  LE    6c 06 00 80 00 20 00 06 00 01 28 00 06 e0 00 c8
#
# name                     type                                       size  value(int)                                                                                                                        data(bits)    # noqa: E501
# -----------------------  -----------------------------------------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------    # noqa: E501
# packet_type_id.0.VAL     u7                                            7         108                                                                                                                           1101100    # noqa: E501
# packet_type_id.0.DFF     bool                                          1           0                                                                                                                          0           # noqa: E501
# type                     SmpmUlDeviceEnergy16bProfile8h3EnergyType     2           2                                                                                                                        10            # noqa: E501
# point_factor_multiplier  u2                                            2           1                                                                                                                      01              # noqa: E501
# days_ago                 timedelta                                     6           0                                                                                                                000000                # noqa: E501
# profile.0.point          u13                                          13           0                                                                                                   0000000000000                      # noqa: E501
# profile.1.point          u13                                          13           1                                                                                      0000000000001                                   # noqa: E501
# profile.2.point          u13                                          13           2                                                                         0000000000010
# profile.3.point          u13                                          13           3                                                            0000000000011
# profile.4.point          u13                                          13           4                                               0000000000100
# profile.5.point          u13                                          13           5                                  0000000000101
# profile.6.point          u13                                          13           6                     0000000000110
# profile.7.point          u13                                          13           7        0000000000111
# point_factor             uf6p1                                         6          50  110010

@unique
class SmpmUlDeviceEnergy16bProfile8h3EnergyType(IntEnum):
    ENERGY_GENERATED_ACTIVE = 0  # ENERGY_A_N 0
    ENERGY_GENERATED_REACTIVE = 1  # ENERGY_R_N 1
    ENERGY_CONSUMED_ACTIVE = 2  # ENERGY_A_P 2
    ENERGY_CONSUMED_REACTIVE = 3  # ENERGY_R_P 3

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


PROFILE_MAP = {
    SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_GENERATED_ACTIVE: ProfileKind.ENERGY_A_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_GENERATED_REACTIVE: ProfileKind.ENERGY_R_N_DELTA,
    SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE: ProfileKind.ENERGY_A_P_DELTA,
    SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_REACTIVE: ProfileKind.ENERGY_R_P_DELTA,
}


class SmpmUlDeviceEnergy16BProfile8H3EnergyData(Packet):
    type: SmpmUlDeviceEnergy16bProfile8h3EnergyType
    point_factor_multiplier: int
    days_ago: timedelta
    profile: Tuple[int, int, int, int, int, int, int, int]
    point_factor: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((108) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.type, SmpmUlDeviceEnergy16bProfile8h3EnergyType)
        result |= ((data.type.value) & (2 ** (2) - 1)) << size
        size += 2
        assert isinstance(data.point_factor_multiplier, int)
        assert 1 <= data.point_factor_multiplier <= 4
        result |= (((data.point_factor_multiplier + -1)) & (2 ** (2) - 1)) << size
        size += 2
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 63
        result |= ((days_ago_tmp1) & (2 ** (6) - 1)) << size
        size += 6
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
        assert isinstance(data.point_factor, (int, float))
        assert 0.0 <= data.point_factor <= 6.3
        result |= ((int(round(float(data.point_factor) * 10.0, 0))) & (2 ** (6) - 1)) << size
        size += 6
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BProfile8H3EnergyData':
        result__el_tmp2: Dict[str, Any] = dict()
        if 108 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp2["type"] = SmpmUlDeviceEnergy16bProfile8h3EnergyType(buf.shift(2))
        result__el_tmp2["point_factor_multiplier"] = buf.shift(2) + 1
        result__el_tmp2["days_ago"] = timedelta(seconds=buf.shift(6) * 86400)
        profile_tmp3: List[int] = []
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        profile__item_tmp4 = buf.shift(13) + 0
        profile_tmp3.append(profile__item_tmp4)
        result__el_tmp2["profile"] = tuple(profile_tmp3)
        result__el_tmp2["point_factor"] = round(buf.shift(6) / 10.0 - 0.0, 1)
        result = SmpmUlDeviceEnergy16BProfile8H3EnergyData(**result__el_tmp2)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        point_factor = self.point_factor * self.point_factor_multiplier
        hacks = kwargs.get('hacks', [])
        if DeviceHack.electricity_profile_packets_days_ago_is_zero in hacks:
            return [
                IntegrationV0MessageData(
                    dt=(
                        round_dt(
                            received_at.astimezone(device_tz),
                            GRANULATION_TO_END_OF_DATETIME_MAP[ProfileGranulation.MINUTE_60],
                        ) - timedelta(seconds=3600 * 8)).astimezone(pytz.timezone('UTC')),
                    profiles=[
                        IntegrationV0MessageProfile(
                            type=PROFILE_MAP[self.type],
                            granulation=ProfileGranulation.MINUTE_60,
                            values=(
                                true_round(self.profile[0] * point_factor) / 1000,
                                true_round(self.profile[1] * point_factor) / 1000,
                                true_round(self.profile[2] * point_factor) / 1000,
                                true_round(self.profile[3] * point_factor) / 1000,
                                true_round(self.profile[4] * point_factor) / 1000,
                                true_round(self.profile[5] * point_factor) / 1000,
                                true_round(self.profile[6] * point_factor) / 1000,
                                true_round(self.profile[7] * point_factor) / 1000,
                                None, None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None, None,
                            ),
                        ),
                    ],
                ),
            ]
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
                        type=PROFILE_MAP[self.type],
                        granulation=ProfileGranulation.MINUTE_60,
                        values=(
                            None, None, None, None, None, None, None, None,
                            None, None, None, None, None, None, None, None,
                            true_round(self.profile[0] * point_factor, 3) / 1000,
                            true_round(self.profile[1] * point_factor, 3) / 1000,
                            true_round(self.profile[2] * point_factor, 3) / 1000,
                            true_round(self.profile[3] * point_factor, 3) / 1000,
                            true_round(self.profile[4] * point_factor, 3) / 1000,
                            true_round(self.profile[5] * point_factor, 3) / 1000,
                            true_round(self.profile[6] * point_factor, 3) / 1000,
                            true_round(self.profile[7] * point_factor, 3) / 1000,
                        ),
                    ),
                ],
            ),
        ]
