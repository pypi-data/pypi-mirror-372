from typing import Tuple, Type

from data_gateway_sdk.protocols.device_packet.device_packet import DevicePacketTyped
from data_gateway_sdk.protocols.water5_v_nero.water5_device_cold_reset import Water5DeviceColdResetData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_daily import Water5DeviceDailyData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_info_ch1 import Water5DeviceInfoCh1Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_info_ch2 import Water5DeviceInfoCh2Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_magnet import Water5DeviceMagnetData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_fluo_a import Water5DeviceWarmResetVFluoAData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_fluo_freescale import Water5DeviceWarmResetVFluoFreescaleData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_fluo_stm import Water5DeviceWarmResetVFluoStmData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_jupiter_freescale import Water5DeviceWarmResetVJupiterFreescaleData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_jupiter_stm import Water5DeviceWarmResetVJupiterStmData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_warm_reset_v_metano_a import \
    Water5DeviceWarmResetVMetanoAData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch1 import Water5DeviceWeeklyCh1Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch1_impulse import Water5DeviceWeeklyCh1ImpulseData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch1_impulse_v2 import Water5DeviceWeeklyCh1ImpulseV2Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch2 import Water5DeviceWeeklyCh2Data
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch2_impulse import Water5DeviceWeeklyCh2ImpulseData
from data_gateway_sdk.protocols.water5_v_nero.water5_device_weekly_ch2_impulse_v2 import Water5DeviceWeeklyCh2ImpulseV2Data
from data_gateway_sdk.utils.packet import Packet


class Water5NeroV0DevicePacket(DevicePacketTyped):
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceDailyData,
        Water5DeviceWeeklyCh1Data,
        Water5DeviceWeeklyCh2Data,
        Water5DeviceInfoCh1Data,
        Water5DeviceInfoCh2Data,
        Water5DeviceMagnetData,
        Water5DeviceColdResetData,
    )


class Water5GasV0DevicePacket(DevicePacketTyped):
    # MM215. DAILY, WEEKLY, INFO, WARM_RESET
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWarmResetVMetanoAData,
        Water5DeviceDailyData,
        Water5DeviceWeeklyCh1Data,
        Water5DeviceInfoCh1Data,
    )


class Water5FluoAV0DevicePacket(DevicePacketTyped):
    # MM217. WEEKLY, INFO, COLD_RESET, WARM_RESET
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWeeklyCh1Data,
        Water5DeviceInfoCh1Data,
        Water5DeviceColdResetData,
        Water5DeviceWarmResetVFluoAData,
    )


class Water5FluoSV0DevicePacket(DevicePacketTyped):
    # MM217. WEEKLY, INFO, COLD_RESET, WARM_RESET
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceDailyData,
        Water5DeviceWeeklyCh1Data,
        Water5DeviceColdResetData,
    )


class Water5FluoFreeScaleV0DevicePacket(DevicePacketTyped):
    # MM214. CH1. WEEKLY, INFO, COLD_RESET, WARM_RESET, COMMAND
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceDailyData,
        Water5DeviceWeeklyCh1Data,
        Water5DeviceInfoCh1Data,
        Water5DeviceMagnetData,
        Water5DeviceWarmResetVFluoFreescaleData,
    )  # noqa: E501


class Water5FluoLoraV0DevicePacket(DevicePacketTyped):  #
    # FLUO LORA. MM224. CH_1 - прямой, СH_2 - обратный. WEEKLY
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWeeklyCh1Data,
        Water5DeviceWeeklyCh2Data,
    )


class Water5JupiterLoraV0DevicePacket(DevicePacketTyped):  #
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWeeklyCh1ImpulseData,
        Water5DeviceWeeklyCh2ImpulseData,
    )
    # JUPITER LORA. MM216. CH_1 - прямой, СH_2 - обратный. WEEKLY.  АБСОЛЮТНО ТАКОЙ ЖЕ КАК И FLUO LORA (MM224)


class Water5FluoSTMV0DevicePacket(DevicePacketTyped):
    # FLUO STM. MM223 - huashun, MM222 - vnlink. WEEKLY, INFO, COMMAND, WARM_RESET
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWeeklyCh1Data,
        Water5DeviceInfoCh1Data,
        Water5DeviceMagnetData,
        Water5DeviceWarmResetVFluoStmData,
    )


class Water5JupiterSTMV0DevicePacket(DevicePacketTyped):
    # Jupiter STM. MM212. CH_1, СH_2. WEEKLY, WARM_RESET
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWeeklyCh1ImpulseData,
        Water5DeviceWeeklyCh2ImpulseData,
        Water5DeviceWarmResetVJupiterStmData,
    )


class Water5JupiterFreeScaleV0DevicePacket(DevicePacketTyped):
    # Jupiter Free Scale. MM212, CH_1, СH_2, WEEKLY, WARM_RESET, 24 bits
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = (
        Water5DeviceWeeklyCh1ImpulseV2Data,
        Water5DeviceWeeklyCh2ImpulseV2Data,
        Water5DeviceWarmResetVJupiterFreescaleData,
    )
