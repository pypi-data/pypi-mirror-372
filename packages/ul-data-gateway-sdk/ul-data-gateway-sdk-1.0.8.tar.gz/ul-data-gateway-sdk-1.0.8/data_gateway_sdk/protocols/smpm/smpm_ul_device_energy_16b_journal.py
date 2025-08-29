from datetime import timedelta, datetime, time, tzinfo
from enum import IntEnum, unique
from typing import List, Any, Dict, Tuple, NamedTuple
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_journal
#
# RESULT int:        952893555
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00111000 11001100 00000000 01110011   LSB                                      # noqa: E501
# RESULT hex:  LE    73 00 cc 38 00 00 00 00 00 00 00 00 00 00 00 00
#
# name                    type                              size  value(int)                                                                                                                        data(bits)  # noqa: E501
# ----------------------  --------------------------------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------  # noqa: E501
# packet_type_id.0.VAL    u7                                   7         115                                                                                                                           1110011  # noqa: E501
# packet_type_id.0.DFF    bool                                 1           0                                                                                                                          0         # noqa: E501
# days_ago                timedelta                            7           0                                                                                                                   0000000          # noqa: E501
# valid                   bool                                 1           0                                                                                                                  0                 # noqa: E501
# time_offset             timedelta                            6          12                                                                                                            001100                  # noqa: E501
# journal.0.event.offset  timedelta                            5           3                                                                                                       00011                        # noqa: E501
# journal.0.event.code    SmpmUlDeviceEnergy16bJournalType     8           7                                                                                               00000111                             # noqa: E501
# journal.1.event.offset  timedelta                            5           0                                                                                          00000                                     # noqa: E501
# journal.1.event.code    SmpmUlDeviceEnergy16bJournalType     8           0                                                                                  00000000                                          # noqa: E501
# journal.2.event.offset  timedelta                            5           0                                                                             00000                                                  # noqa: E501
# journal.2.event.code    SmpmUlDeviceEnergy16bJournalType     8           0                                                                     00000000                                                       # noqa: E501
# journal.3.event.offset  timedelta                            5           0                                                                00000                                                               # noqa: E501
# journal.3.event.code    SmpmUlDeviceEnergy16bJournalType     8           0                                                        00000000                                                                    # noqa: E501
# journal.4.event.offset  timedelta                            5           0                                                   00000                                                                            # noqa: E501
# journal.4.event.code    SmpmUlDeviceEnergy16bJournalType     8           0                                           00000000                                                                                 # noqa: E501
# journal.5.event.offset  timedelta                            5           0                                      00000
# journal.5.event.code    SmpmUlDeviceEnergy16bJournalType     8           0                              00000000
# journal.6.event.offset  timedelta                            5           0                         00000
# journal.6.event.code    SmpmUlDeviceEnergy16bJournalType     8           0                 00000000
# journal.7.event.offset  timedelta                            5           0            00000
# journal.7.event.code    SmpmUlDeviceEnergy16bJournalType     8           0    00000000
# RESERVED                u2                                   2           0  00


@unique
class SmpmUlDeviceEnergy16bJournalType(IntEnum):
    NONE = 0
    SUCCESSFUL_AUTO_DIAGNOSTIC = 1
    SWITCH_WINTER_DAYLIGHT = 2
    SWITCH_SUMMER_DAYLIGHT = 3
    SETUP_UPDATE = 5
    RECORD_DATETIME = 6
    CHANGE_OFFSET_DAILY_CLOCK = 7
    PERMISSION_SWITCH_DAYLIGHT_ON = 8
    PERMISSION_SWITCH_DAYLIGHT_OFF = 9
    CHANGE_DATE_TIME_SWITCH_DAYLIGHT = 10
    ERASE_EEPROM = 12
    NULLIFY_TARIFF_ACCUMULATION = 13
    NULLIFY_INTERVAL_ACCUMULATION = 14
    RESET_PASSWORD = 15
    RESET_POWER_LOST_TIME_COUNTER = 16
    RESET_MAGNET_IMPACT_TIME_COUNTER = 17
    RESET_POWER_INCREASE_TIME_COUNTER = 18
    RESET_POWER_DECREASE_TIME_COUNTER = 19
    RESET_MAINTS_FREQ_DIVERGENCE_TIME_COUNTER = 20
    RESET_POWER_OVER_LIMIT_TIME_COUNTER = 22
    CHANGE_CAPACITY_DATA_LCD = 25
    CHANGE_TARIFF_METHODS = 26
    CHANGE_TARIFF_PROGRAMS = 27
    CHANGE_ACTUAL_SEASON_SCHEDULES = 28
    CHANGE_CONSUMPTION_LIMIT = 34
    CHANGE_LOW_THRESHOLD_VOLTAGE = 35
    CHANGE_HIGH_THRESHOLD_VOLTAGE = 36
    CHANGE_MAINTS_FREQ_THRESHOLD = 37
    CHANGE_THRESHOLD_LOW_CONSUMPTION = 39
    RECHARGE_ENERGY_PAYMENT = 40
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_INTERNAL_CLOCK = 58
    ABNORMAL_COUNTER_AUTOSTART = 59
    EXTERNAL_POWER_LOST = 60
    EXTERNAL_POWER_DETECTED = 61
    START_POWER_OVER_LIMIT = 68
    STOP_POWER_OVER_LIMIT = 69
    ENERGY_OVER_LIMIT_1 = 70
    ENERGY_OVER_LIMIT_2 = 71
    ENERGY_OVER_LIMIT_3 = 72
    WRONG_PASSWORD_BLOCK = 73
    WRONG_PASSWORD_APPEAL = 74
    EXHAUST_DAILY_BATTERY_LIFE_LIMIT = 75
    START_MAGNET_IMPACT = 76
    STOP_MAGNET_IMPACT = 77
    VIOLATION_TERMINAL_BLOCK_SEAL = 78
    RECOVERY_TERMINAL_BLOCK_SEAL = 79
    VIOLATION_CASE_SEAL = 80
    RECOVERY_CASE_SEAL = 81
    TIME_OUT_SYNC_LIMIT = 84
    CRITICAL_DIVERGENCE_TIME = 85
    OVERHEAT_COUNTER_START = 90
    OVERHEAT_COUNTER_STOP = 91
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEMORY = 92
    LOW_BATTERY_CAPACITY = 94
    RECOVERY_BATTERY_WORKING_VOLTAGE = 95
    LOW_CONSUMPTION = 96
    RESET_FLAG_LOW_CONSUMPTION = 97
    CHANGE_VALIDATION_SETTINGS = 113
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEASUREMENT_BLOCK = 116
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_CALCULATION_BLOCK = 117
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_POWER_BLOCK = 118
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_SCREEN = 119
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_RADIO = 120
    MAINS_VOLTAGE_LOST_PHASE_A_START = 134
    MAINS_VOLTAGE_LOST_PHASE_A_STOP = 135
    MAINS_VOLTAGE_LOST_PHASE_B_START = 136
    MAINS_VOLTAGE_LOST_PHASE_B_STOP = 137
    MAINS_VOLTAGE_LOST_PHASE_C_START = 138
    MAINS_VOLTAGE_LOST_PHASE_C_STOP = 139
    VOLTAGE_LAYDOWN_PHASE_A_START = 140
    VOLTAGE_LAYDOWN_PHASE_A_STOP = 141
    VOLTAGE_LAYDOWN_PHASE_B_START = 142
    VOLTAGE_LAYDOWN_PHASE_B_STOP = 143
    VOLTAGE_LAYDOWN_PHASE_C_START = 144
    VOLTAGE_LAYDOWN_PHASE_C_STOP = 145
    OVERVOLTAGE_PHASE_A_START = 146
    OVERVOLTAGE_PHASE_A_STOP = 147
    OVERVOLTAGE_PHASE_B_START = 148
    OVERVOLTAGE_PHASE_B_STOP = 149
    OVERVOLTAGE_PHASE_C_START = 150
    OVERVOLTAGE_PHASE_C_STOP = 151
    OVERCURRENT_PHASE_A_START = 152
    OVERCURRENT_PHASE_A_STOP = 153
    OVERCURRENT_PHASE_B_START = 154
    OVERCURRENT_PHASE_B_STOP = 155
    OVERCURRENT_PHASE_C_START = 156
    OVERCURRENT_PHASE_C_STOP = 157
    CURRENT_SUM_THRESHOLD_LOW_START = 158
    CURRENT_SUM_THRESHOLD_LOW_STOP = 159
    FREQ_OUT_PHASE_A_START = 160
    FREQ_OUT_PHASE_A_STOP = 161
    FREQ_OUT_PHASE_B_START = 162
    FREQ_OUT_PHASE_B_STOP = 163
    FREQ_OUT_PHASE_C_START = 164
    FREQ_OUT_PHASE_C_STOP = 165
    PHASE_ORDER_DISTURBANCE_START = 166
    PHASE_ORDER_DISTURBANCE_STOP = 167
    RADIO_IMPACT_START = 169
    RADIO_IMPACT_STOP = 170
    DAYLIGHT_TIME_SWITCH = 173
    DAYLIGHT_TIME_MODE_DATES_CHANGE = 174
    INTERNAL_CLOCK_SYNC = 175
    METROLOGY_CHANGE = 176
    PROFILE_CONF_CHANGE = 177
    TARIFFICATION_METHOD_CHANGE = 178
    PERMISSION_CHANGE_SETTINGS_POWER_CONTROL = 179
    CONTROL_LEVEL_MAINS_CHANGE = 180
    PERMISSION_CHANGE_SETTINGS_CONSUMPTION_CONTROL = 181
    LOAD_RELAY_CONDITION_SETTINGS_CHANGE = 182
    SIGNALIZATION_RELAY_CONDITION_SETTINGS_CHANGE = 183
    INTERFACE_SIGNALIZATION_CONDITION_SETTINGS_CHANGE = 184
    INDICATION_SETTINGS_CHANGE = 185
    SOUND_SIGNAL_CONDITION_SETTINGS_CHANGE = 186
    LOAD_RELAY_STATE_CHANGE = 187
    SIGNALIZATION_RELAY_STATE_CHANGE = 188

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


EVENTS_MAP = {
    SmpmUlDeviceEnergy16bJournalType.NONE: IntegrationV0MessageEvent.NONE,
    SmpmUlDeviceEnergy16bJournalType.SUCCESSFUL_AUTO_DIAGNOSTIC: IntegrationV0MessageEvent.SUCCESSFUL_AUTO_DIAGNOSTIC,
    SmpmUlDeviceEnergy16bJournalType.SETUP_UPDATE: IntegrationV0MessageEvent.SETUP_UPDATE,
    SmpmUlDeviceEnergy16bJournalType.SWITCH_WINTER_DAYLIGHT: IntegrationV0MessageEvent.SWITCH_WINTER_DAYLIGHT,
    SmpmUlDeviceEnergy16bJournalType.SWITCH_SUMMER_DAYLIGHT: IntegrationV0MessageEvent.SWITCH_SUMMER_DAYLIGHT,
    SmpmUlDeviceEnergy16bJournalType.RECORD_DATETIME: IntegrationV0MessageEvent.RECORD_DATETIME,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_OFFSET_DAILY_CLOCK: IntegrationV0MessageEvent.CHANGE_OFFSET_DAILY_CLOCK,
    SmpmUlDeviceEnergy16bJournalType.PERMISSION_SWITCH_DAYLIGHT_ON: IntegrationV0MessageEvent.PERMISSION_SWITCH_DAYLIGHT_ON,
    SmpmUlDeviceEnergy16bJournalType.PERMISSION_SWITCH_DAYLIGHT_OFF: IntegrationV0MessageEvent.PERMISSION_SWITCH_DAYLIGHT_OFF,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_DATE_TIME_SWITCH_DAYLIGHT: IntegrationV0MessageEvent.CHANGE_DATE_TIME_SWITCH_DAYLIGHT,
    SmpmUlDeviceEnergy16bJournalType.ERASE_EEPROM: IntegrationV0MessageEvent.ERASE_EEPROM,
    SmpmUlDeviceEnergy16bJournalType.NULLIFY_TARIFF_ACCUMULATION: IntegrationV0MessageEvent.NULLIFY_TARIFF_ACCUMULATION,
    SmpmUlDeviceEnergy16bJournalType.NULLIFY_INTERVAL_ACCUMULATION: IntegrationV0MessageEvent.NULLIFY_INTERVAL_ACCUMULATION,
    SmpmUlDeviceEnergy16bJournalType.RESET_PASSWORD: IntegrationV0MessageEvent.RESET_PASSWORD,
    SmpmUlDeviceEnergy16bJournalType.RESET_POWER_LOST_TIME_COUNTER: IntegrationV0MessageEvent.RESET_POWER_LOST_TIME_COUNTER,
    SmpmUlDeviceEnergy16bJournalType.RESET_MAGNET_IMPACT_TIME_COUNTER: IntegrationV0MessageEvent.RESET_MAGNET_IMPACT_TIME_COUNTER,
    SmpmUlDeviceEnergy16bJournalType.RESET_POWER_INCREASE_TIME_COUNTER: IntegrationV0MessageEvent.RESET_POWER_INCREASE_TIME_COUNTER,
    SmpmUlDeviceEnergy16bJournalType.RESET_POWER_DECREASE_TIME_COUNTER: IntegrationV0MessageEvent.RESET_POWER_DECREASE_TIME_COUNTER,
    SmpmUlDeviceEnergy16bJournalType.RESET_MAINTS_FREQ_DIVERGENCE_TIME_COUNTER: IntegrationV0MessageEvent.RESET_MAINTS_FREQ_DIVERGENCE_TIME_COUNTER,
    SmpmUlDeviceEnergy16bJournalType.RESET_POWER_OVER_LIMIT_TIME_COUNTER: IntegrationV0MessageEvent.RESET_POWER_OVER_LIMIT_TIME_COUNTER,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_CAPACITY_DATA_LCD: IntegrationV0MessageEvent.CHANGE_CAPACITY_DATA_LCD,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_TARIFF_METHODS: IntegrationV0MessageEvent.CHANGE_TARIFF_METHODS,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_TARIFF_PROGRAMS: IntegrationV0MessageEvent.CHANGE_TARIFF_PROGRAMS,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_ACTUAL_SEASON_SCHEDULES: IntegrationV0MessageEvent.CHANGE_ACTUAL_SEASON_SCHEDULES,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_CONSUMPTION_LIMIT: IntegrationV0MessageEvent.CHANGE_CONSUMPTION_LIMIT,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_LOW_THRESHOLD_VOLTAGE: IntegrationV0MessageEvent.CHANGE_LOW_THRESHOLD_VOLTAGE,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_HIGH_THRESHOLD_VOLTAGE: IntegrationV0MessageEvent.CHANGE_HIGH_THRESHOLD_VOLTAGE,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_MAINTS_FREQ_THRESHOLD: IntegrationV0MessageEvent.CHANGE_MAINTS_FREQ_THRESHOLD,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_THRESHOLD_LOW_CONSUMPTION: IntegrationV0MessageEvent.CHANGE_THRESHOLD_LOW_CONSUMPTION,
    SmpmUlDeviceEnergy16bJournalType.RECHARGE_ENERGY_PAYMENT: IntegrationV0MessageEvent.RECHARGE_ENERGY_PAYMENT,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_INTERNAL_CLOCK: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_INTERNAL_CLOCK,
    SmpmUlDeviceEnergy16bJournalType.ABNORMAL_COUNTER_AUTOSTART: IntegrationV0MessageEvent.ABNORMAL_COUNTER_AUTOSTART,
    SmpmUlDeviceEnergy16bJournalType.EXTERNAL_POWER_LOST: IntegrationV0MessageEvent.EXTERNAL_POWER_LOST,
    SmpmUlDeviceEnergy16bJournalType.EXTERNAL_POWER_DETECTED: IntegrationV0MessageEvent.EXTERNAL_POWER_DETECTED,
    SmpmUlDeviceEnergy16bJournalType.START_POWER_OVER_LIMIT: IntegrationV0MessageEvent.START_POWER_OVER_LIMIT,
    SmpmUlDeviceEnergy16bJournalType.STOP_POWER_OVER_LIMIT: IntegrationV0MessageEvent.STOP_POWER_OVER_LIMIT,
    SmpmUlDeviceEnergy16bJournalType.ENERGY_OVER_LIMIT_1: IntegrationV0MessageEvent.ENERGY_OVER_LIMIT_1,
    SmpmUlDeviceEnergy16bJournalType.ENERGY_OVER_LIMIT_2: IntegrationV0MessageEvent.ENERGY_OVER_LIMIT_2,
    SmpmUlDeviceEnergy16bJournalType.ENERGY_OVER_LIMIT_3: IntegrationV0MessageEvent.ENERGY_OVER_LIMIT_3,
    SmpmUlDeviceEnergy16bJournalType.WRONG_PASSWORD_BLOCK: IntegrationV0MessageEvent.WRONG_PASSWORD_BLOCK,
    SmpmUlDeviceEnergy16bJournalType.WRONG_PASSWORD_APPEAL: IntegrationV0MessageEvent.WRONG_PASSWORD_APPEAL,
    SmpmUlDeviceEnergy16bJournalType.EXHAUST_DAILY_BATTERY_LIFE_LIMIT: IntegrationV0MessageEvent.EXHAUST_DAILY_BATTERY_LIFE_LIMIT,
    SmpmUlDeviceEnergy16bJournalType.START_MAGNET_IMPACT: IntegrationV0MessageEvent.START_MAGNET_IMPACT,
    SmpmUlDeviceEnergy16bJournalType.STOP_MAGNET_IMPACT: IntegrationV0MessageEvent.STOP_MAGNET_IMPACT,
    SmpmUlDeviceEnergy16bJournalType.VIOLATION_TERMINAL_BLOCK_SEAL: IntegrationV0MessageEvent.VIOLATION_TERMINAL_BLOCK_SEAL,
    SmpmUlDeviceEnergy16bJournalType.RECOVERY_TERMINAL_BLOCK_SEAL: IntegrationV0MessageEvent.RECOVERY_TERMINAL_BLOCK_SEAL,
    SmpmUlDeviceEnergy16bJournalType.VIOLATION_CASE_SEAL: IntegrationV0MessageEvent.VIOLATION_CASE_SEAL,
    SmpmUlDeviceEnergy16bJournalType.RECOVERY_CASE_SEAL: IntegrationV0MessageEvent.RECOVERY_CASE_SEAL,
    SmpmUlDeviceEnergy16bJournalType.TIME_OUT_SYNC_LIMIT: IntegrationV0MessageEvent.TIME_OUT_SYNC_LIMIT,
    SmpmUlDeviceEnergy16bJournalType.CRITICAL_DIVERGENCE_TIME: IntegrationV0MessageEvent.CRITICAL_DIVERGENCE_TIME,
    SmpmUlDeviceEnergy16bJournalType.OVERHEAT_COUNTER_START: IntegrationV0MessageEvent.OVERHEAT_COUNTER_START,
    SmpmUlDeviceEnergy16bJournalType.OVERHEAT_COUNTER_STOP: IntegrationV0MessageEvent.OVERHEAT_COUNTER_STOP,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEMORY: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEMORY,
    SmpmUlDeviceEnergy16bJournalType.LOW_BATTERY_CAPACITY: IntegrationV0MessageEvent.LOW_BATTERY_CAPACITY,
    SmpmUlDeviceEnergy16bJournalType.RECOVERY_BATTERY_WORKING_VOLTAGE: IntegrationV0MessageEvent.RECOVERY_BATTERY_WORKING_VOLTAGE,
    SmpmUlDeviceEnergy16bJournalType.LOW_CONSUMPTION: IntegrationV0MessageEvent.LOW_CONSUMPTION,
    SmpmUlDeviceEnergy16bJournalType.RESET_FLAG_LOW_CONSUMPTION: IntegrationV0MessageEvent.RESET_FLAG_LOW_CONSUMPTION,
    SmpmUlDeviceEnergy16bJournalType.CHANGE_VALIDATION_SETTINGS: IntegrationV0MessageEvent.CHANGE_VALIDATION_SETTINGS,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEASUREMENT_BLOCK: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEASUREMENT_BLOCK,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_CALCULATION_BLOCK: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_CALCULATION_BLOCK,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_POWER_BLOCK: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_POWER_BLOCK,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_SCREEN: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_SCREEN,
    SmpmUlDeviceEnergy16bJournalType.UNSUCCESSFUL_AUTO_DIAGNOSTIC_RADIO: IntegrationV0MessageEvent.UNSUCCESSFUL_AUTO_DIAGNOSTIC_RADIO,
    SmpmUlDeviceEnergy16bJournalType.MAINS_VOLTAGE_LOST_PHASE_A_START: IntegrationV0MessageEvent.MAINS_VOLTAGE_LOST_PHASE_A_START,
    SmpmUlDeviceEnergy16bJournalType.MAINS_VOLTAGE_LOST_PHASE_A_STOP: IntegrationV0MessageEvent.MAINS_VOLTAGE_LOST_PHASE_A_STOP,
    SmpmUlDeviceEnergy16bJournalType.MAINS_VOLTAGE_LOST_PHASE_B_START: IntegrationV0MessageEvent.MAINS_VOLTAGE_LOST_PHASE_B_START,
    SmpmUlDeviceEnergy16bJournalType.MAINS_VOLTAGE_LOST_PHASE_B_STOP: IntegrationV0MessageEvent.MAINS_VOLTAGE_LOST_PHASE_B_STOP,
    SmpmUlDeviceEnergy16bJournalType.MAINS_VOLTAGE_LOST_PHASE_C_START: IntegrationV0MessageEvent.MAINS_VOLTAGE_LOST_PHASE_C_START,
    SmpmUlDeviceEnergy16bJournalType.MAINS_VOLTAGE_LOST_PHASE_C_STOP: IntegrationV0MessageEvent.MAINS_VOLTAGE_LOST_PHASE_C_STOP,
    SmpmUlDeviceEnergy16bJournalType.VOLTAGE_LAYDOWN_PHASE_A_START: IntegrationV0MessageEvent.VOLTAGE_LAYDOWN_PHASE_A_START,
    SmpmUlDeviceEnergy16bJournalType.VOLTAGE_LAYDOWN_PHASE_A_STOP: IntegrationV0MessageEvent.VOLTAGE_LAYDOWN_PHASE_A_STOP,
    SmpmUlDeviceEnergy16bJournalType.VOLTAGE_LAYDOWN_PHASE_B_START: IntegrationV0MessageEvent.VOLTAGE_LAYDOWN_PHASE_B_START,
    SmpmUlDeviceEnergy16bJournalType.VOLTAGE_LAYDOWN_PHASE_B_STOP: IntegrationV0MessageEvent.VOLTAGE_LAYDOWN_PHASE_B_STOP,
    SmpmUlDeviceEnergy16bJournalType.VOLTAGE_LAYDOWN_PHASE_C_START: IntegrationV0MessageEvent.VOLTAGE_LAYDOWN_PHASE_C_START,
    SmpmUlDeviceEnergy16bJournalType.VOLTAGE_LAYDOWN_PHASE_C_STOP: IntegrationV0MessageEvent.VOLTAGE_LAYDOWN_PHASE_C_STOP,
    SmpmUlDeviceEnergy16bJournalType.OVERVOLTAGE_PHASE_A_START: IntegrationV0MessageEvent.OVERVOLTAGE_PHASE_A_START,
    SmpmUlDeviceEnergy16bJournalType.OVERVOLTAGE_PHASE_A_STOP: IntegrationV0MessageEvent.OVERVOLTAGE_PHASE_A_STOP,
    SmpmUlDeviceEnergy16bJournalType.OVERVOLTAGE_PHASE_B_START: IntegrationV0MessageEvent.OVERVOLTAGE_PHASE_B_START,
    SmpmUlDeviceEnergy16bJournalType.OVERVOLTAGE_PHASE_B_STOP: IntegrationV0MessageEvent.OVERVOLTAGE_PHASE_B_STOP,
    SmpmUlDeviceEnergy16bJournalType.OVERVOLTAGE_PHASE_C_START: IntegrationV0MessageEvent.OVERVOLTAGE_PHASE_C_START,
    SmpmUlDeviceEnergy16bJournalType.OVERVOLTAGE_PHASE_C_STOP: IntegrationV0MessageEvent.OVERVOLTAGE_PHASE_C_STOP,
    SmpmUlDeviceEnergy16bJournalType.OVERCURRENT_PHASE_A_START: IntegrationV0MessageEvent.OVERCURRENT_PHASE_A_START,
    SmpmUlDeviceEnergy16bJournalType.OVERCURRENT_PHASE_A_STOP: IntegrationV0MessageEvent.OVERCURRENT_PHASE_A_STOP,
    SmpmUlDeviceEnergy16bJournalType.OVERCURRENT_PHASE_B_START: IntegrationV0MessageEvent.OVERCURRENT_PHASE_B_START,
    SmpmUlDeviceEnergy16bJournalType.OVERCURRENT_PHASE_B_STOP: IntegrationV0MessageEvent.OVERCURRENT_PHASE_B_STOP,
    SmpmUlDeviceEnergy16bJournalType.OVERCURRENT_PHASE_C_START: IntegrationV0MessageEvent.OVERCURRENT_PHASE_C_START,
    SmpmUlDeviceEnergy16bJournalType.OVERCURRENT_PHASE_C_STOP: IntegrationV0MessageEvent.OVERCURRENT_PHASE_C_STOP,
    SmpmUlDeviceEnergy16bJournalType.CURRENT_SUM_THRESHOLD_LOW_START: IntegrationV0MessageEvent.CURRENT_SUM_THRESHOLD_LOW_START,
    SmpmUlDeviceEnergy16bJournalType.CURRENT_SUM_THRESHOLD_LOW_STOP: IntegrationV0MessageEvent.CURRENT_SUM_THRESHOLD_LOW_STOP,
    SmpmUlDeviceEnergy16bJournalType.FREQ_OUT_PHASE_A_START: IntegrationV0MessageEvent.FREQ_OUT_PHASE_A_START,
    SmpmUlDeviceEnergy16bJournalType.FREQ_OUT_PHASE_A_STOP: IntegrationV0MessageEvent.FREQ_OUT_PHASE_A_STOP,
    SmpmUlDeviceEnergy16bJournalType.FREQ_OUT_PHASE_B_START: IntegrationV0MessageEvent.FREQ_OUT_PHASE_B_START,
    SmpmUlDeviceEnergy16bJournalType.FREQ_OUT_PHASE_B_STOP: IntegrationV0MessageEvent.FREQ_OUT_PHASE_B_STOP,
    SmpmUlDeviceEnergy16bJournalType.FREQ_OUT_PHASE_C_START: IntegrationV0MessageEvent.FREQ_OUT_PHASE_C_START,
    SmpmUlDeviceEnergy16bJournalType.FREQ_OUT_PHASE_C_STOP: IntegrationV0MessageEvent.FREQ_OUT_PHASE_C_STOP,
    SmpmUlDeviceEnergy16bJournalType.PHASE_ORDER_DISTURBANCE_START: IntegrationV0MessageEvent.PHASE_ORDER_DISTURBANCE_START,
    SmpmUlDeviceEnergy16bJournalType.PHASE_ORDER_DISTURBANCE_STOP: IntegrationV0MessageEvent.PHASE_ORDER_DISTURBANCE_STOP,
    SmpmUlDeviceEnergy16bJournalType.RADIO_IMPACT_START: IntegrationV0MessageEvent.RADIO_IMPACT_START,
    SmpmUlDeviceEnergy16bJournalType.RADIO_IMPACT_STOP: IntegrationV0MessageEvent.RADIO_IMPACT_STOP,
    SmpmUlDeviceEnergy16bJournalType.DAYLIGHT_TIME_SWITCH: IntegrationV0MessageEvent.DAYLIGHT_TIME_SWITCH,
    SmpmUlDeviceEnergy16bJournalType.DAYLIGHT_TIME_MODE_DATES_CHANGE: IntegrationV0MessageEvent.DAYLIGHT_TIME_MODE_DATES_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.INTERNAL_CLOCK_SYNC: IntegrationV0MessageEvent.INTERNAL_CLOCK_SYNC,
    SmpmUlDeviceEnergy16bJournalType.METROLOGY_CHANGE: IntegrationV0MessageEvent.METROLOGY_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.PROFILE_CONF_CHANGE: IntegrationV0MessageEvent.PROFILE_CONF_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.TARIFFICATION_METHOD_CHANGE: IntegrationV0MessageEvent.TARIFFICATION_METHOD_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.PERMISSION_CHANGE_SETTINGS_POWER_CONTROL: IntegrationV0MessageEvent.PERMISSION_CHANGE_SETTINGS_POWER_CONTROL,
    SmpmUlDeviceEnergy16bJournalType.CONTROL_LEVEL_MAINS_CHANGE: IntegrationV0MessageEvent.CONTROL_LEVEL_MAINS_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.PERMISSION_CHANGE_SETTINGS_CONSUMPTION_CONTROL: IntegrationV0MessageEvent.PERMISSION_CHANGE_SETTINGS_CONSUMPTION_CONTROL,
    SmpmUlDeviceEnergy16bJournalType.LOAD_RELAY_CONDITION_SETTINGS_CHANGE: IntegrationV0MessageEvent.LOAD_RELAY_CONDITION_SETTINGS_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.SIGNALIZATION_RELAY_CONDITION_SETTINGS_CHANGE: IntegrationV0MessageEvent.SIGNALIZATION_RELAY_CONDITION_SETTINGS_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.INTERFACE_SIGNALIZATION_CONDITION_SETTINGS_CHANGE: IntegrationV0MessageEvent.INTERFACE_SIGNALIZATION_CONDITION_SETTINGS_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.INDICATION_SETTINGS_CHANGE: IntegrationV0MessageEvent.INDICATION_SETTINGS_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.SOUND_SIGNAL_CONDITION_SETTINGS_CHANGE: IntegrationV0MessageEvent.SOUND_SIGNAL_CONDITION_SETTINGS_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.LOAD_RELAY_STATE_CHANGE: IntegrationV0MessageEvent.LOAD_RELAY_STATE_CHANGE,
    SmpmUlDeviceEnergy16bJournalType.SIGNALIZATION_RELAY_STATE_CHANGE: IntegrationV0MessageEvent.SIGNALIZATION_RELAY_STATE_CHANGE,
}
assert len(set(SmpmUlDeviceEnergy16bJournalType)) == len(set(EVENTS_MAP.keys())), "Wrong length of events codes"


class EventData(NamedTuple):
    offset: timedelta
    code: SmpmUlDeviceEnergy16bJournalType


class SmpmUlDeviceEnergy16BJournalData(Packet):
    days_ago: timedelta
    valid: bool
    time_offset: timedelta
    journal: Tuple[EventData, EventData, EventData, EventData, EventData, EventData, EventData, EventData]

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((115) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 127
        result |= ((days_ago_tmp1) & (2 ** (7) - 1)) << size
        size += 7
        assert isinstance(data.valid, bool)
        result |= ((int(data.valid)) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.time_offset, (int, timedelta))
        time_offset_tmp2 = int(data.time_offset.total_seconds() // 1200 if isinstance(data.time_offset, timedelta) else data.time_offset // 1200)
        assert 0 <= time_offset_tmp2 <= 63
        result |= ((time_offset_tmp2) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.journal, tuple) and len(data.journal) == 8
        isinstance(data.journal[0].offset, (int, timedelta))
        offset_tmp3 = int(data.journal[0].offset.total_seconds() // 60 if isinstance(data.journal[0].offset, timedelta) else data.journal[0].offset // 60)
        assert 0 <= offset_tmp3 <= 31
        result |= ((offset_tmp3) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[0].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[0].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[1].offset, (int, timedelta))
        offset_tmp4 = int(data.journal[1].offset.total_seconds() // 60 if isinstance(data.journal[1].offset, timedelta) else data.journal[1].offset // 60)
        assert 0 <= offset_tmp4 <= 31
        result |= ((offset_tmp4) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[1].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[1].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[2].offset, (int, timedelta))
        offset_tmp5 = int(data.journal[2].offset.total_seconds() // 60 if isinstance(data.journal[2].offset, timedelta) else data.journal[2].offset // 60)
        assert 0 <= offset_tmp5 <= 31
        result |= ((offset_tmp5) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[2].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[2].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[3].offset, (int, timedelta))
        offset_tmp6 = int(data.journal[3].offset.total_seconds() // 60 if isinstance(data.journal[3].offset, timedelta) else data.journal[3].offset // 60)
        assert 0 <= offset_tmp6 <= 31
        result |= ((offset_tmp6) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[3].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[3].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[4].offset, (int, timedelta))
        offset_tmp7 = int(data.journal[4].offset.total_seconds() // 60 if isinstance(data.journal[4].offset, timedelta) else data.journal[4].offset // 60)
        assert 0 <= offset_tmp7 <= 31
        result |= ((offset_tmp7) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[4].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[4].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[5].offset, (int, timedelta))
        offset_tmp8 = int(data.journal[5].offset.total_seconds() // 60 if isinstance(data.journal[5].offset, timedelta) else data.journal[5].offset // 60)
        assert 0 <= offset_tmp8 <= 31
        result |= ((offset_tmp8) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[5].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[5].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[6].offset, (int, timedelta))
        offset_tmp9 = int(data.journal[6].offset.total_seconds() // 60 if isinstance(data.journal[6].offset, timedelta) else data.journal[6].offset // 60)
        assert 0 <= offset_tmp9 <= 31
        result |= ((offset_tmp9) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[6].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[6].code.value) & (2 ** (8) - 1)) << size
        size += 8
        isinstance(data.journal[7].offset, (int, timedelta))
        offset_tmp10 = int(data.journal[7].offset.total_seconds() // 60 if isinstance(data.journal[7].offset, timedelta) else data.journal[7].offset // 60)
        assert 0 <= offset_tmp10 <= 31
        result |= ((offset_tmp10) & (2 ** (5) - 1)) << size
        size += 5
        assert isinstance(data.journal[7].code, SmpmUlDeviceEnergy16bJournalType)
        result |= ((data.journal[7].code.value) & (2 ** (8) - 1)) << size
        size += 8
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BJournalData':
        result__el_tmp11: Dict[str, Any] = dict()
        if 115 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp11["days_ago"] = timedelta(seconds=buf.shift(7) * 86400)
        result__el_tmp11["valid"] = bool(buf.shift(1))
        result__el_tmp11["time_offset"] = timedelta(seconds=buf.shift(6) * 1200)
        journal_tmp12: List[EventData] = []
        journal__item_tmp13__el_tmp14: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp14["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp14["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp14)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp15: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp15["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp15["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp15)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp16: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp16["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp16["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp16)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp17: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp17["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp17["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp17)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp18: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp18["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp18["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp18)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp19: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp19["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp19["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp19)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp20: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp20["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp20["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp20)
        journal_tmp12.append(journal__item_tmp13)
        journal__item_tmp13__el_tmp21: Dict[str, Any] = dict()
        journal__item_tmp13__el_tmp21["offset"] = timedelta(seconds=buf.shift(5) * 60)
        journal__item_tmp13__el_tmp21["code"] = SmpmUlDeviceEnergy16bJournalType(buf.shift(8))
        journal__item_tmp13 = EventData(**journal__item_tmp13__el_tmp21)
        journal_tmp12.append(journal__item_tmp13)
        result__el_tmp11["journal"] = tuple(journal_tmp12)
        result = SmpmUlDeviceEnergy16BJournalData(**result__el_tmp11)
        buf.shift(2)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        date = days_ago_calculation(received_at, device_tz, received_at.time(), self.days_ago)
        dt = datetime.combine(date.date(), (date + self.time_offset).time()) if self.days_ago.total_seconds() else datetime.combine(received_at.date(), time(hour=0, minute=0, second=0))   # noqa: E501
        integration_messages = []
        for event in self.journal:
            if event.code is SmpmUlDeviceEnergy16bJournalType.NONE:
                continue
            integration_messages.append(IntegrationV0MessageData(
                is_valid=self.valid,
                dt=dt + event.offset,
                events=[EVENTS_MAP[event.code]],
            ))
        return integration_messages
