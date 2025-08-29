import random
import typing
from enum import IntEnum, unique

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_dl_device_energy_16b_set_regular_data_sending
#
# RESULT int:        4161395094
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 11111000 00001001 11011001 10010110   LSB
# RESULT hex:  LE    96 d9 09 f8 00 00 00 00 00 00 00 00 00 00 00 00
#
# name                  type                                                     size  value(int)                                                                                                                        data(bits)
# --------------------  -------------------------------------------------------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL  u7                                                          7          22                                                                                                                           0010110
# packet_type_id.0.DFF  bool                                                        1           1                                                                                                                          1
# packet_type_id.1.VAL  u2                                                          2           1                                                                                                                        01
# packet_type_id.1.DFF  bool                                                        1           0                                                                                                                       0
# pack_id               SmpmDlDeviceEnergy16bSetRegularDataSendingDataRequestId    14         315                                                                                                         00000100111011
# action                SpecUpLinkModelingPacketIdU8Action                          2           0                                                                                                       00
# period_ago            u6                                                          6          31                                                                                                 011111
# week_mask.0.day       bool                                                        1           0                                                                                                0
# week_mask.1.day       bool                                                        1           0                                                                                               0
# week_mask.2.day       bool                                                        1           0                                                                                              0
# week_mask.3.day       bool                                                        1           0                                                                                             0
# week_mask.4.day       bool                                                        1           0                                                                                            0
# week_mask.5.day       bool                                                        1           0                                                                                           0
# week_mask.6.day       bool                                                        1           0                                                                                          0
# days_mask.0.day       bool                                                        1           0                                                                                         0
# days_mask.1.day       bool                                                        1           0                                                                                        0
# days_mask.2.day       bool                                                        1           0                                                                                       0
# days_mask.3.day       bool                                                        1           0                                                                                      0
# days_mask.4.day       bool                                                        1           0                                                                                     0
# days_mask.5.day       bool                                                        1           0                                                                                    0
# days_mask.6.day       bool                                                        1           0                                                                                   0
# days_mask.7.day       bool                                                        1           0                                                                                  0
# days_mask.8.day       bool                                                        1           0                                                                                 0
# days_mask.9.day       bool                                                        1           0                                                                                0
# days_mask.10.day      bool                                                        1           0                                                                               0
# days_mask.11.day      bool                                                        1           0                                                                              0
# days_mask.12.day      bool                                                        1           0                                                                             0
# days_mask.13.day      bool                                                        1           0                                                                            0
# days_mask.14.day      bool                                                        1           0                                                                           0
# days_mask.15.day      bool                                                        1           0                                                                          0
# days_mask.16.day      bool                                                        1           0                                                                         0
# days_mask.17.day      bool                                                        1           0                                                                        0
# days_mask.18.day      bool                                                        1           0                                                                       0
# days_mask.19.day      bool                                                        1           0                                                                      0
# days_mask.20.day      bool                                                        1           0                                                                     0
# days_mask.21.day      bool                                                        1           0                                                                    0
# days_mask.22.day      bool                                                        1           0                                                                   0
# days_mask.23.day      bool                                                        1           0                                                                  0
# days_mask.24.day      bool                                                        1           0                                                                 0
# days_mask.25.day      bool                                                        1           0                                                                0
# days_mask.26.day      bool                                                        1           0                                                               0
# days_mask.27.day      bool                                                        1           0                                                              0
# days_mask.28.day      bool                                                        1           0                                                             0
# days_mask.29.day      bool                                                        1           0                                                            0
# days_mask.30.day      bool                                                        1           0                                                           0
# hour_mask.0.hour      bool                                                        1           0                                                          0
# hour_mask.1.hour      bool                                                        1           0                                                         0
# hour_mask.2.hour      bool                                                        1           0                                                        0
# hour_mask.3.hour      bool                                                        1           0                                                       0
# hour_mask.4.hour      bool                                                        1           0                                                      0
# hour_mask.5.hour      bool                                                        1           0                                                     0
# hour_mask.6.hour      bool                                                        1           0                                                    0
# hour_mask.7.hour      bool                                                        1           0                                                   0
# hour_mask.8.hour      bool                                                        1           0                                                  0
# hour_mask.9.hour      bool                                                        1           0                                                 0
# hour_mask.10.hour     bool                                                        1           0                                                0
# hour_mask.11.hour     bool                                                        1           0                                               0
# hour_mask.12.hour     bool                                                        1           0                                              0
# hour_mask.13.hour     bool                                                        1           0                                             0
# hour_mask.14.hour     bool                                                        1           0                                            0
# hour_mask.15.hour     bool                                                        1           0                                           0
# hour_mask.16.hour     bool                                                        1           0                                          0
# hour_mask.17.hour     bool                                                        1           0                                         0
# hour_mask.18.hour     bool                                                        1           0                                        0
# hour_mask.19.hour     bool                                                        1           0                                       0
# hour_mask.20.hour     bool                                                        1           0                                      0
# hour_mask.21.hour     bool                                                        1           0                                     0
# hour_mask.22.hour     bool                                                        1           0                                    0
# hour_mask.23.hour     bool                                                        1           0                                   0
# RESERVED              u33                                                        33           0  000000000000000000000000000000000
# Reserved space is filled with random bits in DOWNLINK packets !


@unique
class SmpmDlDeviceEnergy16bSetRegularDataSendingDataRequestId(IntEnum):
    UL_DATA_16B__ENERGY = 315
    DAILY_ENERGY_ACTIVE_CONSUMED = 400
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_1 = 401
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2 = 402
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_3 = 403
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_4 = 404
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM = 405
    DAILY_ENERGY_REACTIVE_CONSUMED = 406
    DAILY_ENERGY_ACTIVE_GENERATED = 407
    DAILY_ENERGY_REACTIVE_GENERATED = 408
    MONTHLY_ENERGY_ACTIVE_CONSUMED = 409
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_1 = 410
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_2 = 411
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_3 = 412
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_4 = 413
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM = 414
    MONTHLY_ENERGY_REACTIVE_CONSUMED = 415
    MONTHLY_ENERGY_ACTIVE_GENERATED = 416
    MONTHLY_ENERGY_REACTIVE_GENERATED = 417


@unique
class SpecUpLinkModelingPacketIdU8Action(IntEnum):
    REPLACE = 0
    ADD = 1
    REPLACE_HOUR = 2
    REPLACE_DAY = 3


class SmpmDlDeviceEnergy16BSetRegularDataSendingData(Packet):
    pack_id: SmpmDlDeviceEnergy16bSetRegularDataSendingDataRequestId
    action: SpecUpLinkModelingPacketIdU8Action
    period_ago: int
    week_mask: typing.Tuple[bool, bool, bool, bool, bool, bool, bool]
    days_mask: typing.Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool]
    hour_mask: typing.Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool]

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((22) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.pack_id, SmpmDlDeviceEnergy16bSetRegularDataSendingDataRequestId)
        result |= ((data.pack_id.value) & (2 ** (14) - 1)) << size
        size += 14
        assert isinstance(data.action, SpecUpLinkModelingPacketIdU8Action)
        result |= ((data.action.value) & (2 ** (2) - 1)) << size
        size += 2
        assert isinstance(data.period_ago, int)
        assert 0 <= data.period_ago <= 63
        result |= ((data.period_ago) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.week_mask, tuple) and len(data.week_mask) == 7
        assert isinstance(data.week_mask[0], bool)
        result |= ((int(data.week_mask[0])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.week_mask[1], bool)
        result |= ((int(data.week_mask[1])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.week_mask[2], bool)
        result |= ((int(data.week_mask[2])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.week_mask[3], bool)
        result |= ((int(data.week_mask[3])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.week_mask[4], bool)
        result |= ((int(data.week_mask[4])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.week_mask[5], bool)
        result |= ((int(data.week_mask[5])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.week_mask[6], bool)
        result |= ((int(data.week_mask[6])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask, tuple) and len(data.days_mask) == 31
        assert isinstance(data.days_mask[0], bool)
        result |= ((int(data.days_mask[0])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[1], bool)
        result |= ((int(data.days_mask[1])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[2], bool)
        result |= ((int(data.days_mask[2])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[3], bool)
        result |= ((int(data.days_mask[3])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[4], bool)
        result |= ((int(data.days_mask[4])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[5], bool)
        result |= ((int(data.days_mask[5])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[6], bool)
        result |= ((int(data.days_mask[6])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[7], bool)
        result |= ((int(data.days_mask[7])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[8], bool)
        result |= ((int(data.days_mask[8])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[9], bool)
        result |= ((int(data.days_mask[9])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[10], bool)
        result |= ((int(data.days_mask[10])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[11], bool)
        result |= ((int(data.days_mask[11])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[12], bool)
        result |= ((int(data.days_mask[12])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[13], bool)
        result |= ((int(data.days_mask[13])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[14], bool)
        result |= ((int(data.days_mask[14])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[15], bool)
        result |= ((int(data.days_mask[15])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[16], bool)
        result |= ((int(data.days_mask[16])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[17], bool)
        result |= ((int(data.days_mask[17])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[18], bool)
        result |= ((int(data.days_mask[18])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[19], bool)
        result |= ((int(data.days_mask[19])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[20], bool)
        result |= ((int(data.days_mask[20])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[21], bool)
        result |= ((int(data.days_mask[21])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[22], bool)
        result |= ((int(data.days_mask[22])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[23], bool)
        result |= ((int(data.days_mask[23])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[24], bool)
        result |= ((int(data.days_mask[24])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[25], bool)
        result |= ((int(data.days_mask[25])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[26], bool)
        result |= ((int(data.days_mask[26])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[27], bool)
        result |= ((int(data.days_mask[27])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[28], bool)
        result |= ((int(data.days_mask[28])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[29], bool)
        result |= ((int(data.days_mask[29])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.days_mask[30], bool)
        result |= ((int(data.days_mask[30])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask, tuple) and len(data.hour_mask) == 24
        assert isinstance(data.hour_mask[0], bool)
        result |= ((int(data.hour_mask[0])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[1], bool)
        result |= ((int(data.hour_mask[1])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[2], bool)
        result |= ((int(data.hour_mask[2])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[3], bool)
        result |= ((int(data.hour_mask[3])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[4], bool)
        result |= ((int(data.hour_mask[4])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[5], bool)
        result |= ((int(data.hour_mask[5])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[6], bool)
        result |= ((int(data.hour_mask[6])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[7], bool)
        result |= ((int(data.hour_mask[7])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[8], bool)
        result |= ((int(data.hour_mask[8])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[9], bool)
        result |= ((int(data.hour_mask[9])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[10], bool)
        result |= ((int(data.hour_mask[10])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[11], bool)
        result |= ((int(data.hour_mask[11])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[12], bool)
        result |= ((int(data.hour_mask[12])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[13], bool)
        result |= ((int(data.hour_mask[13])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[14], bool)
        result |= ((int(data.hour_mask[14])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[15], bool)
        result |= ((int(data.hour_mask[15])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[16], bool)
        result |= ((int(data.hour_mask[16])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[17], bool)
        result |= ((int(data.hour_mask[17])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[18], bool)
        result |= ((int(data.hour_mask[18])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[19], bool)
        result |= ((int(data.hour_mask[19])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[20], bool)
        result |= ((int(data.hour_mask[20])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[21], bool)
        result |= ((int(data.hour_mask[21])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[22], bool)
        result |= ((int(data.hour_mask[22])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hour_mask[23], bool)
        result |= ((int(data.hour_mask[23])) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((random.getrandbits(33)) & (2 ** 33 - 1)) << size
        size += 33
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmDlDeviceEnergy16BSetRegularDataSendingData':
        result__el_tmp1: typing.Dict[str, typing.Any] = dict()
        if 22 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["pack_id"] = SmpmDlDeviceEnergy16bSetRegularDataSendingDataRequestId(buf.shift(14))
        result__el_tmp1["action"] = SpecUpLinkModelingPacketIdU8Action(buf.shift(2))
        result__el_tmp1["period_ago"] = buf.shift(6) + 0
        week_mask_tmp2: typing.List[bool] = []
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        week_mask__item_tmp3 = bool(buf.shift(1))
        week_mask_tmp2.append(week_mask__item_tmp3)
        result__el_tmp1["week_mask"] = tuple(week_mask_tmp2)
        days_mask_tmp4: typing.List[bool] = []
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        days_mask__item_tmp5 = bool(buf.shift(1))
        days_mask_tmp4.append(days_mask__item_tmp5)
        result__el_tmp1["days_mask"] = tuple(days_mask_tmp4)
        hour_mask_tmp6: typing.List[bool] = []
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        hour_mask__item_tmp7 = bool(buf.shift(1))
        hour_mask_tmp6.append(hour_mask__item_tmp7)
        result__el_tmp1["hour_mask"] = tuple(hour_mask_tmp6)
        result = SmpmDlDeviceEnergy16BSetRegularDataSendingData(**result__el_tmp1)
        buf.shift(33)
        return result
