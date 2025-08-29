from datetime import timedelta, datetime, time, tzinfo
from typing import List, Any, Tuple, Dict

from data_aggregator_sdk.constants.enums import JournalDataType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    ResourceType, CounterType
from decimal import Decimal

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_tariff_consumed
#
# RESULT int:        1636017705544601932779225794
# RESULT bin:  MSB   00000000000000000000000000000000000001010100100101001000001110011000011101100000000111100000111100110010010100000000001011000010   LSB                             # noqa: E501
# RESULT hex:  LE    c2 02 50 32 0f 1e 60 87 39 48 49 05 00 00 00 00
#
#
# name                  type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7            7          66                                                                                                                           1000010   # noqa: E501
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1          # noqa: E501
# packet_type_id.1.VAL  u2            2           2                                                                                                                        10           # noqa: E501
# packet_type_id.1.DFF  bool          1           0                                                                                                                       0             # noqa: E501
# energy_is_reactive    bool          1           0                                                                                                                      0              # noqa: E501
# days_ago              timedelta     7           0                                                                                                               0000000               # noqa: E501
# valid                 bool          1           0                                                                                                              0                      # noqa: E501
# tariff_mask.0.tariff  bool          1           1                                                                                                             1                       # noqa: E501
# tariff_mask.1.tariff  bool          1           0                                                                                                            0                        # noqa: E501
# tariff_mask.2.tariff  bool          1           1                                                                                                           1                         # noqa: E501
# tariff_mask.3.tariff  bool          1           0                                                                                                          0                          # noqa: E501
# tariff_mask.4.tariff  bool          1           0                                                                                                         0                           # noqa: E501
# tariff_mask.5.tariff  bool          1           1                                                                                                        1                            # noqa: E501
# tariff_mask.6.tariff  bool          1           0                                                                                                       0                             # noqa: E501
# tariff_mask.7.tariff  bool          1           0                                                                                                      0                              # noqa: E501
# slot_0                u25          25      123123                                                                             0000000011110000011110011                               # noqa: E501
# slot_1                u25          25     4312123                                                    0010000011100110000111011                                                        # noqa: E501
# slot_2                u25          25        5413                           0000000000001010100100101
# slot_3                u25          25           0  0000000000000000000000000


class SmpmUlDeviceEnergy16BTariffConsumedData(Packet):
    energy_is_reactive: bool
    days_ago: timedelta
    valid: bool
    tariff_mask: Tuple[bool, bool, bool, bool, bool, bool, bool, bool]
    slot_0: int
    slot_1: int
    slot_2: int
    slot_3: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((66) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((2) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.energy_is_reactive, bool)
        result |= ((int(data.energy_is_reactive)) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 127
        result |= ((days_ago_tmp1) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.valid, bool)
        result |= ((int(data.valid)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask, tuple) and len(data.tariff_mask) == 8
        assert isinstance(data.tariff_mask[0], bool)
        result |= ((int(data.tariff_mask[0])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[1], bool)
        result |= ((int(data.tariff_mask[1])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[2], bool)
        result |= ((int(data.tariff_mask[2])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[3], bool)
        result |= ((int(data.tariff_mask[3])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[4], bool)
        result |= ((int(data.tariff_mask[4])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[5], bool)
        result |= ((int(data.tariff_mask[5])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[6], bool)
        result |= ((int(data.tariff_mask[6])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.tariff_mask[7], bool)
        result |= ((int(data.tariff_mask[7])) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.slot_0, int)
        result |= (((data.slot_0) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        assert isinstance(data.slot_1, int)
        result |= (((data.slot_1) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        assert isinstance(data.slot_2, int)
        result |= (((data.slot_2) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        assert isinstance(data.slot_3, int)
        result |= (((data.slot_3) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BTariffConsumedData':
        result__el_tmp2: Dict[str, Any] = dict()
        if 66 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 2 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp2["energy_is_reactive"] = bool(buf.shift(1))
        result__el_tmp2["days_ago"] = timedelta(seconds=buf.shift(7) * 86400)
        result__el_tmp2["valid"] = bool(buf.shift(1))
        tariff_mask_tmp3: List[bool] = []
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        tariff_mask__item_tmp4 = bool(buf.shift(1))
        tariff_mask_tmp3.append(tariff_mask__item_tmp4)
        result__el_tmp2["tariff_mask"] = tuple(tariff_mask_tmp3)
        result__el_tmp2["slot_0"] = buf.shift(25) + 0
        result__el_tmp2["slot_1"] = buf.shift(25) + 0
        result__el_tmp2["slot_2"] = buf.shift(25) + 0
        result__el_tmp2["slot_3"] = buf.shift(25) + 0
        result = SmpmUlDeviceEnergy16BTariffConsumedData(**result__el_tmp2)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        slots = [self.slot_0, self.slot_1, self.slot_2, self.slot_3]
        consumptions = []
        for tariff_number, tariff in enumerate(self.tariff_mask, 1):
            if tariff and slots:
                consumptions.append(
                    IntegrationV0MessageConsumption(
                        tariff=tariff_number,
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(slots.pop(0))),
                        resource_type=ResourceType.ENERGY_REACTIVE if self.energy_is_reactive else ResourceType.ENERGY_ACTIVE,
                        channel=1,
                        overloading_value=Decimal(str(33554431.0)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                )
        return [
            IntegrationV0MessageData(
                is_valid=self.valid,
                dt=days_ago_calculation(received_at, device_tz, time(0), self.days_ago),
                consumption=consumptions,
            ),
        ]
