import random
import typing
from enum import IntEnum, unique

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   smpm_dl_device_energy_8b_get_data
#
# RESULT int:        976420344234368
# RESULT bin:  MSB   00000000 00000011 01111000 00001100 10010011 11000101 00000001 10000000   LSB
# RESULT hex:  LE    80 01 c5 93 0c 78 03 00
#
# name                             type                                         size  value(int)                                                        data(bits)
# -------------------------------  -------------------------------------------  ----  ----------  ----------------------------------------------------------------
# packet_type_id.0.VAL             u7                                              7           0                                                           0000000
# packet_type_id.0.DFF             bool                                            1           1                                                          1
# packet_type_id.1.VAL             u2                                              2           1                                                        01
# packet_type_id.1.DFF             bool                                            1           0                                                       0
# year                             u7                                              7          32                                                0100000
# month                            SmpmDlDeviceEnergy8bGetDataDataRequestMonth     4           1                                            0001
# day                              u5                                              5          15                                       01111
# request_data_pack_ids.0.pack_id  SmpmDlDeviceEnergy8bGetDataDataRequestId       14         402                         00000110010010
# request_data_pack_ids.1.pack_id  SmpmDlDeviceEnergy8bGetDataDataRequestId       14         444           00000110111100
# RESERVED                         u9                                              9           0  000000000
# Reserved space is filled with random bits in DOWNLINK packets !


@unique
class SmpmDlDeviceEnergy8bGetDataDataRequestId(IntEnum):
    UNDEFINED = 0
    UL_DATA_16B__ENERGY = 315
    NETWORK_PARAMS_PHASE1 = 444
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
class SmpmDlDeviceEnergy8bGetDataDataRequestMonth(IntEnum):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OKT = 10
    NOV = 11
    DEC = 12


class SmpmDlDeviceEnergy8BGetDataData(Packet):
    year: int
    month: SmpmDlDeviceEnergy8bGetDataDataRequestMonth
    day: int
    request_data_pack_ids: typing.Tuple[SmpmDlDeviceEnergy8bGetDataDataRequestId, SmpmDlDeviceEnergy8bGetDataDataRequestId]

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((0) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.year, int)
        assert 2000 <= data.year <= 2127
        result |= (((data.year + -2000)) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.month, SmpmDlDeviceEnergy8bGetDataDataRequestMonth)
        result |= ((data.month.value) & (2 ** (4) - 1)) << size
        size += 4
        assert isinstance(data.day, int)
        assert 0 <= data.day <= 31
        result |= ((data.day) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.request_data_pack_ids, tuple) and len(data.request_data_pack_ids) == 2
        assert isinstance(data.request_data_pack_ids[0], SmpmDlDeviceEnergy8bGetDataDataRequestId)
        result |= ((data.request_data_pack_ids[0].value) & (2 ** (14) - 1)) << size
        size += 14
        assert isinstance(data.request_data_pack_ids[1], SmpmDlDeviceEnergy8bGetDataDataRequestId)
        result |= ((data.request_data_pack_ids[1].value) & (2 ** (14) - 1)) << size
        size += 14
        result |= ((random.getrandbits(9)) & (2 ** 9 - 1)) << size
        size += 9
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmDlDeviceEnergy8BGetDataData':
        result__el_tmp1: typing.Dict[str, typing.Any] = dict()
        if 0 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["year"] = buf.shift(7) + 2000
        result__el_tmp1["month"] = SmpmDlDeviceEnergy8bGetDataDataRequestMonth(buf.shift(4))
        result__el_tmp1["day"] = buf.shift(5) + 0
        request_data_pack_ids_tmp2: typing.List[SmpmDlDeviceEnergy8bGetDataDataRequestId] = []
        request_data_pack_ids__item_tmp3 = SmpmDlDeviceEnergy8bGetDataDataRequestId(buf.shift(14))
        request_data_pack_ids_tmp2.append(request_data_pack_ids__item_tmp3)
        request_data_pack_ids__item_tmp3 = SmpmDlDeviceEnergy8bGetDataDataRequestId(buf.shift(14))
        request_data_pack_ids_tmp2.append(request_data_pack_ids__item_tmp3)
        result__el_tmp1["request_data_pack_ids"] = tuple(request_data_pack_ids_tmp2)
        result = SmpmDlDeviceEnergy8BGetDataData(**result__el_tmp1)
        buf.shift(9)
        return result
