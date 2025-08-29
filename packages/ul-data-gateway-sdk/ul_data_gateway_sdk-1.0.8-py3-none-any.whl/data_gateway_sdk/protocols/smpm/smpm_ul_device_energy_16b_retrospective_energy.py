from decimal import Decimal
from datetime import datetime, tzinfo, time
from enum import IntEnum, unique
from typing import Dict, Any, List

from data_aggregator_sdk.constants.enums import JournalDataType
from data_aggregator_sdk.integration_message import IntegrationV0MessageConsumption, IntegrationV0MessageGeneration, IntegrationV0MessageData, \
    CounterType, ResourceType
from dateutil.relativedelta import relativedelta

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.first_day_of_month import first_day_of_month
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_retrospective_energy
#
# RESULT int:        60967556582773559757215997875516304
# RESULT bin:  MSB   00000000 00001011 10111101 11101110 11000000 00000000 00000000 00000000 10000100 00100111 01000011 01100111 10001110 00011000 11110011 10010000   LSB
# RESULT hex:  LE    90 f3 18 8e 67 43 27 84 00 00 00 c0 ee bd 0b 00
#
# name                       type    size  value(int)                                                                                                                        data(bits) # noqa: E501
# -------------------------  ------  ----  ----------  -------------------------------------------------------------------------------------------------------------------------------- # noqa: E501
# packet_type_id_enum.0.VAL  u7         7          16                                                                                                                           0010000 # noqa: E501
# packet_type_id_enum.0.DFF  bool       1           1                                                                                                                          1
# packet_type_id_enum.1.VAL  u2         2           3                                                                                                                        11
# packet_type_id_enum.1.DFF  bool       1           0                                                                                                                       0
# is_valid                   bool       1           0                                                                                                                      0
# period_ago                 u5         5          15                                                                                                                 01111
# value_current              uf27p2    27    28559116                                                                                      001101100111100011100001100
# value_previous_1_delta     uf24p2    24      541300                                                              000010000100001001110100
# value_previous_2_delta     uf24p2    24           0                                      000000000000000000000000
# value_previous_3_delta     uf24p2    24    12312300              101110111101111011101100
# RESERVED                   u12       12           0  000000000000

@unique
class SmpmUlDeviceEnergy16bRetrospectiveEnergyIds(IntEnum):
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


class SmpmUlDeviceEnergy16BRetrospectiveEnergyData(Packet):
    packet_type_id_enum: SmpmUlDeviceEnergy16bRetrospectiveEnergyIds
    is_valid: bool
    period_ago: int
    value_current: float
    value_previous_1_delta: float
    value_previous_2_delta: float
    value_previous_3_delta: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        packet_type_id_enum__value_int_tmp1 = 0
        packet_type_id_enum__value_size_tmp2 = 0
        assert isinstance(data.packet_type_id_enum, SmpmUlDeviceEnergy16bRetrospectiveEnergyIds)
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
        assert isinstance(data.is_valid, bool)
        result |= ((int(data.is_valid)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.period_ago, int)
        assert 0 <= data.period_ago <= 31
        result |= ((data.period_ago) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.value_current, (int, float))
        result |= ((int(round(float(data.value_current) * 100.0, 0)) & 134217727) & (2 ** (27) - 1)) << size
        size += 27
        assert isinstance(data.value_previous_1_delta, (int, float))
        result |= ((int(round(float(data.value_previous_1_delta) * 100.0, 0)) & 16777215) & (2 ** (24) - 1)) << size
        size += 24
        assert isinstance(data.value_previous_2_delta, (int, float))
        result |= ((int(round(float(data.value_previous_2_delta) * 100.0, 0)) & 16777215) & (2 ** (24) - 1)) << size
        size += 24
        assert isinstance(data.value_previous_3_delta, (int, float))
        result |= ((int(round(float(data.value_previous_3_delta) * 100.0, 0)) & 16777215) & (2 ** (24) - 1)) << size
        size += 24
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BRetrospectiveEnergyData':
        result__el_tmp8: Dict[str, Any] = dict()
        packet_type_id_enum__res_tmp9 = 0
        packet_type_id_enum__steps_tmp10 = (8, 3, 3, 3)
        packet_type_id_enum__res_size_tmp11 = 0
        packet_type_id_enum__step_tmp12 = 0
        for packet_type_id_enum__i_tmp14 in range(32):
            packet_type_id_enum__step_tmp12 = (packet_type_id_enum__steps_tmp10[packet_type_id_enum__i_tmp14] if packet_type_id_enum__i_tmp14 < len(
                packet_type_id_enum__steps_tmp10) else packet_type_id_enum__steps_tmp10[-1]) - 1
            packet_type_id_enum__res_tmp9 |= buf.shift(packet_type_id_enum__step_tmp12) << packet_type_id_enum__res_size_tmp11
            packet_type_id_enum__res_size_tmp11 += packet_type_id_enum__step_tmp12
            packet_type_id_enum__dff_tmp13 = bool(buf.shift(1))
            if not packet_type_id_enum__dff_tmp13:
                break
        packet_type_id_enum__buf_tmp15 = buf
        buf = BufRef(packet_type_id_enum__res_tmp9, stop_on_buffer_end=True)
        result__el_tmp8["packet_type_id_enum"] = SmpmUlDeviceEnergy16bRetrospectiveEnergyIds(buf.shift(11))
        buf = packet_type_id_enum__buf_tmp15
        result__el_tmp8["is_valid"] = bool(buf.shift(1))
        result__el_tmp8["period_ago"] = buf.shift(5) + 0
        result__el_tmp8["value_current"] = round(buf.shift(27) / 100.0, 2)
        result__el_tmp8["value_previous_1_delta"] = round(buf.shift(24) / 100.0, 2)
        result__el_tmp8["value_previous_2_delta"] = round(buf.shift(24) / 100.0, 2)
        result__el_tmp8["value_previous_3_delta"] = round(buf.shift(24) / 100.0, 2)
        result = SmpmUlDeviceEnergy16BRetrospectiveEnergyData(**result__el_tmp8)
        buf.shift(12)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        resource_type: ResourceType
        tariff: int
        journal_data_type_for_end: JournalDataType
        period_ago: relativedelta

        if self.packet_type_id_enum in {401, 410}:
            tariff = 1
        elif self.packet_type_id_enum in {402, 411}:
            tariff = 2
        elif self.packet_type_id_enum in {403, 412}:
            tariff = 3
        elif self.packet_type_id_enum in {404, 413}:
            tariff = 4
        elif self.packet_type_id_enum in {405, 414}:
            tariff = 0
        else:
            tariff = -1

        if self.packet_type_id_enum in {406, 408, 415, 417}:
            resource_type = ResourceType.ENERGY_REACTIVE
        else:
            resource_type = ResourceType.ENERGY_ACTIVE

        if self.packet_type_id_enum in {400, 401, 402, 403, 404, 405, 406, 407, 408}:
            journal_data_type_for_end = JournalDataType.END_OF_DAY
            period_ago = relativedelta(days=self.period_ago)
            delta = relativedelta(days=1)
            dt_value_current = days_ago_calculation(received_at, device_tz, time(0), period_ago) if self.period_ago != 0 else received_at
            dt_value_previous_1_delta = days_ago_calculation(received_at, device_tz, time(0), period_ago + delta)
            dt_value_previous_2_delta = days_ago_calculation(received_at, device_tz, time(0), period_ago + delta * 2)
            dt_value_previous_3_delta = days_ago_calculation(received_at, device_tz, time(0), period_ago + delta * 3)
        else:
            journal_data_type_for_end = JournalDataType.END_OF_MONTH
            period_ago = relativedelta(months=self.period_ago)
            delta = relativedelta(months=1)
            dt_value_current = first_day_of_month(days_ago_calculation(received_at, device_tz, time(0), period_ago - delta), device_tz) if self.period_ago != 0 else received_at
            dt_value_previous_1_delta = first_day_of_month(days_ago_calculation(received_at, device_tz, time(0), period_ago), device_tz)
            dt_value_previous_2_delta = first_day_of_month(days_ago_calculation(received_at, device_tz, time(0), period_ago + delta), device_tz)
            dt_value_previous_3_delta = first_day_of_month(days_ago_calculation(received_at, device_tz, time(0), period_ago + delta * 2), device_tz)

        integration_message_data = []
        # adding value_current with checking validity
        if self.is_valid:
            integration_message_data.append(
                IntegrationV0MessageData(
                    is_valid=self.is_valid,
                    dt=dt_value_current,
                    consumption=[
                        IntegrationV0MessageConsumption(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current)),
                            resource_type=resource_type,
                            channel=1,
                            overloading_value=Decimal(str(1342177.27)),
                            journal_data_type=journal_data_type_for_end if self.period_ago != 0 else JournalDataType.CURRENT,
                        ),
                    ] if self.packet_type_id_enum not in {407, 408, 416, 417} else [],
                    generation=[
                        IntegrationV0MessageGeneration(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current)),
                            resource_type=resource_type,
                            overloading_value=Decimal(str(1342177.27)),
                            journal_data_type=journal_data_type_for_end if self.period_ago != 0 else JournalDataType.CURRENT,
                        ),
                    ] if self.packet_type_id_enum in {407, 408, 416, 417} else [],
                ))
            # adding END_OF_DAY / END_OF_MONTH values with checking validity
            integration_message_data.append(
                IntegrationV0MessageData(
                    is_valid=self.is_valid,
                    dt=dt_value_previous_1_delta,
                    consumption=[
                        IntegrationV0MessageConsumption(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current - self.value_previous_1_delta)),
                            resource_type=resource_type,
                            channel=1,
                            overloading_value=Decimal(str(167772.15)),
                            journal_data_type=journal_data_type_for_end,
                        ),
                    ] if self.packet_type_id_enum not in {407, 408, 416, 417} else [],
                    generation=[
                        IntegrationV0MessageGeneration(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current - self.value_previous_1_delta)),
                            resource_type=resource_type,
                            overloading_value=Decimal(str(167772.15)),
                            journal_data_type=journal_data_type_for_end,
                        ),
                    ] if self.packet_type_id_enum in {407, 408, 416, 417} else [],
                ))
            integration_message_data.append(
                IntegrationV0MessageData(
                    is_valid=self.is_valid,
                    dt=dt_value_previous_2_delta,
                    consumption=[
                        IntegrationV0MessageConsumption(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current - self.value_previous_2_delta - self.value_previous_1_delta)),
                            resource_type=resource_type,
                            channel=1,
                            overloading_value=Decimal(str(167772.15)),
                            journal_data_type=journal_data_type_for_end,
                        ),
                    ] if self.packet_type_id_enum not in {407, 408, 416, 417} else [],
                    generation=[
                        IntegrationV0MessageGeneration(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current - self.value_previous_2_delta - self.value_previous_1_delta)),
                            resource_type=resource_type,
                            overloading_value=Decimal(str(167772.15)),
                            journal_data_type=journal_data_type_for_end,
                        ),
                    ] if self.packet_type_id_enum in {407, 408, 416, 417} else [],
                ))
            integration_message_data.append(
                IntegrationV0MessageData(
                    is_valid=self.is_valid,
                    dt=dt_value_previous_3_delta,
                    consumption=[
                        IntegrationV0MessageConsumption(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current - self.value_previous_3_delta - self.value_previous_2_delta - self.value_previous_1_delta)),
                            resource_type=resource_type,
                            channel=1,
                            overloading_value=Decimal(str(167772.15)),
                            journal_data_type=journal_data_type_for_end,
                        ),
                    ] if self.packet_type_id_enum not in {407, 408, 416, 417} else [],
                    generation=[
                        IntegrationV0MessageGeneration(
                            tariff=tariff,
                            counter_type=CounterType.COMMON,
                            value=Decimal(str(self.value_current - self.value_previous_3_delta - self.value_previous_2_delta - self.value_previous_1_delta)),
                            resource_type=resource_type,
                            overloading_value=Decimal(str(167772.15)),
                            journal_data_type=journal_data_type_for_end,
                        ),
                    ] if self.packet_type_id_enum in {407, 408, 416, 417} else [],
                ))
        return integration_message_data
