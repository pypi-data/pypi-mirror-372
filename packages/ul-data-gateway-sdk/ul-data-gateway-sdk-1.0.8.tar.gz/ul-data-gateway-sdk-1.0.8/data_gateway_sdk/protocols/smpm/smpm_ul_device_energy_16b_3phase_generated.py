from decimal import Decimal
from datetime import timedelta, datetime, time, tzinfo
from typing import Dict, Any, List

from data_aggregator_sdk.constants.enums import DeviceHack, JournalDataType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, CounterType, \
    ResourceType, IntegrationV0MessageGeneration

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_3phase_generated
#
# RESULT int:        6653256196879938732392428594653037259
# RESULT bin:  MSB   00000101000000010101111011011011010011000101011101100000000000010000110110010000000000000001111000001111001100000000001011001011   LSB                             # noqa: E501
# RESULT hex:  LE    cb 02 30 0f 1e 00 90 0d 01 60 57 4c db 5e 01 05
#
#
# name                  type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7            7          75                                                                                                                           1001011   # noqa: E501
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1          # noqa: E501
# packet_type_id.1.VAL  u2            2           2                                                                                                                        10           # noqa: E501
# packet_type_id.1.DFF  bool          1           0                                                                                                                       0             # noqa: E501
# energy_is_reactive    bool          1           0                                                                                                                      0              # noqa: E501
# days_ago              timedelta     7           0                                                                                                               0000000               # noqa: E501
# valid                 bool          1           0                                                                                                              0                      # noqa: E501
# total                 u32          32      123123                                                                              00000000000000011110000011110011                       # noqa: E501
# phase_a               u25          25        4313                                                     0000000000001000011011001                                                       # noqa: E501
# phase_b               u25          25    14312123                            0110110100110001010111011
# phase_c               u25          25     1312123   0000101000000010101111011
# RESERVED              u1            1           0  0


class SmpmUlDeviceEnergy16B3PhaseGeneratedData(Packet):
    energy_is_reactive: bool
    days_ago: timedelta
    valid: bool
    total: int
    phase_a: int
    phase_b: int
    phase_c: int

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((75) & (2 ** (7) - 1)) << size
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
        assert isinstance(data.total, int)
        result |= (((data.total) & 4294967295) & (2 ** (32) - 1)) << size
        size += 32
        assert isinstance(data.phase_a, int)
        result |= (((data.phase_a) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        assert isinstance(data.phase_b, int)
        result |= (((data.phase_b) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        assert isinstance(data.phase_c, int)
        result |= (((data.phase_c) & 33554431) & (2 ** (25) - 1)) << size
        size += 25
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16B3PhaseGeneratedData':
        result__el_tmp2: Dict[str, Any] = dict()
        if 75 != buf.shift(7):
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
        result__el_tmp2["total"] = buf.shift(32) + 0
        result__el_tmp2["phase_a"] = buf.shift(25) + 0
        result__el_tmp2["phase_b"] = buf.shift(25) + 0
        result__el_tmp2["phase_c"] = buf.shift(25) + 0
        result = SmpmUlDeviceEnergy16B3PhaseGeneratedData(**result__el_tmp2)
        buf.shift(1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        resource_type = ResourceType.ENERGY_REACTIVE if self.energy_is_reactive else ResourceType.ENERGY_ACTIVE
        total_energy_overload_value = 4294967295.0
        hacks = kwargs.get('hacks', [])
        if DeviceHack.electricity_phase_packet_generated_total_enrg_overload_value in hacks:
            total_energy_overload_value = 3355443.0
        return [
            IntegrationV0MessageData(
                is_valid=self.valid,
                dt=days_ago_calculation(received_at, device_tz, time(0), self.days_ago),
                generation=[
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(self.total)),
                        resource_type=resource_type,
                        overloading_value=Decimal(str(total_energy_overload_value)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.ENERGY_PHASE_A,
                        value=Decimal(str(self.phase_a)),
                        resource_type=resource_type,
                        overloading_value=Decimal(str(33554431.0)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.ENERGY_PHASE_B,
                        value=Decimal(str(self.phase_b)),
                        resource_type=resource_type,
                        overloading_value=Decimal(str(33554431.0)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageGeneration(
                        counter_type=CounterType.ENERGY_PHASE_C,
                        value=Decimal(str(self.phase_c)),
                        resource_type=resource_type,
                        overloading_value=Decimal(str(33554431.0)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
            ),
        ]
