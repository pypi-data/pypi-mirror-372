from typing import Tuple, Type

from data_gateway_sdk.protocols.device_packet.device_packet import DevicePacketTyped
from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_16b_get_data import SmpmDlDeviceEnergy16BGetDataData
from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_16b_set_regular_data_sending import \
    SmpmDlDeviceEnergy16BSetRegularDataSendingData
from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_8b_get_data import SmpmDlDeviceEnergy8BGetDataData
from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_8b_set_clock import SmpmDlDeviceEnergy8BSetClockData
from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_8b_set_relay import SmpmDlDeviceEnergy8BSetRelayData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_dl_answer import SmpmUlDeviceDlAnswerData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_3phase_consumed import SmpmUlDeviceEnergy16B3PhaseConsumedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_3phase_generated import \
    SmpmUlDeviceEnergy16B3PhaseGeneratedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_daily import SmpmUlDeviceEnergy16BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_device_info import SmpmUlDeviceEnergy16BDeviceInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_electricity_params import SmpmUlDeviceEnergy16BElectricityParamsData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_info import SmpmUlDeviceEnergy16BInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_journal import SmpmUlDeviceEnergy16BJournalData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h1_energy import \
    SmpmUlDeviceEnergy16BProfile8H1EnergyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h2_energy import \
    SmpmUlDeviceEnergy16BProfile8H2EnergyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h3_energy import \
    SmpmUlDeviceEnergy16BProfile8H3EnergyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_ar import SmpmUlDeviceEnergy16BProfile8HArData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_energy import SmpmUlDeviceEnergy16BProfile8HEnergyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_f import SmpmUlDeviceEnergy16BProfile8HFData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h_pqs import SmpmUlDeviceEnergy16BProfile8HPqsData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_retrospective_energy import SmpmUlDeviceEnergy16BRetrospectiveEnergyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_status_info import SmpmUlDeviceEnergy16BStatusInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_tariff_consumed import \
    SmpmUlDeviceEnergy16BTariffConsumedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_tariff_generated import \
    SmpmUlDeviceEnergy16BTariffGeneratedData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_gaz_flow_08b_daily import SmpmUlDeviceGazFlow08BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_gaz_flow_16b_daily import SmpmUlDeviceGazFlow16BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_heat_group_meter_56b_daily import SmpmUlDeviceHeatGroupMeter56BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_heat_group_meter_daily import SmpmUlDeviceHeatGroupMeterDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_heat_proxy_meter_16b_daily import SmpmUlDeviceHeatProxyMeter16BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_internal_info import SmpmUlDeviceInternalInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter import SmpmUlDeviceJupiter08BCounterData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_ch1 import SmpmUlDeviceJupiter08BCounterCh1Data
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_ch2 import SmpmUlDeviceJupiter08BCounterCh2Data
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_08b_counter_volume import \
    SmpmUlDeviceJupiter08BCounterVolumeData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_12b_counter import SmpmUlDeviceJupiter12BCounterData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_12b_counter_volume import \
    SmpmUlDeviceJupiter12BCounterVolumeData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_jupiter_16b_counter import SmpmUlDeviceJupiter16BCounterData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_04b_event import SmpmUlDeviceWaterMeter04BEventData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_daily import SmpmUlDeviceWaterMeter08BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_daily_new import \
    SmpmUlDeviceWaterMeter08BDailyNewData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_08b_info import SmpmUlDeviceWaterMeter08BInfoData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_12b_daily import SmpmUlDeviceWaterMeter12BDailyData
from data_gateway_sdk.protocols.smpm.smpm_ul_device_water_meter_16b_daily import SmpmUlDeviceWaterMeter16BDailyData
from data_gateway_sdk.utils.packet import Packet


class SmpMGasMeterV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceGazFlow08BDailyData,
        SmpmUlDeviceGazFlow16BDailyData,
    )


class SmpMEnergyMeterV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceEnergy16B3PhaseConsumedData,
        SmpmUlDeviceEnergy16B3PhaseGeneratedData,
        SmpmUlDeviceEnergy16BDailyData,
        SmpmUlDeviceEnergy16BProfile8H1EnergyData,
        SmpmUlDeviceEnergy16BProfile8H2EnergyData,
        SmpmUlDeviceEnergy16BProfile8H3EnergyData,
        SmpmUlDeviceEnergy16BProfile8HArData,
        SmpmUlDeviceEnergy16BProfile8HFData,
        SmpmUlDeviceEnergy16BProfile8HPqsData,
        SmpmUlDeviceEnergy16BTariffConsumedData,
        SmpmUlDeviceEnergy16BTariffGeneratedData,
        SmpmUlDeviceEnergy16BInfoData,
        SmpmUlDeviceEnergy16BJournalData,
    )


class SmpMEnergyMeterV1DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceEnergy16B3PhaseConsumedData,
        SmpmUlDeviceEnergy16B3PhaseGeneratedData,
        SmpmUlDeviceEnergy16BDailyData,
        SmpmUlDeviceEnergy16BProfile8H1EnergyData,
        SmpmUlDeviceEnergy16BProfile8H2EnergyData,
        SmpmUlDeviceEnergy16BProfile8H3EnergyData,
        SmpmUlDeviceEnergy16BProfile8HArData,
        SmpmUlDeviceEnergy16BProfile8HFData,
        SmpmUlDeviceEnergy16BProfile8HPqsData,
        SmpmUlDeviceEnergy16BTariffConsumedData,
        SmpmUlDeviceEnergy16BTariffGeneratedData,
        SmpmUlDeviceEnergy16BInfoData,
        SmpmUlDeviceEnergy16BJournalData,
        SmpmUlDeviceEnergy16BElectricityParamsData,
        SmpmUlDeviceEnergy16BProfile8HEnergyData,
        SmpmUlDeviceEnergy16BRetrospectiveEnergyData,
        SmpmUlDeviceEnergy16BDeviceInfoData,
        SmpmUlDeviceEnergy16BStatusInfoData,
        SmpmUlDeviceDlAnswerData,
    )


class SmpMJupiter08BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceJupiter08BCounterData,
        SmpmUlDeviceJupiter08BCounterCh1Data,
        SmpmUlDeviceJupiter08BCounterCh2Data,
        SmpmUlDeviceJupiter08BCounterVolumeData,
    )


class SmpMJupiter12BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceJupiter12BCounterData,
        SmpmUlDeviceJupiter12BCounterVolumeData,
    )


class SmpMJupiter16BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceJupiter16BCounterData,
    )


class SmpMWaterMeter04BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceWaterMeter04BEventData,
    )


class SmpMWaterMeter08BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceWaterMeter08BDailyData,
        SmpmUlDeviceWaterMeter08BDailyNewData,
        SmpmUlDeviceWaterMeter08BInfoData,
    )


class SmpMWaterMeter12BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceWaterMeter12BDailyData,
    )


class SmpMWaterMeter16BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceWaterMeter16BDailyData,
    )


class SmpMHeatProxyMeter16BV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceHeatProxyMeter16BDailyData,
    )


class SmpMHeatGroupMeterV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceHeatGroupMeterDailyData,
        SmpmUlDeviceHeatGroupMeter56BDailyData,
    )


class SmpMInternalInfoDataV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmUlDeviceInternalInfoData,
    )


class SmpMDownlinkV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        SmpmDlDeviceEnergy8BGetDataData,
        SmpmDlDeviceEnergy8BSetClockData,
        SmpmDlDeviceEnergy8BSetRelayData,
        SmpmDlDeviceEnergy16BGetDataData,
        SmpmDlDeviceEnergy16BSetRegularDataSendingData,
    )
