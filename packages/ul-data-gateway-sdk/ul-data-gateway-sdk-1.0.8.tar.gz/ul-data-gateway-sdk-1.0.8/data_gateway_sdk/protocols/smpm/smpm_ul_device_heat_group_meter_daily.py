from datetime import timedelta, datetime, tzinfo, time
from typing import Any, List, Dict
from decimal import Decimal

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent, JournalDataType, SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, ResourceType, CounterType, IntegrationV0MessageConsumption, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet


# PACKET (384 bits)   smpm_ul_device_heat_group_meter_daily
#
# RESULT int:        36796229577608994159379990843197031097932211333
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000110 01110010 00000000 00000000 00000000 00000110 01110010 00000000 00000000 00000000 00000110 01110010 00000000 00000000 00000000 00000110 01110010 00000000 01100100 10000101   LSB              # noqa: E501
# RESULT hex:  LE    85 64 00 72 06 00 00 00 72 06 00 00 00 72 06 00 00 00 72 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#
# name                                                type       size  value(int)                                                                                                                                                                                                                                                                                                                                                                                        data(bits)     # noqa: E501
# --------------------------------------------------  ---------  ----  ----------  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------     # noqa: E501
# packet_type_id.0.VAL                                u7            7           5                                                                                                                                                                                                                                                                                                                                                                                           0000101     # noqa: E501
# packet_type_id.0.DFF                                bool          1           1                                                                                                                                                                                                                                                                                                                                                                                          1            # noqa: E501
# packet_type_id.1.VAL                                u2            2           0                                                                                                                                                                                                                                                                                                                                                                                        00             # noqa: E501
# packet_type_id.1.DFF                                bool          1           1                                                                                                                                                                                                                                                                                                                                                                                       1               # noqa: E501
# packet_type_id.2.VAL                                u2            2           0                                                                                                                                                                                                                                                                                                                                                                                     00                # noqa: E501
# packet_type_id.2.DFF                                bool          1           1                                                                                                                                                                                                                                                                                                                                                                                    1                  # noqa: E501
# packet_type_id.3.VAL                                u2            2           1                                                                                                                                                                                                                                                                                                                                                                                  01                   # noqa: E501
# packet_type_id.3.DFF                                bool          1           0                                                                                                                                                                                                                                                                                                                                                                                 0                     # noqa: E501
# days_ago                                            timedelta     6           0                                                                                                                                                                                                                                                                                                                                                                           000000                      # noqa: E501
# value_ch1                                           uf40p3       40        3300                                                                                                                                                                                                                                                                                                                                   0000000000000000000000000000110011100100                            # noqa: E501
# value_ch2                                           uf40p3       40        3300                                                                                                                                                                                                                                                                                           0000000000000000000000000000110011100100                                                                    # noqa: E501
# value_ch3                                           uf40p3       40        3300                                                                                                                                                                                                                                                   0000000000000000000000000000110011100100                                                                                                            # noqa: E501
# value_ch4                                           uf40p3       40        3300                                                                                                                                                                                                           0000000000000000000000000000110011100100                                                                                                                                                    # noqa: E501
# uptime_ch1                                          timedelta    22           0                                                                                                                                                                                     0000000000000000000000                                                                                                                                                                                            # noqa: E501
# uptime_ch2                                          timedelta    22           0                                                                                                                                                               0000000000000000000000                                                                                                                                                                                                                  # noqa: E501
# uptime_ch3                                          timedelta    22           0                                                                                                                                         0000000000000000000000                                                                                                                                                                                                                                        # noqa: E501
# uptime_ch4                                          timedelta    22           0                                                                                                                   0000000000000000000000                                                                                                                                                                                                                                                              # noqa: E501
# event_device_power_supply_lost                      bool          1           0                                                                                                                  0                                                                                                                                                                                                                                                                                    # noqa: E501
# event_device_power_supply_enabled                   bool          1           0                                                                                                                 0                                                                                                                                                                                                                                                                                     # noqa: E501
# event_device_common_settings_changed                bool          1           0                                                                                                                0                                                                                                                                                                                                                                                                                      # noqa: E501
# event_device_measure_channels_settings_changed      bool          1           0                                                                                                               0                                                                                                                                                                                                                                                                                       # noqa: E501
# event_device_digital_i_o_settings_changed           bool          1           0                                                                                                              0                                                                                                                                                                                                                                                                                        # noqa: E501
# event_device_datetime_changed                       bool          1           0                                                                                                             0                                                                                                                                                                                                                                                                                         # noqa: E501
# event_device_ethernet_settings_changed              bool          1           0                                                                                                            0                                                                                                                                                                                                                                                                                          # noqa: E501
# event_device_system_settings_changed1               bool          1           0                                                                                                           0                                                                                                                                                                                                                                                                                           # noqa: E501
# event_device_system_settings_changed2               bool          1           0                                                                                                          0                                                                                                                                                                                                                                                                                            # noqa: E501
# event_device_system_settings_changed3               bool          1           0                                                                                                         0                                                                                                                                                                                                                                                                                             # noqa: E501
# event_device_system_settings_changed4               bool          1           0                                                                                                        0                                                                                                                                                                                                                                                                                              # noqa: E501
# event_device_alarm_digital_input1                   bool          1           0                                                                                                       0                                                                                                                                                                                                                                                                                               # noqa: E501
# event_device_alarm_overrate_digital_input1          bool          1           0                                                                                                      0                                                                                                                                                                                                                                                                                                # noqa: E501
# event_device_alarm_overrate_digital_input2          bool          1           0                                                                                                     0                                                                                                                                                                                                                                                                                                 # noqa: E501
# event_device_alarm_underrate_digital_input1         bool          1           0                                                                                                    0                                                                                                                                                                                                                                                                                                  # noqa: E501
# event_device_alarm_underrate_digital_input2         bool          1           0                                                                                                   0                                                                                                                                                                                                                                                                                                   # noqa: E501
# event_device_alarm_t_high_digital_input1            bool          1           0                                                                                                  0
# event_device_alarm_t_high_digital_input2            bool          1           0                                                                                                 0
# event_device_alarm_t_low_digital_input1             bool          1           0                                                                                                0
# event_device_alarm_t_low_digital_input2             bool          1           0                                                                                               0
# event_device_alarm_delta_t_high_digital_input1      bool          1           0                                                                                              0
# event_device_alarm_delta_t_high_digital_input2      bool          1           0                                                                                             0
# event_device_alarm_delta_t_low_digital_input1       bool          1           0                                                                                            0
# event_device_alarm_delta_t_low_digital_input2       bool          1           0                                                                                           0
# event_device_alarm_power_high_digital_input1        bool          1           0                                                                                          0
# event_device_alarm_power_high_digital_input2        bool          1           0                                                                                         0
# event_device_alarm_power_low_digital_input1         bool          1           0                                                                                        0
# event_device_alarm_power_low_digital_input2         bool          1           0                                                                                       0
# event_ch1_circuit_break_t_sensor_1                  bool          1           0                                                                                      0
# event_ch1_circuit_break_t_sensor_2                  bool          1           0                                                                                     0
# event_ch1_circuit_break_t_sensor_3                  bool          1           0                                                                                    0
# event_ch1_error_delta_t                             bool          1           0                                                                                   0
# event_ch1_consumption_lower_g_min_channel_rate_1    bool          1           0                                                                                  0
# event_ch1_consumption_lower_g_min_channel_rate_2    bool          1           0                                                                                 0
# event_ch1_consumption_lower_g_min_channel_rate_3    bool          1           0                                                                                0
# event_ch1_consumption_lower_g_max_channel_rate_1    bool          1           0                                                                               0
# event_ch1_consumption_lower_g_max_channel_rate_2    bool          1           0                                                                              0
# event_ch1_consumption_lower_g_max_channel_rate_3    bool          1           0                                                                             0
# event_ch1_no_coolant_channel_rate_1                 bool          1           0                                                                            0
# event_ch1_no_coolant_channel_rate_2                 bool          1           0                                                                           0
# event_ch1_no_coolant_channel_rate_3                 bool          1           0                                                                          0
# event_ch1_circuit_break_stimulation_channel_rate_1  bool          1           0                                                                         0
# event_ch1_circuit_break_stimulation_channel_rate_2  bool          1           0                                                                        0
# event_ch1_circuit_break_pressure_sensor_1           bool          1           0                                                                       0
# event_ch1_circuit_break_pressure_sensor_2           bool          1           0                                                                      0
# event_ch1_circuit_break_pressure_sensor_3           bool          1           0                                                                     0
# event_ch1_reverse                                   bool          1           0                                                                    0
# event_ch2_circuit_break_t_sensor_1                  bool          1           0                                                                   0
# event_ch2_circuit_break_t_sensor_2                  bool          1           0                                                                  0
# event_ch2_circuit_break_t_sensor_3                  bool          1           0                                                                 0
# event_ch2_error_delta_t                             bool          1           0                                                                0
# event_ch2_consumption_lower_g_min_channel_rate_1    bool          1           0                                                               0
# event_ch2_consumption_lower_g_min_channel_rate_2    bool          1           0                                                              0
# event_ch2_consumption_lower_g_min_channel_rate_3    bool          1           0                                                             0
# event_ch2_consumption_lower_g_max_channel_rate_1    bool          1           0                                                            0
# event_ch2_consumption_lower_g_max_channel_rate_2    bool          1           0                                                           0
# event_ch2_consumption_lower_g_max_channel_rate_3    bool          1           0                                                          0
# event_ch2_no_coolant_channel_rate_1                 bool          1           0                                                         0
# event_ch2_no_coolant_channel_rate_2                 bool          1           0                                                        0
# event_ch2_no_coolant_channel_rate_3                 bool          1           0                                                       0
# event_ch2_circuit_break_stimulation_channel_rate_1  bool          1           0                                                      0
# event_ch2_circuit_break_stimulation_channel_rate_2  bool          1           0                                                     0
# event_ch2_circuit_break_pressure_sensor_1           bool          1           0                                                    0
# event_ch2_circuit_break_pressure_sensor_2           bool          1           0                                                   0
# event_ch2_circuit_break_pressure_sensor_3           bool          1           0                                                  0
# event_ch2_reverse                                   bool          1           0                                                 0
# event_ch3_circuit_break_t_sensor_1                  bool          1           0                                                0
# event_ch3_circuit_break_t_sensor_2                  bool          1           0                                               0
# event_ch3_circuit_break_t_sensor_3                  bool          1           0                                              0
# event_ch3_error_delta_t                             bool          1           0                                             0
# event_ch3_consumption_lower_g_min_channel_rate_1    bool          1           0                                            0
# event_ch3_consumption_lower_g_min_channel_rate_2    bool          1           0                                           0
# event_ch3_consumption_lower_g_min_channel_rate_3    bool          1           0                                          0
# event_ch3_consumption_lower_g_max_channel_rate_1    bool          1           0                                         0
# event_ch3_consumption_lower_g_max_channel_rate_2    bool          1           0                                        0
# event_ch3_consumption_lower_g_max_channel_rate_3    bool          1           0                                       0
# event_ch3_no_coolant_channel_rate_1                 bool          1           0                                      0
# event_ch3_no_coolant_channel_rate_2                 bool          1           0                                     0
# event_ch3_no_coolant_channel_rate_3                 bool          1           0                                    0
# event_ch3_circuit_break_stimulation_channel_rate_1  bool          1           0                                   0
# event_ch3_circuit_break_stimulation_channel_rate_2  bool          1           0                                  0
# event_ch3_circuit_break_pressure_sensor_1           bool          1           0                                 0
# event_ch3_circuit_break_pressure_sensor_2           bool          1           0                                0
# event_ch3_circuit_break_pressure_sensor_3           bool          1           0                               0
# event_ch3_reverse                                   bool          1           0                              0
# event_ch4_circuit_break_t_sensor_1                  bool          1           0                             0
# event_ch4_circuit_break_t_sensor_2                  bool          1           0                            0
# event_ch4_circuit_break_t_sensor_3                  bool          1           0                           0
# event_ch4_error_delta_t                             bool          1           0                          0
# event_ch4_consumption_lower_g_min_channel_rate_1    bool          1           0                         0
# event_ch4_consumption_lower_g_min_channel_rate_2    bool          1           0                        0
# event_ch4_consumption_lower_g_min_channel_rate_3    bool          1           0                       0
# event_ch4_consumption_lower_g_max_channel_rate_1    bool          1           0                      0
# event_ch4_consumption_lower_g_max_channel_rate_2    bool          1           0                     0
# event_ch4_consumption_lower_g_max_channel_rate_3    bool          1           0                    0
# event_ch4_no_coolant_channel_rate_1                 bool          1           0                   0
# event_ch4_no_coolant_channel_rate_2                 bool          1           0                  0
# event_ch4_no_coolant_channel_rate_3                 bool          1           0                 0
# event_ch4_circuit_break_stimulation_channel_rate_1  bool          1           0                0
# event_ch4_circuit_break_stimulation_channel_rate_2  bool          1           0               0
# event_ch4_circuit_break_pressure_sensor_1           bool          1           0              0
# event_ch4_circuit_break_pressure_sensor_2           bool          1           0             0
# event_ch4_circuit_break_pressure_sensor_3           bool          1           0            0
# event_ch4_reverse                                   bool          1           0           0
# RESERVED                                            u9            9           0  000000000


class SmpmUlDeviceHeatGroupMeterDailyData(Packet):
    days_ago: timedelta
    value_ch1: float
    value_ch2: float
    value_ch3: float
    value_ch4: float
    uptime_ch1: timedelta
    uptime_ch2: timedelta
    uptime_ch3: timedelta
    uptime_ch4: timedelta
    event_device_power_supply_lost: bool
    event_device_power_supply_enabled: bool
    event_device_common_settings_changed: bool
    event_device_measure_channels_settings_changed: bool
    event_device_digital_i_o_settings_changed: bool
    event_device_datetime_changed: bool
    event_device_ethernet_settings_changed: bool
    event_device_system_settings_changed1: bool
    event_device_system_settings_changed2: bool
    event_device_system_settings_changed3: bool
    event_device_system_settings_changed4: bool
    event_device_alarm_digital_input1: bool
    event_device_alarm_overrate_digital_input1: bool
    event_device_alarm_overrate_digital_input2: bool
    event_device_alarm_underrate_digital_input1: bool
    event_device_alarm_underrate_digital_input2: bool
    event_device_alarm_t_high_digital_input1: bool
    event_device_alarm_t_high_digital_input2: bool
    event_device_alarm_t_low_digital_input1: bool
    event_device_alarm_t_low_digital_input2: bool
    event_device_alarm_delta_t_high_digital_input1: bool
    event_device_alarm_delta_t_high_digital_input2: bool
    event_device_alarm_delta_t_low_digital_input1: bool
    event_device_alarm_delta_t_low_digital_input2: bool
    event_device_alarm_power_high_digital_input1: bool
    event_device_alarm_power_high_digital_input2: bool
    event_device_alarm_power_low_digital_input1: bool
    event_device_alarm_power_low_digital_input2: bool
    event_ch1_circuit_break_t_sensor_1: bool
    event_ch1_circuit_break_t_sensor_2: bool
    event_ch1_circuit_break_t_sensor_3: bool
    event_ch1_error_delta_t: bool
    event_ch1_consumption_lower_g_min_channel_rate_1: bool
    event_ch1_consumption_lower_g_min_channel_rate_2: bool
    event_ch1_consumption_lower_g_min_channel_rate_3: bool
    event_ch1_consumption_lower_g_max_channel_rate_1: bool
    event_ch1_consumption_lower_g_max_channel_rate_2: bool
    event_ch1_consumption_lower_g_max_channel_rate_3: bool
    event_ch1_no_coolant_channel_rate_1: bool
    event_ch1_no_coolant_channel_rate_2: bool
    event_ch1_no_coolant_channel_rate_3: bool
    event_ch1_circuit_break_stimulation_channel_rate_1: bool
    event_ch1_circuit_break_stimulation_channel_rate_2: bool
    event_ch1_circuit_break_pressure_sensor_1: bool
    event_ch1_circuit_break_pressure_sensor_2: bool
    event_ch1_circuit_break_pressure_sensor_3: bool
    event_ch1_reverse: bool
    event_ch2_circuit_break_t_sensor_1: bool
    event_ch2_circuit_break_t_sensor_2: bool
    event_ch2_circuit_break_t_sensor_3: bool
    event_ch2_error_delta_t: bool
    event_ch2_consumption_lower_g_min_channel_rate_1: bool
    event_ch2_consumption_lower_g_min_channel_rate_2: bool
    event_ch2_consumption_lower_g_min_channel_rate_3: bool
    event_ch2_consumption_lower_g_max_channel_rate_1: bool
    event_ch2_consumption_lower_g_max_channel_rate_2: bool
    event_ch2_consumption_lower_g_max_channel_rate_3: bool
    event_ch2_no_coolant_channel_rate_1: bool
    event_ch2_no_coolant_channel_rate_2: bool
    event_ch2_no_coolant_channel_rate_3: bool
    event_ch2_circuit_break_stimulation_channel_rate_1: bool
    event_ch2_circuit_break_stimulation_channel_rate_2: bool
    event_ch2_circuit_break_pressure_sensor_1: bool
    event_ch2_circuit_break_pressure_sensor_2: bool
    event_ch2_circuit_break_pressure_sensor_3: bool
    event_ch2_reverse: bool
    event_ch3_circuit_break_t_sensor_1: bool
    event_ch3_circuit_break_t_sensor_2: bool
    event_ch3_circuit_break_t_sensor_3: bool
    event_ch3_error_delta_t: bool
    event_ch3_consumption_lower_g_min_channel_rate_1: bool
    event_ch3_consumption_lower_g_min_channel_rate_2: bool
    event_ch3_consumption_lower_g_min_channel_rate_3: bool
    event_ch3_consumption_lower_g_max_channel_rate_1: bool
    event_ch3_consumption_lower_g_max_channel_rate_2: bool
    event_ch3_consumption_lower_g_max_channel_rate_3: bool
    event_ch3_no_coolant_channel_rate_1: bool
    event_ch3_no_coolant_channel_rate_2: bool
    event_ch3_no_coolant_channel_rate_3: bool
    event_ch3_circuit_break_stimulation_channel_rate_1: bool
    event_ch3_circuit_break_stimulation_channel_rate_2: bool
    event_ch3_circuit_break_pressure_sensor_1: bool
    event_ch3_circuit_break_pressure_sensor_2: bool
    event_ch3_circuit_break_pressure_sensor_3: bool
    event_ch3_reverse: bool
    event_ch4_circuit_break_t_sensor_1: bool
    event_ch4_circuit_break_t_sensor_2: bool
    event_ch4_circuit_break_t_sensor_3: bool
    event_ch4_error_delta_t: bool
    event_ch4_consumption_lower_g_min_channel_rate_1: bool
    event_ch4_consumption_lower_g_min_channel_rate_2: bool
    event_ch4_consumption_lower_g_min_channel_rate_3: bool
    event_ch4_consumption_lower_g_max_channel_rate_1: bool
    event_ch4_consumption_lower_g_max_channel_rate_2: bool
    event_ch4_consumption_lower_g_max_channel_rate_3: bool
    event_ch4_no_coolant_channel_rate_1: bool
    event_ch4_no_coolant_channel_rate_2: bool
    event_ch4_no_coolant_channel_rate_3: bool
    event_ch4_circuit_break_stimulation_channel_rate_1: bool
    event_ch4_circuit_break_stimulation_channel_rate_2: bool
    event_ch4_circuit_break_pressure_sensor_1: bool
    event_ch4_circuit_break_pressure_sensor_2: bool
    event_ch4_circuit_break_pressure_sensor_3: bool
    event_ch4_reverse: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((5) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((1) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp1 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp1 <= 63
        result |= ((days_ago_tmp1) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.value_ch1, (int, float))
        result |= ((int(round(float(data.value_ch1) * 1000.0, 0)) & 1099511627775) & (2 ** (40) - 1)) << size
        size += 40
        assert isinstance(data.value_ch2, (int, float))
        result |= ((int(round(float(data.value_ch2) * 1000.0, 0)) & 1099511627775) & (2 ** (40) - 1)) << size
        size += 40
        assert isinstance(data.value_ch3, (int, float))
        result |= ((int(round(float(data.value_ch3) * 1000.0, 0)) & 1099511627775) & (2 ** (40) - 1)) << size
        size += 40
        assert isinstance(data.value_ch4, (int, float))
        result |= ((int(round(float(data.value_ch4) * 1000.0, 0)) & 1099511627775) & (2 ** (40) - 1)) << size
        size += 40
        isinstance(data.uptime_ch1, (int, timedelta))
        value_int_tmp2 = int(data.uptime_ch1.total_seconds() // 60 if isinstance(data.uptime_ch1, timedelta) else data.uptime_ch1 // 60) & 4194303
        result |= ((value_int_tmp2) & (2 ** (22) - 1)) << size
        size += 22
        isinstance(data.uptime_ch2, (int, timedelta))
        value_int_tmp3 = int(data.uptime_ch2.total_seconds() // 60 if isinstance(data.uptime_ch2, timedelta) else data.uptime_ch2 // 60) & 4194303
        result |= ((value_int_tmp3) & (2 ** (22) - 1)) << size
        size += 22
        isinstance(data.uptime_ch3, (int, timedelta))
        value_int_tmp4 = int(data.uptime_ch3.total_seconds() // 60 if isinstance(data.uptime_ch3, timedelta) else data.uptime_ch3 // 60) & 4194303
        result |= ((value_int_tmp4) & (2 ** (22) - 1)) << size
        size += 22
        isinstance(data.uptime_ch4, (int, timedelta))
        value_int_tmp5 = int(data.uptime_ch4.total_seconds() // 60 if isinstance(data.uptime_ch4, timedelta) else data.uptime_ch4 // 60) & 4194303
        result |= ((value_int_tmp5) & (2 ** (22) - 1)) << size
        size += 22
        assert isinstance(data.event_device_power_supply_lost, bool)
        result |= ((int(data.event_device_power_supply_lost)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_power_supply_enabled, bool)
        result |= ((int(data.event_device_power_supply_enabled)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_common_settings_changed, bool)
        result |= ((int(data.event_device_common_settings_changed)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_measure_channels_settings_changed, bool)
        result |= ((int(data.event_device_measure_channels_settings_changed)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_digital_i_o_settings_changed, bool)
        result |= ((int(data.event_device_digital_i_o_settings_changed)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_datetime_changed, bool)
        result |= ((int(data.event_device_datetime_changed)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_ethernet_settings_changed, bool)
        result |= ((int(data.event_device_ethernet_settings_changed)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_system_settings_changed1, bool)
        result |= ((int(data.event_device_system_settings_changed1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_system_settings_changed2, bool)
        result |= ((int(data.event_device_system_settings_changed2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_system_settings_changed3, bool)
        result |= ((int(data.event_device_system_settings_changed3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_system_settings_changed4, bool)
        result |= ((int(data.event_device_system_settings_changed4)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_digital_input1, bool)
        result |= ((int(data.event_device_alarm_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_overrate_digital_input1, bool)
        result |= ((int(data.event_device_alarm_overrate_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_overrate_digital_input2, bool)
        result |= ((int(data.event_device_alarm_overrate_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_underrate_digital_input1, bool)
        result |= ((int(data.event_device_alarm_underrate_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_underrate_digital_input2, bool)
        result |= ((int(data.event_device_alarm_underrate_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_t_high_digital_input1, bool)
        result |= ((int(data.event_device_alarm_t_high_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_t_high_digital_input2, bool)
        result |= ((int(data.event_device_alarm_t_high_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_t_low_digital_input1, bool)
        result |= ((int(data.event_device_alarm_t_low_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_t_low_digital_input2, bool)
        result |= ((int(data.event_device_alarm_t_low_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_delta_t_high_digital_input1, bool)
        result |= ((int(data.event_device_alarm_delta_t_high_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_delta_t_high_digital_input2, bool)
        result |= ((int(data.event_device_alarm_delta_t_high_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_delta_t_low_digital_input1, bool)
        result |= ((int(data.event_device_alarm_delta_t_low_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_delta_t_low_digital_input2, bool)
        result |= ((int(data.event_device_alarm_delta_t_low_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_power_high_digital_input1, bool)
        result |= ((int(data.event_device_alarm_power_high_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_power_high_digital_input2, bool)
        result |= ((int(data.event_device_alarm_power_high_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_power_low_digital_input1, bool)
        result |= ((int(data.event_device_alarm_power_low_digital_input1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_device_alarm_power_low_digital_input2, bool)
        result |= ((int(data.event_device_alarm_power_low_digital_input2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_t_sensor_1, bool)
        result |= ((int(data.event_ch1_circuit_break_t_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_t_sensor_2, bool)
        result |= ((int(data.event_ch1_circuit_break_t_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_t_sensor_3, bool)
        result |= ((int(data.event_ch1_circuit_break_t_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_error_delta_t, bool)
        result |= ((int(data.event_ch1_error_delta_t)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_consumption_lower_g_min_channel_rate_1, bool)
        result |= ((int(data.event_ch1_consumption_lower_g_min_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_consumption_lower_g_min_channel_rate_2, bool)
        result |= ((int(data.event_ch1_consumption_lower_g_min_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_consumption_lower_g_min_channel_rate_3, bool)
        result |= ((int(data.event_ch1_consumption_lower_g_min_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_consumption_lower_g_max_channel_rate_1, bool)
        result |= ((int(data.event_ch1_consumption_lower_g_max_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_consumption_lower_g_max_channel_rate_2, bool)
        result |= ((int(data.event_ch1_consumption_lower_g_max_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_consumption_lower_g_max_channel_rate_3, bool)
        result |= ((int(data.event_ch1_consumption_lower_g_max_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_no_coolant_channel_rate_1, bool)
        result |= ((int(data.event_ch1_no_coolant_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_no_coolant_channel_rate_2, bool)
        result |= ((int(data.event_ch1_no_coolant_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_no_coolant_channel_rate_3, bool)
        result |= ((int(data.event_ch1_no_coolant_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_stimulation_channel_rate_1, bool)
        result |= ((int(data.event_ch1_circuit_break_stimulation_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_stimulation_channel_rate_2, bool)
        result |= ((int(data.event_ch1_circuit_break_stimulation_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_pressure_sensor_1, bool)
        result |= ((int(data.event_ch1_circuit_break_pressure_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_pressure_sensor_2, bool)
        result |= ((int(data.event_ch1_circuit_break_pressure_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_circuit_break_pressure_sensor_3, bool)
        result |= ((int(data.event_ch1_circuit_break_pressure_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch1_reverse, bool)
        result |= ((int(data.event_ch1_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_t_sensor_1, bool)
        result |= ((int(data.event_ch2_circuit_break_t_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_t_sensor_2, bool)
        result |= ((int(data.event_ch2_circuit_break_t_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_t_sensor_3, bool)
        result |= ((int(data.event_ch2_circuit_break_t_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_error_delta_t, bool)
        result |= ((int(data.event_ch2_error_delta_t)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_consumption_lower_g_min_channel_rate_1, bool)
        result |= ((int(data.event_ch2_consumption_lower_g_min_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_consumption_lower_g_min_channel_rate_2, bool)
        result |= ((int(data.event_ch2_consumption_lower_g_min_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_consumption_lower_g_min_channel_rate_3, bool)
        result |= ((int(data.event_ch2_consumption_lower_g_min_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_consumption_lower_g_max_channel_rate_1, bool)
        result |= ((int(data.event_ch2_consumption_lower_g_max_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_consumption_lower_g_max_channel_rate_2, bool)
        result |= ((int(data.event_ch2_consumption_lower_g_max_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_consumption_lower_g_max_channel_rate_3, bool)
        result |= ((int(data.event_ch2_consumption_lower_g_max_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_no_coolant_channel_rate_1, bool)
        result |= ((int(data.event_ch2_no_coolant_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_no_coolant_channel_rate_2, bool)
        result |= ((int(data.event_ch2_no_coolant_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_no_coolant_channel_rate_3, bool)
        result |= ((int(data.event_ch2_no_coolant_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_stimulation_channel_rate_1, bool)
        result |= ((int(data.event_ch2_circuit_break_stimulation_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_stimulation_channel_rate_2, bool)
        result |= ((int(data.event_ch2_circuit_break_stimulation_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_pressure_sensor_1, bool)
        result |= ((int(data.event_ch2_circuit_break_pressure_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_pressure_sensor_2, bool)
        result |= ((int(data.event_ch2_circuit_break_pressure_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_circuit_break_pressure_sensor_3, bool)
        result |= ((int(data.event_ch2_circuit_break_pressure_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch2_reverse, bool)
        result |= ((int(data.event_ch2_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_t_sensor_1, bool)
        result |= ((int(data.event_ch3_circuit_break_t_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_t_sensor_2, bool)
        result |= ((int(data.event_ch3_circuit_break_t_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_t_sensor_3, bool)
        result |= ((int(data.event_ch3_circuit_break_t_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_error_delta_t, bool)
        result |= ((int(data.event_ch3_error_delta_t)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_consumption_lower_g_min_channel_rate_1, bool)
        result |= ((int(data.event_ch3_consumption_lower_g_min_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_consumption_lower_g_min_channel_rate_2, bool)
        result |= ((int(data.event_ch3_consumption_lower_g_min_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_consumption_lower_g_min_channel_rate_3, bool)
        result |= ((int(data.event_ch3_consumption_lower_g_min_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_consumption_lower_g_max_channel_rate_1, bool)
        result |= ((int(data.event_ch3_consumption_lower_g_max_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_consumption_lower_g_max_channel_rate_2, bool)
        result |= ((int(data.event_ch3_consumption_lower_g_max_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_consumption_lower_g_max_channel_rate_3, bool)
        result |= ((int(data.event_ch3_consumption_lower_g_max_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_no_coolant_channel_rate_1, bool)
        result |= ((int(data.event_ch3_no_coolant_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_no_coolant_channel_rate_2, bool)
        result |= ((int(data.event_ch3_no_coolant_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_no_coolant_channel_rate_3, bool)
        result |= ((int(data.event_ch3_no_coolant_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_stimulation_channel_rate_1, bool)
        result |= ((int(data.event_ch3_circuit_break_stimulation_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_stimulation_channel_rate_2, bool)
        result |= ((int(data.event_ch3_circuit_break_stimulation_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_pressure_sensor_1, bool)
        result |= ((int(data.event_ch3_circuit_break_pressure_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_pressure_sensor_2, bool)
        result |= ((int(data.event_ch3_circuit_break_pressure_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_circuit_break_pressure_sensor_3, bool)
        result |= ((int(data.event_ch3_circuit_break_pressure_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch3_reverse, bool)
        result |= ((int(data.event_ch3_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_t_sensor_1, bool)
        result |= ((int(data.event_ch4_circuit_break_t_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_t_sensor_2, bool)
        result |= ((int(data.event_ch4_circuit_break_t_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_t_sensor_3, bool)
        result |= ((int(data.event_ch4_circuit_break_t_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_error_delta_t, bool)
        result |= ((int(data.event_ch4_error_delta_t)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_consumption_lower_g_min_channel_rate_1, bool)
        result |= ((int(data.event_ch4_consumption_lower_g_min_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_consumption_lower_g_min_channel_rate_2, bool)
        result |= ((int(data.event_ch4_consumption_lower_g_min_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_consumption_lower_g_min_channel_rate_3, bool)
        result |= ((int(data.event_ch4_consumption_lower_g_min_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_consumption_lower_g_max_channel_rate_1, bool)
        result |= ((int(data.event_ch4_consumption_lower_g_max_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_consumption_lower_g_max_channel_rate_2, bool)
        result |= ((int(data.event_ch4_consumption_lower_g_max_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_consumption_lower_g_max_channel_rate_3, bool)
        result |= ((int(data.event_ch4_consumption_lower_g_max_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_no_coolant_channel_rate_1, bool)
        result |= ((int(data.event_ch4_no_coolant_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_no_coolant_channel_rate_2, bool)
        result |= ((int(data.event_ch4_no_coolant_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_no_coolant_channel_rate_3, bool)
        result |= ((int(data.event_ch4_no_coolant_channel_rate_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_stimulation_channel_rate_1, bool)
        result |= ((int(data.event_ch4_circuit_break_stimulation_channel_rate_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_stimulation_channel_rate_2, bool)
        result |= ((int(data.event_ch4_circuit_break_stimulation_channel_rate_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_pressure_sensor_1, bool)
        result |= ((int(data.event_ch4_circuit_break_pressure_sensor_1)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_pressure_sensor_2, bool)
        result |= ((int(data.event_ch4_circuit_break_pressure_sensor_2)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_circuit_break_pressure_sensor_3, bool)
        result |= ((int(data.event_ch4_circuit_break_pressure_sensor_3)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.event_ch4_reverse, bool)
        result |= ((int(data.event_ch4_reverse)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(48, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceHeatGroupMeterDailyData':
        result__el_tmp6: Dict[str, Any] = dict()
        if 5 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp6["days_ago"] = timedelta(seconds=buf.shift(6) * 86400)
        result__el_tmp6["value_ch1"] = round(buf.shift(40) / 1000.0, 3)
        result__el_tmp6["value_ch2"] = round(buf.shift(40) / 1000.0, 3)
        result__el_tmp6["value_ch3"] = round(buf.shift(40) / 1000.0, 3)
        result__el_tmp6["value_ch4"] = round(buf.shift(40) / 1000.0, 3)
        result__el_tmp6["uptime_ch1"] = timedelta(seconds=buf.shift(22) * 60)
        result__el_tmp6["uptime_ch2"] = timedelta(seconds=buf.shift(22) * 60)
        result__el_tmp6["uptime_ch3"] = timedelta(seconds=buf.shift(22) * 60)
        result__el_tmp6["uptime_ch4"] = timedelta(seconds=buf.shift(22) * 60)
        result__el_tmp6["event_device_power_supply_lost"] = bool(buf.shift(1))
        result__el_tmp6["event_device_power_supply_enabled"] = bool(buf.shift(1))
        result__el_tmp6["event_device_common_settings_changed"] = bool(buf.shift(1))
        result__el_tmp6["event_device_measure_channels_settings_changed"] = bool(buf.shift(1))
        result__el_tmp6["event_device_digital_i_o_settings_changed"] = bool(buf.shift(1))
        result__el_tmp6["event_device_datetime_changed"] = bool(buf.shift(1))
        result__el_tmp6["event_device_ethernet_settings_changed"] = bool(buf.shift(1))
        result__el_tmp6["event_device_system_settings_changed1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_system_settings_changed2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_system_settings_changed3"] = bool(buf.shift(1))
        result__el_tmp6["event_device_system_settings_changed4"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_overrate_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_overrate_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_underrate_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_underrate_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_t_high_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_t_high_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_t_low_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_t_low_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_delta_t_high_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_delta_t_high_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_delta_t_low_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_delta_t_low_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_power_high_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_power_high_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_power_low_digital_input1"] = bool(buf.shift(1))
        result__el_tmp6["event_device_alarm_power_low_digital_input2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_t_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_t_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_t_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_error_delta_t"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_consumption_lower_g_min_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_consumption_lower_g_min_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_consumption_lower_g_min_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_consumption_lower_g_max_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_consumption_lower_g_max_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_consumption_lower_g_max_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_no_coolant_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_no_coolant_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_no_coolant_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_stimulation_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_stimulation_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_pressure_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_pressure_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_circuit_break_pressure_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch1_reverse"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_t_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_t_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_t_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_error_delta_t"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_consumption_lower_g_min_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_consumption_lower_g_min_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_consumption_lower_g_min_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_consumption_lower_g_max_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_consumption_lower_g_max_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_consumption_lower_g_max_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_no_coolant_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_no_coolant_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_no_coolant_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_stimulation_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_stimulation_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_pressure_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_pressure_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_circuit_break_pressure_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch2_reverse"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_t_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_t_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_t_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_error_delta_t"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_consumption_lower_g_min_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_consumption_lower_g_min_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_consumption_lower_g_min_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_consumption_lower_g_max_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_consumption_lower_g_max_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_consumption_lower_g_max_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_no_coolant_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_no_coolant_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_no_coolant_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_stimulation_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_stimulation_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_pressure_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_pressure_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_circuit_break_pressure_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch3_reverse"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_t_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_t_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_t_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_error_delta_t"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_consumption_lower_g_min_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_consumption_lower_g_min_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_consumption_lower_g_min_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_consumption_lower_g_max_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_consumption_lower_g_max_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_consumption_lower_g_max_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_no_coolant_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_no_coolant_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_no_coolant_channel_rate_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_stimulation_channel_rate_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_stimulation_channel_rate_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_pressure_sensor_1"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_pressure_sensor_2"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_circuit_break_pressure_sensor_3"] = bool(buf.shift(1))
        result__el_tmp6["event_ch4_reverse"] = bool(buf.shift(1))
        result = SmpmUlDeviceHeatGroupMeterDailyData(**result__el_tmp6)
        buf.shift(9)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        overloading_value = Decimal(str(134217.727))
        return [
            IntegrationV0MessageData(
                dt=days_ago_calculation(received_at, device_tz, time(0), self.days_ago),
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(self.value_ch1)),
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        overloading_value=overloading_value,
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(self.value_ch2)),
                        resource_type=ResourceType.COMMON,
                        channel=2,
                        overloading_value=overloading_value,
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(self.value_ch3)),
                        resource_type=ResourceType.COMMON,
                        channel=3,
                        overloading_value=overloading_value,
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        value=Decimal(str(self.value_ch4)),
                        resource_type=ResourceType.COMMON,
                        channel=4,
                        overloading_value=overloading_value,
                        journal_data_type=JournalDataType.END_OF_DAY if self.days_ago else JournalDataType.CURRENT,
                    ),
                ],
                events=[
                    *([IntegrationV0MessageEvent.DEVICE__POWER_SUPPLY_LOST] if self.event_device_power_supply_lost else []),
                    *([IntegrationV0MessageEvent.DEVICE__POWER_SUPPLY_ENABLED] if self.event_device_power_supply_enabled else []),
                    *([IntegrationV0MessageEvent.DEVICE__COMMON_SETTINGS_CHANGED] if self.event_device_common_settings_changed else []),
                    *([IntegrationV0MessageEvent.DEVICE__MEASURE_CHANNELS_SETTINGS_CHANGED] if self.event_device_measure_channels_settings_changed else []),
                    *([IntegrationV0MessageEvent.DEVICE__DIGITAL_I_O_SETTINGS_CHANGED] if self.event_device_digital_i_o_settings_changed else []),
                    *([IntegrationV0MessageEvent.DEVICE__DATETIME_CHANGED] if self.event_device_datetime_changed else []),
                    *([IntegrationV0MessageEvent.DEVICE__ETHERNET_SETTINGS_CHANGED] if self.event_device_ethernet_settings_changed else []),
                    *([IntegrationV0MessageEvent.DEVICE__SYSTEM_SETTINGS_CHANGED_1] if self.event_device_system_settings_changed1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__SYSTEM_SETTINGS_CHANGED_2] if self.event_device_system_settings_changed2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__SYSTEM_SETTINGS_CHANGED_3] if self.event_device_system_settings_changed3 else []),
                    *([IntegrationV0MessageEvent.DEVICE__SYSTEM_SETTINGS_CHANGED_4] if self.event_device_system_settings_changed4 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_DIGITAL_INPUT_1] if self.event_device_alarm_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_1] if self.event_device_alarm_overrate_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_2] if self.event_device_alarm_overrate_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_1] if self.event_device_alarm_underrate_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_2] if self.event_device_alarm_underrate_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_1] if self.event_device_alarm_t_high_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_2] if self.event_device_alarm_t_high_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_T_LOW_DIGITAL_INPUT_1] if self.event_device_alarm_t_low_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_T_LOW_DIGITAL_INPUT_2] if self.event_device_alarm_t_low_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_1] if self.event_device_alarm_delta_t_high_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_2] if self.event_device_alarm_delta_t_high_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_1] if self.event_device_alarm_delta_t_low_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_2] if self.event_device_alarm_delta_t_low_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_1] if self.event_device_alarm_power_high_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_2] if self.event_device_alarm_power_high_digital_input2 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_1] if self.event_device_alarm_power_low_digital_input1 else []),
                    *([IntegrationV0MessageEvent.DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_2] if self.event_device_alarm_power_low_digital_input2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_1] if self.event_ch1_circuit_break_t_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_2] if self.event_ch1_circuit_break_t_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_3] if self.event_ch1_circuit_break_t_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__ERROR_DELTA_T] if self.event_ch1_error_delta_t else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1] if self.event_ch1_consumption_lower_g_min_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2] if self.event_ch1_consumption_lower_g_min_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3] if self.event_ch1_consumption_lower_g_min_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1] if self.event_ch1_consumption_lower_g_max_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2] if self.event_ch1_consumption_lower_g_max_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3] if self.event_ch1_consumption_lower_g_max_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_1] if self.event_ch1_no_coolant_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_2] if self.event_ch1_no_coolant_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_3] if self.event_ch1_no_coolant_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1] if self.event_ch1_circuit_break_stimulation_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2] if self.event_ch1_circuit_break_stimulation_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1] if self.event_ch1_circuit_break_pressure_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2] if self.event_ch1_circuit_break_pressure_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3] if self.event_ch1_circuit_break_pressure_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__REVERSE] if self.event_ch1_reverse else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_1] if self.event_ch2_circuit_break_t_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_2] if self.event_ch2_circuit_break_t_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_3] if self.event_ch2_circuit_break_t_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__ERROR_DELTA_T] if self.event_ch2_error_delta_t else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1] if self.event_ch2_consumption_lower_g_min_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2] if self.event_ch2_consumption_lower_g_min_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3] if self.event_ch2_consumption_lower_g_min_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1] if self.event_ch2_consumption_lower_g_max_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2] if self.event_ch2_consumption_lower_g_max_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3] if self.event_ch2_consumption_lower_g_max_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_1] if self.event_ch2_no_coolant_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_2] if self.event_ch2_no_coolant_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_3] if self.event_ch2_no_coolant_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1] if self.event_ch2_circuit_break_stimulation_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2] if self.event_ch2_circuit_break_stimulation_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1] if self.event_ch2_circuit_break_pressure_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2] if self.event_ch2_circuit_break_pressure_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3] if self.event_ch2_circuit_break_pressure_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__REVERSE] if self.event_ch2_reverse else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_1] if self.event_ch3_circuit_break_t_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_2] if self.event_ch3_circuit_break_t_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_3] if self.event_ch3_circuit_break_t_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__ERROR_DELTA_T] if self.event_ch3_error_delta_t else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1] if self.event_ch3_consumption_lower_g_min_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2] if self.event_ch3_consumption_lower_g_min_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3] if self.event_ch3_consumption_lower_g_min_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1] if self.event_ch3_consumption_lower_g_max_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2] if self.event_ch3_consumption_lower_g_max_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3] if self.event_ch3_consumption_lower_g_max_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_1] if self.event_ch3_no_coolant_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_2] if self.event_ch3_no_coolant_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_3] if self.event_ch3_no_coolant_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1] if self.event_ch3_circuit_break_stimulation_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2] if self.event_ch3_circuit_break_stimulation_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1] if self.event_ch3_circuit_break_pressure_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2] if self.event_ch3_circuit_break_pressure_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3] if self.event_ch3_circuit_break_pressure_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__REVERSE] if self.event_ch3_reverse else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_1] if self.event_ch4_circuit_break_t_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_2] if self.event_ch4_circuit_break_t_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_T_SENSOR_3] if self.event_ch4_circuit_break_t_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__ERROR_DELTA_T] if self.event_ch4_error_delta_t else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1] if self.event_ch4_consumption_lower_g_min_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2] if self.event_ch4_consumption_lower_g_min_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3] if self.event_ch4_consumption_lower_g_min_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1] if self.event_ch4_consumption_lower_g_max_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2] if self.event_ch4_consumption_lower_g_max_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3] if self.event_ch4_consumption_lower_g_max_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_1] if self.event_ch4_no_coolant_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_2] if self.event_ch4_no_coolant_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__NO_COOLANT_CHANNEL_RATE_3] if self.event_ch4_no_coolant_channel_rate_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1] if self.event_ch4_circuit_break_stimulation_channel_rate_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2] if self.event_ch4_circuit_break_stimulation_channel_rate_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1] if self.event_ch4_circuit_break_pressure_sensor_1 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2] if self.event_ch4_circuit_break_pressure_sensor_2 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3] if self.event_ch4_circuit_break_pressure_sensor_3 else []),
                    *([IntegrationV0MessageEvent.SYSTEM__REVERSE] if self.event_ch4_reverse else []),
                ],
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.uptime_ch1.total_seconds())),
                        sensor_type=SensorType.UPTIME,
                        channel_id=1,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.uptime_ch2.total_seconds())),
                        sensor_type=SensorType.UPTIME,
                        channel_id=2,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.uptime_ch3.total_seconds())),
                        sensor_type=SensorType.UPTIME,
                        channel_id=3,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.uptime_ch4.total_seconds())),
                        sensor_type=SensorType.UPTIME,
                        channel_id=4,
                    ),
                ],

            ),
        ]
