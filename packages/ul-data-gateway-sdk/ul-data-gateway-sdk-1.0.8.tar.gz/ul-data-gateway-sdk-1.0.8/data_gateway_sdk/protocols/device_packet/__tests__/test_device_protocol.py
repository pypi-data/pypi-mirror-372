from datetime import datetime, timedelta

from data_gateway_sdk.device_data_protocol import DeviceProtocolType
from data_gateway_sdk.protocols.device_packet.ncp_smp_device_packet import NcpSmpV0DevicePacket
from data_gateway_sdk.protocols.device_packet.smp_device_packet import SmpV0DevicePacket, SmpDaily
from data_gateway_sdk.protocols.device_packet.smpm_device_packet import SmpMGasMeterV0DevicePacket, \
    SmpMEnergyMeterV0DevicePacket, SmpMJupiter08BV0DevicePacket, \
    SmpMJupiter12BV0DevicePacket, SmpMJupiter16BV0DevicePacket, SmpMWaterMeter04BV0DevicePacket, \
    SmpMWaterMeter08BV0DevicePacket, SmpMWaterMeter12BV0DevicePacket, \
    SmpMWaterMeter16BV0DevicePacket
from data_gateway_sdk.protocols.device_packet.water5_device_packet import Water5NeroV0DevicePacket
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_3phase_consumed import \
    SmpmUlDeviceEnergy16B3PhaseConsumedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_3phase_generated import \
    SmpmUlDeviceEnergy16B3PhaseGeneratedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_daily import SmpmUlDeviceEnergy16BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_info import SmpmUlDeviceEnergy16BInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_journal import SmpmUlDeviceEnergy16BJournalData, \
    SmpmUlDeviceEnergy16bJournalType, EventData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h3_energy import \
    SmpmUlDeviceEnergy16bProfile8h3EnergyType, SmpmUlDeviceEnergy16BProfile8H3EnergyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_tariff_consumed import \
    SmpmUlDeviceEnergy16BTariffConsumedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_tariff_generated import \
    SmpmUlDeviceEnergy16BTariffGeneratedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_gaz_flow_08b_daily import SmpmUlDeviceGazFlow08BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_gaz_flow_16b_daily import SmpmUlDeviceGazFlow16BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter import SmpmUlDeviceJupiter08BCounterData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_ch1 import SmpmUlDeviceJupiter08BCounterCh1Data
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_ch2 import SmpmUlDeviceJupiter08BCounterCh2Data
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_12b_counter import SmpmUlDeviceJupiter12BCounterData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_16b_counter import SmpmUlDeviceJupiter16BCounterData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_04b_event import SmpmUlDeviceWaterMeter04BEventData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_daily import SmpmUlDeviceWaterMeter08BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_daily_new import \
    SmpmUlDeviceWaterMeter08BDailyNewData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_info import SmpmUlDeviceWaterMeter08BInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_12b_daily import SmpmUlDeviceWaterMeter12BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_16b_daily import SmpmUlDeviceWaterMeter16BDailyData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_cold_reset import Water5DeviceColdResetData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_daily import Water5DeviceDailyData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_info_ch1 import Water5DeviceInfoCh1Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_magnet import Water5DeviceMagnetData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch1 import Water5DeviceWeeklyCh1Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch2 import Water5DeviceWeeklyCh2Data


# FLUO(FREESCALE) , NBFI
# assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('97157A6F8028CF075DE4DC4EB9752171EBAF87E704E3C12E7905126ED48747946068D9E4'))


# FLUO A, NBFI
# assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('97157A6F8028CF075DE4DC4EB9752171EBAF87E704E3C12E7905126ED48747946068D9E4'))


def test_protocol_water5_v_nero_v0() -> None:
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('54c2000000000000')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceDailyData(value=24.874),
    )]

    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('73086e0a000000a5')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=683.528,
            # battery=3.37,
            battery_int=3,
            battery_fract=37,
        ),
    )]

    assert 3 + (37 / 100) == 3.37

    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('7b3a00000000001f')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh2Data(
            value=0.058,
            # battery=2.31,
            battery_int=2,
            battery_fract=31,
        ),
    )]

    # FLUO A, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000 ПОТОМУ ЧТО м3 а не в литрах
            # battery=3.67,
            battery_int=3,
            battery_fract=67,
        ),
    )]

    # FLUO A, W5, INFO
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC4894470000D9')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда, В ДОКЕ УКАЗАНО 00 !!!!!(возможно опечатка)
        ),
    )]

    # FLUO A, W5, RESET
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('41CC489447014100')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceColdResetData(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
    )]

    # FLUO A, W5, WARM_RESET
    # assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('41CC4894470100')) == Water5NeroV0DeviceData(
    #     cold_reset=Water5WarmReset(
    #         ???
    #     ),
    # )

    # FLUO(FREESCALE), W5, DAILY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('6086000000000000')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceDailyData(
            value=17200 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
    )]

    # FLUO(FREESCALE), W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
    )]

    # FLUO(FREESCALE), W5, WEEKLY (исп.0), Размерность переменной накопленного объема в прямом направлении за все время равна 24 бит вместо 27 бит.
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('73DA45A3000000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=10700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            # battery=3.67,
            battery_int=3,
            battery_fract=67,
        ),  # counter_bit_size исходя из описания возможно максимум 24???
    )]
    # WEEKLY и WEEKLY (исп.0) дают идентичный результат

    # FLUO(FREESCALE), W5, INFO, Размерность переменной накопленного объема в прямом направлении за все время равна 24 бит вместо 27 бит.
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC4894470000D9')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
    )]

    # FLUO(FREESCALE), W5, INFO(исп.0), Присутствует значение переменной общего количества отправленных пакетов count_send_message
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC489447F875D9')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
    )]

    print(1111111111111111111111111111111)
    # # FLUO(FREESCALE), W5, RESET
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('41CC489447014100')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceColdResetData(
            value=1200900300 / 1000,
        ),
    )]

    # FLUO(FREESCALE), W5, COMMAND
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('51AAAAAAAAAAAAAA')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceMagnetData(),
    )]

    # FLUO(FREESCALE), W5, WARM_RESET
    # assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('43820000004E4552')) == Water5NeroV0DeviceData(
    #     command=Water5WarmReset(
    #         ???
    #     ),
    # )

    # JUPITER FREESCALE/STM32, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31000000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=3259738 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            # battery=3.67,
            battery_int=3,
            battery_fract=67,
        ),
    )]

    # JUPITER FREESCALE/STM32, W5, WARM_RESET
    # assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('43210000004E4552')) == Water5NeroV0DeviceData(
    #     weekly=Water5WarmReset(
    #         ???
    #     ),
    # )

    # FLUO LoRa, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            # battery=3.67,
            battery_int=3,
            battery_fract=67,
        ),
    )]

    # FLUO STM, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            # battery=3.67,
            battery_int=3,
            battery_fract=67,
        ),
    )]
    # FLUO LoRa, W5, WEEKLY = FLUO STM, W5, WEEKLY

    # FLUO STM, W5, INFO
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC4894470000D9')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
    )]

    # FLUO STM, W5, COMMAND
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('51AAAAAAAAAAAAAA')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceMagnetData(),
    )]

    # FLUO STM, W5, WARM_RESET
    # assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('43000000104E4552')) == Water5NeroV0DeviceData(
    #     ??
    # )

    # Jupiter LoRa, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3')) == [Water5NeroV0DevicePacket(  # type: ignore
        packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            # battery=3.67,
            battery_int=3,
            battery_fract=67,
        ),
    )]


def test_protocol_smp_v0() -> None:
    assert DeviceProtocolType.SMP_V0.parse(bytes.fromhex("09800605030000016ed88d016fd999051f1620dc02318b9a9ffc05")) == [SmpV0DevicePacket(
        packet=SmpDaily(
            info_id_code=3,
            sdata_count_ch1_code=18136,
            sdata_count_ch2_code=85209,
            sdata_temperature_code=22,
            sdata_battery_code=3.48,
            sdata_datetime_code=datetime(year=2062, month=10, day=15, hour=4, minute=16, second=11),
        ),
    )]

    # Jupiter NBIoT, SMP, daily
    assert DeviceProtocolType.SMP_V0.parse(bytes.fromhex("09800605AC020000016ED4576F98431F1620EF0231F893CB8306")) == [SmpV0DevicePacket(
        packet=SmpDaily(
            info_id_code=300,
            sdata_count_ch1_code=11220,
            sdata_count_ch2_code=8600,
            sdata_temperature_code=22,
            sdata_battery_code=367 / 100,  # по документации
            sdata_datetime_code=datetime(2063, 4, 11, 10, 5, 44),
        ),
    )]

    # Metano NBIoT, SMP, daily
    assert DeviceProtocolType.SMP_V0.parse(bytes.fromhex("09800605AC020000016ED4576F98431F1620EF0231F893CB8306")) == [SmpV0DevicePacket(
        packet=SmpDaily(
            info_id_code=300,
            sdata_count_ch1_code=11220,
            sdata_count_ch2_code=8600,
            sdata_temperature_code=22,
            sdata_battery_code=367 / 100,  # по документации
            sdata_datetime_code=datetime(2063, 4, 11, 10, 5, 44),
        ),
    )]
    # Jupiter NBIoT, SMP, daily = Metano NBIoT, SMP, daily


def test_protocol_smpm_gaz_v0() -> None:
    assert DeviceProtocolType.SMP_M_GAS_METER_V0.parse(bytes.fromhex('64e4eab1067b2100')) == [SmpMGasMeterV0DevicePacket(  # type: ignore
        packet=SmpmUlDeviceGazFlow08BDailyData(
            cumulative_volume=112323.3,
            temperature=23,
            battery_volts=3.3,
            event_reset=False,
            event_case_was_opened=False,
            event_flow_reverse=False,
            event_flow_speed_is_over_limit=False,
            event_sensor_error_measurement=False,
            event_sensor_error_temperature=False,
            event_low_battery_level=False,
            event_system_error=False,
        ),
    )]


def test_protocol_ncp_smp_v0() -> None:
    assert DeviceProtocolType.NCP_SMP_V0.parse(bytes.fromhex("0603000000000609800605030000016ed88d016fd999051f1620dc02318b9a9ffc052df2")) == [NcpSmpV0DevicePacket(
        mac=3,
        packet=SmpDaily(
            info_id_code=3,
            sdata_count_ch1_code=18136,
            sdata_count_ch2_code=85209,
            sdata_temperature_code=22,
            sdata_battery_code=3.48,
            sdata_datetime_code=datetime(year=2062, month=10, day=15, hour=4, minute=16, second=11),
        ),
    )]


def test_protocol_smpm_energy_v0_multiple_parsing() -> None:
    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("cc02300f1e00900d0160574cdb5e0105cc02300f1e00900d0160574cdb5e0105")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(
            packet=SmpmUlDeviceEnergy16B3PhaseConsumedData(
                energy_is_reactive=False,
                days_ago=timedelta(seconds=0.0),
                valid=False, total=123123,
                phase_a=4313,
                phase_b=14312123,
                phase_c=1312123,
            )),
        SmpMEnergyMeterV0DevicePacket(
            packet=SmpmUlDeviceEnergy16B3PhaseConsumedData(
                energy_is_reactive=False,
                days_ago=timedelta(seconds=0.0),
                valid=False, total=123123,
                phase_a=4313,
                phase_b=14312123,
                phase_c=1312123,
            )),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("cb02300f1e00900d0160574cdb5e0105cb02300f1e00900d0160574cdb5e0105")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(
            packet=SmpmUlDeviceEnergy16B3PhaseGeneratedData(
                energy_is_reactive=False,
                days_ago=timedelta(seconds=0.0),
                valid=False,
                total=123123,
                phase_a=4313,
                phase_b=14312123,
                phase_c=1312123,
            ),
        ),
        SmpMEnergyMeterV0DevicePacket(
            packet=SmpmUlDeviceEnergy16B3PhaseGeneratedData(
                energy_is_reactive=False,
                days_ago=timedelta(seconds=0.0),
                valid=False,
                total=123123,
                phase_a=4313,
                phase_b=14312123,
                phase_c=1312123,
            ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("bbaaaaae545f55aaaa2abbaa6a80160bbbaaaaae545f55aaaa2abbaa6a80160b")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(
            packet=SmpmUlDeviceEnergy16BDailyData(
                energy_consumed_active=1430869,
                energy_consumed_reactive=1398741,
                energy_generated_active=1398101,
                energy_generated_reactive=6990523,
                days_ago=timedelta(seconds=0.0),
                valid=False,
                error_measurement=True,
                error_low_voltage=False,
                error_internal_clock=True,
                error_flash=True,
                error_eeprom=False,
                error_radio=True,
                error_display=False,
                error_plc=False,
                error_reset=False,
                impact_power_lost=True,
                impact_magnet=True,
                impact_cleat_tamper=False,
                impact_body_tamper=True,
                impact_radio=False,
            ),
        ),
        SmpMEnergyMeterV0DevicePacket(
            packet=SmpmUlDeviceEnergy16BDailyData(
                energy_consumed_active=1430869,
                energy_consumed_reactive=1398741,
                energy_generated_active=1398101,
                energy_generated_reactive=6990523,
                days_ago=timedelta(seconds=0.0),
                valid=False,
                error_measurement=True,
                error_low_voltage=False,
                error_internal_clock=True,
                error_flash=True,
                error_eeprom=False,
                error_radio=True,
                error_display=False,
                error_plc=False,
                error_reset=False,
                impact_power_lost=True,
                impact_magnet=True,
                impact_cleat_tamper=False,
                impact_body_tamper=True,
                impact_radio=False,
            ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("bc0aed017c5687000000000000000000bc0aed017c5687000000000000000000")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BInfoData(
            battery_volts=3.3,
            temperature=23,
            date_time=timedelta(seconds=567648000.0),
            relay_is_active=False,
        ),
        ),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BInfoData(
            battery_volts=3.3,
            temperature=23,
            date_time=timedelta(seconds=567648000.0),
            relay_is_active=False,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("7300cc380000000000000000000000007300cc38000000000000000000000000")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BJournalData(
            days_ago=timedelta(seconds=0.0),
            valid=False,
            time_offset=timedelta(seconds=14400.0),
            journal=(
                EventData(offset=timedelta(seconds=180.0), code=SmpmUlDeviceEnergy16bJournalType.CHANGE_OFFSET_DAILY_CLOCK),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
            ),
        )),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BJournalData(
            days_ago=timedelta(seconds=0.0),
            valid=False,
            time_offset=timedelta(seconds=14400.0),
            journal=(
                EventData(offset=timedelta(seconds=180.0), code=SmpmUlDeviceEnergy16bJournalType.CHANGE_OFFSET_DAILY_CLOCK),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
                EventData(offset=timedelta(seconds=0.0), code=SmpmUlDeviceEnergy16bJournalType.NONE),
            ),
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("6c060080002000060001280006e000c86c060080002000060001280006e000c8")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BProfile8H3EnergyData(
            type=SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE,
            days_ago=timedelta(seconds=0.0),
            profile=(0, 1, 2, 3, 4, 5, 6, 7),
            point_factor=5.0,
            point_factor_multiplier=2,
        ),
        ),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BProfile8H3EnergyData(
            type=SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE,
            days_ago=timedelta(seconds=0.0),
            profile=(0, 1, 2, 3, 4, 5, 6, 7),
            point_factor=5.0,
            point_factor_multiplier=2,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("6c060080002000060001280006e000c86c060080002000060001280006e000c8")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BProfile8H3EnergyData(
            type=SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE,
            days_ago=timedelta(seconds=0.0),
            profile=(0, 1, 2, 3, 4, 5, 6, 7),
            point_factor=5.0,
            point_factor_multiplier=2,
        ),
        ),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BProfile8H3EnergyData(
            type=SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE,
            days_ago=timedelta(seconds=0.0),
            profile=(0, 1, 2, 3, 4, 5, 6, 7),
            point_factor=5.0,
            point_factor_multiplier=2,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("6c060080002000060001280006e000c86c060080002000060001280006e000c8")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BProfile8H3EnergyData(
            type=SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE,
            days_ago=timedelta(seconds=0.0),
            profile=(0, 1, 2, 3, 4, 5, 6, 7),
            point_factor=5.0,
            point_factor_multiplier=2,
        ),
        ),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BProfile8H3EnergyData(
            type=SmpmUlDeviceEnergy16bProfile8h3EnergyType.ENERGY_CONSUMED_ACTIVE,
            days_ago=timedelta(seconds=0.0),
            profile=(0, 1, 2, 3, 4, 5, 6, 7),
            point_factor=5.0,
            point_factor_multiplier=2,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("c20250320f1e60873948490500000000c20250320f1e60873948490500000000")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BTariffConsumedData(
            energy_is_reactive=False,
            days_ago=timedelta(seconds=0.0),
            valid=False,
            tariff_mask=(True, False, True, False, False, True, False, False),
            slot_0=123123,
            slot_1=4312123,
            slot_2=5413,
            slot_3=0,
        ),
        ),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BTariffConsumedData(
            energy_is_reactive=False,
            days_ago=timedelta(seconds=0.0),
            valid=False,
            tariff_mask=(True, False, True, False, False, True, False, False),
            slot_0=123123,
            slot_1=4312123,
            slot_2=5413,
            slot_3=0,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_ENERGY_METER_V0.parse(bytes.fromhex("c10250320f1e60873948490500000000c10250320f1e60873948490500000000")) == [  # type: ignore
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BTariffGeneratedData(
            energy_is_reactive=False,
            days_ago=timedelta(seconds=0.0),
            valid=False,
            tariff_mask=(True, False, True, False, False, True, False, False),
            slot_0=123123,
            slot_1=4312123,
            slot_2=5413,
            slot_3=0,
        ),
        ),
        SmpMEnergyMeterV0DevicePacket(packet=SmpmUlDeviceEnergy16BTariffGeneratedData(
            energy_is_reactive=False,
            days_ago=timedelta(seconds=0.0),
            valid=False,
            tariff_mask=(True, False, True, False, False, True, False, False),
            slot_0=123123,
            slot_1=4312123,
            slot_2=5413,
            slot_3=0,
        ),
        ),
    ]


def test_protocol_smpm_gas_v0_multiple_parsing() -> None:
    assert DeviceProtocolType.SMP_M_GAS_METER_V0.parse(bytes.fromhex("820c188416011a00000000000000000064e4eab1067b2100")) == [  # type: ignore
        SmpMGasMeterV0DevicePacket(packet=SmpmUlDeviceGazFlow16BDailyData(
            days_ago=timedelta(0),
            sync_time_days_ago=timedelta(days=3),
            timestamp_s=timedelta(days=3, seconds=26000),
            temperature=-9,
            battery_volts=0.0,
            event_reset=False,
            event_low_battery_level=False,
            event_temperature_limits=False,
            direct_flow_volume=0.0,
            direct_flow_volume_day_ago=0.0,
            reverse_flow_volume=0.0,
            event_battery_warn=False,
            event_system_error=False,
            event_flow_reverse=False,
            event_flow_speed_is_over_limit=False,
            event_sensor_error=False,
            event_sensor_error_temperature=False,
            event_case_was_opened=False,
            event_continuous_consumption=False,
            event_no_resource=False,
        ),
        ),
        SmpMGasMeterV0DevicePacket(packet=SmpmUlDeviceGazFlow08BDailyData(
            cumulative_volume=112323.3,
            temperature=23,
            battery_volts=3.3,
            event_reset=False,
            event_case_was_opened=False,
            event_flow_reverse=False,
            event_flow_speed_is_over_limit=False,
            event_sensor_error_measurement=False,
            event_sensor_error_temperature=False,
            event_low_battery_level=False,
            event_system_error=False,
        ),
        ),
    ]


def test_protocol_smpm_jupiter_multiple_parsing() -> None:
    assert DeviceProtocolType.SMP_M_JUPITER_08B_V0.parse(bytes.fromhex("65fffffffbffffdf66ffffff7fa16e0067ffffff7fa16e00")) == [  # type: ignore
        SmpMJupiter08BV0DevicePacket(packet=SmpmUlDeviceJupiter08BCounterData(
            value_channel_1=67108863,
            value_channel_2=67108863,
            event_reset=True,
            event_low_battery_level=True,
        ),
        ),
        SmpMJupiter08BV0DevicePacket(packet=SmpmUlDeviceJupiter08BCounterCh1Data(
            value=2147483647,
            battery_volts=3.3,
            temperature=23,
            event_reset=True,
            event_low_battery_level=True,
        ),
        ),
        SmpMJupiter08BV0DevicePacket(packet=SmpmUlDeviceJupiter08BCounterCh2Data(
            value=2147483647,
            battery_volts=3.3,
            temperature=23,
            event_reset=True,
            event_low_battery_level=True,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_JUPITER_12B_V0.parse(bytes.fromhex("d4f9ffffffefffffffbf5037d4f9ffffffefffffffbf5037")) == [  # type: ignore
        SmpMJupiter12BV0DevicePacket(packet=SmpmUlDeviceJupiter12BCounterData(
            value_channel_1=8589934591,
            value_channel_2=8589934591,
            battery_volts=3.3,
            temperature=23,
            event_reset=True,
            event_low_battery_level=True,
        ),
        ),
        SmpMJupiter12BV0DevicePacket(packet=SmpmUlDeviceJupiter12BCounterData(
            value_channel_1=8589934591,
            value_channel_2=8589934591,
            battery_volts=3.3,
            temperature=23,
            event_reset=True,
            event_low_battery_level=True,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_JUPITER_16B_V0.parse(bytes.fromhex("810cc0ffff7fba90fdfffffffeffff7f810cc0ffff7fba90fdfffffffeffff7f")) == [  # type: ignore
        SmpMJupiter16BV0DevicePacket(packet=SmpmUlDeviceJupiter16BCounterData(
            days_ago=timedelta(seconds=0.0),
            sync_time_days_ago=timedelta(seconds=0.0),
            timestamp_s=timedelta(seconds=33554431.0),
            temperature=23,
            battery_volts=3.3,
            event_reset=False,
            event_low_battery_level=False,
            event_temperature_limits=True,
            event_battery_warn=True,
            event_system_error=False,
            value_channel_1=1073741823,
            value_channel_2=1073741823,
        ),
        ),
        SmpMJupiter16BV0DevicePacket(packet=SmpmUlDeviceJupiter16BCounterData(
            days_ago=timedelta(seconds=0.0),
            sync_time_days_ago=timedelta(seconds=0.0),
            timestamp_s=timedelta(seconds=33554431.0),
            temperature=23,
            battery_volts=3.3,
            event_reset=False,
            event_low_battery_level=False,
            event_temperature_limits=True,
            event_battery_warn=True,
            event_system_error=False,
            value_channel_1=1073741823,
            value_channel_2=1073741823,
        ),
        ),
    ]


def test_protocol_smpm_water_meter_multiple_parsing() -> None:
    assert DeviceProtocolType.SMP_M_WATER_METER_04B_V0.parse(bytes.fromhex('0ce13a060ce13a06')) == [  # type: ignore
        SmpMWaterMeter04BV0DevicePacket(packet=SmpmUlDeviceWaterMeter04BEventData(
            battery_volts=3.3,
            event_low_battery_level=True,
            event_temperature_limits=True,
            temperature=23,
            event_case_was_opened=False,
            event_magnet=False,
            event_reset=True,
            event_sensor_error=True,
        ),
        ),
        SmpMWaterMeter04BV0DevicePacket(packet=SmpmUlDeviceWaterMeter04BEventData(
            battery_volts=3.3,
            event_low_battery_level=True,
            event_temperature_limits=True,
            temperature=23,
            event_case_was_opened=False,
            event_magnet=False,
            event_reset=True,
            event_sensor_error=True,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_WATER_METER_08B_V0.parse(bytes.fromhex('68e4eab106a33a7874e4eab1d685cf4069e14a1400000000')) == [  # type: ignore
        SmpMWaterMeter08BV0DevicePacket(packet=SmpmUlDeviceWaterMeter08BDailyData(
            direct_flow_volume=112323.3,
            direct_flow_volume_day_ago=3.5,
            event_battery_or_temperature_limits=True,
            temperature=23,
            event_magnet=False,
            event_continues_consumption=False,
            event_case_was_opened=False,
            event_system_error=False,
            event_reset=True,
            event_sensor_error=True,
            event_no_resource=True,
            event_flow_speed_is_over_limit=True,
            event_flow_reverse=False,
        ),
        ),
        SmpMWaterMeter08BV0DevicePacket(packet=SmpmUlDeviceWaterMeter08BDailyNewData(
            value=112323.3,
            temperature=23,
            battery_volts=3.3,
            event_low_battery_level=True,
            event_temperature_limits=True,
            event_reset=True,
            event_magnet=True,
            event_reverse_flow=False,
            value_reverse=0.518,
        ),
        ),
        SmpMWaterMeter08BV0DevicePacket(packet=SmpmUlDeviceWaterMeter08BInfoData(
            battery_volts=3.3,
            event_battery_low=True,
            event_battery_warn=True,
            reverse_flow_volume=10.98,
            event_flow_reverse=True,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_WATER_METER_12B_V0.parse(bytes.fromhex('63c0e4eab1062337bae14a2463c0e4eab1062337bae14a24')) == [  # type: ignore
        SmpMWaterMeter12BV0DevicePacket(packet=SmpmUlDeviceWaterMeter12BDailyData(
            days_ago=timedelta(seconds=0.0),
            event_case_was_opened=False,
            event_reset=True,
            event_sensor_error=True,
            direct_flow_volume=112323.3,
            direct_flow_volume_day_ago=3.5,
            event_magnet=False,
            direct_flow_volume_2days_ago=5.5,
            event_continues_consumption=False,
            temperature=23,
            event_temperature_limits=True,
            battery_volts=3.3,
            event_battery_warn=True,
            event_flow_speed_is_over_limit=True,
            reverse_flow_volume=1.098,
            event_flow_reverse=False,
            event_no_resource=True,
            event_system_error=False,
        ),
        ),
        SmpMWaterMeter12BV0DevicePacket(packet=SmpmUlDeviceWaterMeter12BDailyData(
            days_ago=timedelta(seconds=0.0),
            event_case_was_opened=False,
            event_reset=True,
            event_sensor_error=True,
            direct_flow_volume=112323.3,
            direct_flow_volume_day_ago=3.5,
            event_magnet=False,
            direct_flow_volume_2days_ago=5.5,
            event_continues_consumption=False,
            temperature=23,
            event_temperature_limits=True,
            battery_volts=3.3,
            event_battery_warn=True,
            event_flow_speed_is_over_limit=True,
            reverse_flow_volume=1.098,
            event_flow_reverse=False,
            event_no_resource=True,
            event_system_error=False,
        ),
        ),
    ]

    assert DeviceProtocolType.SMP_M_WATER_METER_16B_V0.parse(bytes.fromhex('830cc0ffff7fba90e4eab10623250a08830cc0ffff7fba90e4eab10623250a08')) == [  # type: ignore
        SmpMWaterMeter16BV0DevicePacket(packet=SmpmUlDeviceWaterMeter16BDailyData(
            days_ago=timedelta(seconds=0.0),
            sync_time_days_ago=timedelta(seconds=0.0),
            timestamp_s=timedelta(seconds=33554431.0),
            temperature=23,
            battery_volts=3.3,
            event_reset=False,
            event_low_battery_level=False,
            event_temperature_limits=True,
            direct_flow_volume=112323.3,
            direct_flow_volume_day_ago=3.5,
            reverse_flow_volume=1.098,
            event_battery_warn=True,
            event_system_error=False,
            event_flow_reverse=False,
            event_flow_speed_is_over_limit=False,
            event_sensor_error=False,
            event_sensor_error_temperature=False,
            event_case_was_opened=False,
            event_continuous_consumption=False,
            event_no_resource=True,
            event_magnet=False,
        ),
        ),
        SmpMWaterMeter16BV0DevicePacket(packet=SmpmUlDeviceWaterMeter16BDailyData(
            days_ago=timedelta(seconds=0.0),
            sync_time_days_ago=timedelta(seconds=0.0),
            timestamp_s=timedelta(seconds=33554431.0),
            temperature=23,
            battery_volts=3.3,
            event_reset=False,
            event_low_battery_level=False,
            event_temperature_limits=True,
            direct_flow_volume=112323.3,
            direct_flow_volume_day_ago=3.5,
            reverse_flow_volume=1.098,
            event_battery_warn=True,
            event_system_error=False,
            event_flow_reverse=False,
            event_flow_speed_is_over_limit=False,
            event_sensor_error=False,
            event_sensor_error_temperature=False,
            event_case_was_opened=False,
            event_continuous_consumption=False,
            event_no_resource=True,
            event_magnet=False,
        ),
        ),
    ]


def test_protocol_water5_v0_multiple_parsing() -> None:
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('54c200000000000054c2000000000000')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceDailyData(value=24.874)),
        Water5NeroV0DevicePacket(packet=Water5DeviceDailyData(value=24.874)),
    ]

    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('73086e0a000000a573086e0a000000a5')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=683.528,
            battery_int=3,
            battery_fract=37,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=683.528,
            battery_int=3,
            battery_fract=37,
        ),
        ),
    ]

    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('7b3a00000000001f7b3a00000000001f735ABD31070000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh2Data(
            value=0.058,
            battery_int=2,
            battery_fract=31,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh2Data(
            value=0.058,
            battery_int=2,
            battery_fract=31,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000 ПОТОМУ ЧТО м3 а не в литрах
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]

    # FLUO A, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3735ABD31070000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000 ПОТОМУ ЧТО м3 а не в литрах
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000 ПОТОМУ ЧТО м3 а не в литрах
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]

    # FLUO A, W5, INFO
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC4894470000D961CC4894470000D9')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда, В ДОКЕ УКАЗАНО 00 !!!!!(возможно опечатка)
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда, В ДОКЕ УКАЗАНО 00 !!!!!(возможно опечатка)
        ),
        ),
    ]

    # FLUO A, W5, RESET
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('41CC48944701410041CC489447014100')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceColdResetData(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceColdResetData(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
    ]

    # FLUO(FREESCALE), W5, DAILY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('60860000000000006086000000000000')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceDailyData(
            value=17200 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceDailyData(
            value=17200 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
    ]

    # FLUO(FREESCALE), W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3735ABD31070000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]

    # FLUO(FREESCALE), W5, WEEKLY (исп.0), Размерность переменной накопленного объема в прямом направлении за все время равна 24 бит вместо 27 бит.
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('73DA45A3000000C373DA45A3000000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=10700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=10700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),  # counter_bit_size исходя из описания возможно максимум 24???
        ),
    ]
    # WEEKLY и WEEKLY (исп.0) дают идентичный результат

    # FLUO(FREESCALE), W5, INFO, Размерность переменной накопленного объема в прямом направлении за все время равна 24 бит вместо 27 бит.
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC4894470000D961CC4894470000D9')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
    ]

    # FLUO(FREESCALE), W5, INFO(исп.0), Присутствует значение переменной общего количества отправленных пакетов count_send_message
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC489447F875D961CC489447F875D9')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
    ]

    # FLUO(FREESCALE), W5, RESET
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('41CC48944701410041CC489447014100')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceColdResetData(
            value=1200900300 / 1000,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceColdResetData(
            value=1200900300 / 1000,
        ),
        ),
    ]

    # FLUO(FREESCALE), W5, COMMAND
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('51AAAAAAAAAAAAAA51AAAAAAAAAAAAAA')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceMagnetData()),
        Water5NeroV0DevicePacket(packet=Water5DeviceMagnetData()),
    ]

    # JUPITER FREESCALE/STM32, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31000000C3735ABD31000000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=3259738 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=3259738 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]

    # FLUO LoRa, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3735ABD31070000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]

    # FLUO STM, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3735ABD31070000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]
    # FLUO LoRa, W5, WEEKLY = FLUO STM, W5, WEEKLY

    # FLUO STM, W5, INFO
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('61CC4894470000D961CC4894470000D9')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceInfoCh1Data(
            value=1200900300 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
        ),
        ),
    ]

    # FLUO STM, W5, COMMAND
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('51AAAAAAAAAAAAAA51AAAAAAAAAAAAAA')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceMagnetData()),
        Water5NeroV0DevicePacket(packet=Water5DeviceMagnetData()),
    ]

    # Jupiter LoRa, W5, WEEKLY
    assert DeviceProtocolType.WATER5_V_NERO_V0.parse(bytes.fromhex('735ABD31070000C3735ABD31070000C3')) == [  # type: ignore
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
        Water5NeroV0DevicePacket(packet=Water5DeviceWeeklyCh1Data(
            value=120700250 / 1000,  # не совпадает поле, множитель 1000, выяснить откуда
            battery_int=3,
            battery_fract=67,
        ),
        ),
    ]
