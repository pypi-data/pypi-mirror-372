from decimal import Decimal
from datetime import timedelta, datetime, time, tzinfo
from typing import List, Any, Dict
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, DeviceHack, JournalDataType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, \
    IntegrationV0MessageGeneration, CounterType, ResourceType

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_daily
#
# RESULT int:        14738343083975057021112790317536029371
# RESULT bin:  MSB   00001011000101101000000001101010101010101011101100101010101010101010101001010101010111110101010010101110101010101010101010111011   LSB                                 # noqa: E501
# RESULT hex:  LE    bb aa aa ae 54 5f 55 aa aa 2a bb aa 6a 80 16 0b
#
#
# name                       type       size  value(int)                                                                                                                        data(bits)  # noqa: E501
# -------------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------  # noqa: E501
# packet_type_id.0.VAL       u7            7          59                                                                                                                           0111011  # noqa: E501
# packet_type_id.0.DFF       bool          1           1                                                                                                                          1         # noqa: E501
# packet_type_id.1.VAL       u2            2           2                                                                                                                        10          # noqa: E501
# packet_type_id.1.DFF       bool          1           0                                                                                                                       0            # noqa: E501
# energy_consumed_active     u23          23     1430869                                                                                                00101011101010101010101             # noqa: E501
# energy_consumed_reactive   u23          23     1398741                                                                         00101010101011111010101                                    # noqa: E501
# energy_generated_active    u23          23     1398101                                                  00101010101010101010101                                                           # noqa: E501
# energy_generated_reactive  u23          23     6990523                           11010101010101010111011
# days_ago                   timedelta     7           0                    0000000
# valid                      bool          1           0                   0
# error_measurement          bool          1           1                  1
# error_low_voltage          bool          1           0                 0
# error_internal_clock       bool          1           1                1
# error_flash                bool          1           1               1
# error_eeprom               bool          1           0              0
# error_radio                bool          1           1             1
# error_display              bool          1           0            0
# error_plc                  bool          1           0           0
# error_reset                bool          1           0          0
# impact_power_lost          bool          1           1         1
# impact_magnet              bool          1           1        1
# impact_cleat_tamper        bool          1           0       0
# impact_body_tamper         bool          1           1      1
# impact_radio               bool          1           0     0
# RESERVED                   u3            3           0  000


class SmpmUlDeviceEnergy16BDailyData(Packet):
    energy_consumed_active: int
    energy_consumed_reactive: int
    energy_generated_active: int
    energy_generated_reactive: int
    days_ago: timedelta
    valid: bool
    error_measurement: bool
    error_low_voltage: bool
    error_internal_clock: bool
    error_flash: bool
    error_eeprom: bool
    error_radio: bool
    error_display: bool
    error_plc: bool
    error_reset: bool
    impact_power_lost: bool
    impact_magnet: bool
    impact_cleat_tamper: bool
    impact_body_tamper: bool
    impact_radio: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((59) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((2) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.energy_consumed_active, int)
        result |= (((data.energy_consumed_active) & 8388607) & (2 ** (23) - 1)) << size
        size += 23
        assert isinstance(data.energy_consumed_reactive, int)
        result |= (((data.energy_consumed_reactive) & 8388607) & (2 ** (23) - 1)) << size
        size += 23
        assert isinstance(data.energy_generated_active, int)
        result |= (((data.energy_generated_active) & 8388607) & (2 ** (23) - 1)) << size
        size += 23
        assert isinstance(data.energy_generated_reactive, int)
        result |= (((data.energy_generated_reactive) & 8388607) & (2 ** (23) - 1)) << size
        size += 23
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 127
        result |= ((days_ago_tmp1) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.valid, bool)
        result |= ((int(data.valid)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_measurement, bool)
        result |= ((int(data.error_measurement)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_low_voltage, bool)
        result |= ((int(data.error_low_voltage)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_internal_clock, bool)
        result |= ((int(data.error_internal_clock)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_flash, bool)
        result |= ((int(data.error_flash)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_eeprom, bool)
        result |= ((int(data.error_eeprom)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_radio, bool)
        result |= ((int(data.error_radio)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_display, bool)
        result |= ((int(data.error_display)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_plc, bool)
        result |= ((int(data.error_plc)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.error_reset, bool)
        result |= ((int(data.error_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.impact_power_lost, bool)
        result |= ((int(data.impact_power_lost)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.impact_magnet, bool)
        result |= ((int(data.impact_magnet)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.impact_cleat_tamper, bool)
        result |= ((int(data.impact_cleat_tamper)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.impact_body_tamper, bool)
        result |= ((int(data.impact_body_tamper)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.impact_radio, bool)
        result |= ((int(data.impact_radio)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BDailyData':
        result__el_tmp2: Dict[str, Any] = dict()
        if 59 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 2 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp2["energy_consumed_active"] = buf.shift(23) + 0
        result__el_tmp2["energy_consumed_reactive"] = buf.shift(23) + 0
        result__el_tmp2["energy_generated_active"] = buf.shift(23) + 0
        result__el_tmp2["energy_generated_reactive"] = buf.shift(23) + 0
        result__el_tmp2["days_ago"] = timedelta(seconds=buf.shift(7) * 86400)
        result__el_tmp2["valid"] = bool(buf.shift(1))
        result__el_tmp2["error_measurement"] = bool(buf.shift(1))
        result__el_tmp2["error_low_voltage"] = bool(buf.shift(1))
        result__el_tmp2["error_internal_clock"] = bool(buf.shift(1))
        result__el_tmp2["error_flash"] = bool(buf.shift(1))
        result__el_tmp2["error_eeprom"] = bool(buf.shift(1))
        result__el_tmp2["error_radio"] = bool(buf.shift(1))
        result__el_tmp2["error_display"] = bool(buf.shift(1))
        result__el_tmp2["error_plc"] = bool(buf.shift(1))
        result__el_tmp2["error_reset"] = bool(buf.shift(1))
        result__el_tmp2["impact_power_lost"] = bool(buf.shift(1))
        result__el_tmp2["impact_magnet"] = bool(buf.shift(1))
        result__el_tmp2["impact_cleat_tamper"] = bool(buf.shift(1))
        result__el_tmp2["impact_body_tamper"] = bool(buf.shift(1))
        result__el_tmp2["impact_radio"] = bool(buf.shift(1))
        result = SmpmUlDeviceEnergy16BDailyData(**result__el_tmp2)
        buf.shift(3)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        overloading_value = 8388607.0
        hacks = kwargs.get('hacks', [])
        if DeviceHack.electricity_daily_packet_overload_value in hacks:
            overloading_value = 838861.0
        return [
            IntegrationV0MessageData(
                dt=days_ago_calculation(received_at, device_tz, time(0), self.days_ago),
                is_valid=self.valid,
                consumption=[
                    IntegrationV0MessageConsumption(
                        value=Decimal(str(self.energy_consumed_active)),
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.ENERGY_ACTIVE,
                        channel=1,
                        overloading_value=Decimal(str(overloading_value)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageConsumption(
                        value=Decimal(str(self.energy_consumed_reactive)),
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.ENERGY_REACTIVE,
                        channel=1,
                        overloading_value=Decimal(str(overloading_value)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.ERROR_MEASUREMENT] if self.error_measurement else []),
                    *([IntegrationV0MessageEvent.ERROR_LOW_VOLTAGE] if self.error_low_voltage else []),
                    *([IntegrationV0MessageEvent.ERROR_INTERNAL_CLOCK] if self.error_internal_clock else []),
                    *([IntegrationV0MessageEvent.ERROR_FLASH] if self.error_flash else []),
                    *([IntegrationV0MessageEvent.ERROR_EEPROM] if self.error_eeprom else []),
                    *([IntegrationV0MessageEvent.ERROR_RADIO] if self.error_radio else []),
                    *([IntegrationV0MessageEvent.ERROR_DISPLAY] if self.error_display else []),
                    *([IntegrationV0MessageEvent.ERROR_PLC] if self.error_plc else []),
                    *([IntegrationV0MessageEvent.ERROR_RESET] if self.error_reset else []),
                    *([IntegrationV0MessageEvent.IMPACT_POWER_LOST] if self.impact_power_lost else []),
                    *([IntegrationV0MessageEvent.IMPACT_MAGNET] if self.impact_magnet else []),
                    *([IntegrationV0MessageEvent.IMPACT_CLEAT_TAMPER] if self.impact_cleat_tamper else []),
                    *([IntegrationV0MessageEvent.IMPACT_RADIO] if self.impact_radio else []),
                ],
                generation=[
                    IntegrationV0MessageGeneration(
                        value=Decimal(str(self.energy_generated_active)),
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.ENERGY_ACTIVE,
                        overloading_value=Decimal(str(overloading_value)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageGeneration(
                        value=Decimal(str(self.energy_generated_reactive)),
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.ENERGY_REACTIVE,
                        overloading_value=Decimal(str(overloading_value)),
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
            ),
        ]
