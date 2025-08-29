from enum import Enum, unique
from typing import Any, List

from data_gateway_sdk.errors import DataGatewayDeviceProtocolParsingError
from data_gateway_sdk.protocols.device_packet.device_packet import DevicePacket
from data_gateway_sdk.protocols.device_packet.ncp_smp_device_packet import NcpSmpV0DevicePacket
from data_gateway_sdk.protocols.device_packet.smp_device_packet import SmpV0DevicePacket
from data_gateway_sdk.protocols.device_packet.smpm_device_packet import SmpMGasMeterV0DevicePacket, \
    SmpMEnergyMeterV0DevicePacket, SmpMJupiter08BV0DevicePacket, SmpMJupiter12BV0DevicePacket, \
    SmpMWaterMeter08BV0DevicePacket, SmpMWaterMeter12BV0DevicePacket, SmpMWaterMeter04BV0DevicePacket, \
    SmpMJupiter16BV0DevicePacket, SmpMWaterMeter16BV0DevicePacket, \
    SmpMInternalInfoDataV0DevicePacket, SmpMHeatProxyMeter16BV0DevicePacket, SmpMHeatGroupMeterV0DevicePacket, \
    SmpMEnergyMeterV1DevicePacket, SmpMDownlinkV0DevicePacket
from data_gateway_sdk.protocols.device_packet.water5_device_packet import Water5NeroV0DevicePacket, \
    Water5JupiterFreeScaleV0DevicePacket, Water5JupiterSTMV0DevicePacket, Water5FluoSTMV0DevicePacket, \
    Water5FluoFreeScaleV0DevicePacket, Water5FluoAV0DevicePacket, Water5GasV0DevicePacket, \
    Water5JupiterLoraV0DevicePacket, Water5FluoSV0DevicePacket


@unique
class DeviceProtocolApiType(Enum):
    ARVAS_API_V0 = 'ARVAS_API_V0'
    UNIVERSAL_API_V0 = 'UNIVERSAL_API_V0'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


DEVICE_PROTOCOL_API_TYPE_LIST = [device_protocol_api_type.value for device_protocol_api_type in DeviceProtocolApiType]


@unique
class DeviceProtocolType(Enum):  # DO NOT CHANGE VALUE because it should be compatible with data_aggregator_sdk db !!!
    WATER5_V_NERO_V0 = 'WATER5_V_NERO_V0'
    NCP_SMP_V0 = 'NCP_SMP_V0'  # only for jupiter NbIoT
    SMP_V0 = 'SMP_V0'  # only for jupiter NbIoT
    SMP_M_GAS_METER_V0 = 'SMP_M_GAS_METER_V0'
    SMP_M_ENERGY_METER_V0 = 'SMP_M_ENERGY_METER_V0'
    SMP_M_ENERGY_METER_V1 = 'SMP_M_ENERGY_METER_V1'
    SMP_M_JUPITER_08B_V0 = 'SMP_M_JUPITER_08B_V0'
    SMP_M_JUPITER_12B_V0 = 'SMP_M_JUPITER_12B_V0'
    SMP_M_JUPITER_16B_V0 = 'SMP_M_JUPITER_16B_V0'
    SMP_M_WATER_METER_04B_V0 = 'SMP_M_WATER_METER_04B_V0'
    SMP_M_WATER_METER_08B_V0 = 'SMP_M_WATER_METER_08B_V0'
    SMP_M_WATER_METER_12B_V0 = 'SMP_M_WATER_METER_12B_V0'
    SMP_M_WATER_METER_16B_V0 = 'SMP_M_WATER_METER_16B_V0'
    SMP_M_HEAT_PROXY_METER_16B_V0 = 'SMP_M_HEAT_PROXY_METER_16B_V0'
    SMP_M_HEAT_GROUP_METER_V0 = 'SMP_M_HEAT_GROUP_METER_V0'
    WATER5_V_JUPITER_FREESCALE_V0 = 'WATER5_V_JUPITER_FREESCALE_V0'
    WATER5_V_JUPITER_STM_V0 = 'WATER5_V_JUPITER_STM_V0'
    WATER5_V_FLUO_STM_V0 = 'WATER5_V_FLUO_STM_V0'
    WATER5_V_FLUO_FREESCALE_V0 = 'WATER5_V_FLUO_FREESCALE_V0'
    WATER5_V_FLUO_A_V0 = 'WATER5_V_FLUO_A_V0'
    WATER5_V_FLUO_S_V0 = 'WATER5_V_FLUO_S_V0'
    WATER5_V_GAS_V0 = 'WATER5_V_GAS_V0'
    WATER5_V_JUPITER_LORA_V0 = 'WATER5_V_JUPITER_LORA_V0'
    WATER5_V_FLUO_LORA_V0 = 'WATER5_V_FLUO_LORA_V0'
    SMP_M_INTERNAL_INFO_DATA = 'SMP_M_INTERNAL_INFO_DATA'
    SMP_M_DOWNLINK_V0 = 'SMP_M_DOWNLINK_V0'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def parse(self, payload: bytes, **kwargs: Any) -> List[DevicePacket]:
        assert isinstance(payload, bytes), f'payload must be type of {bytes}, got type {type(payload)}'
        try:
            return DEVICE_PROTOCOL_MAP[self].parse(payload, **kwargs)  # type: ignore
        except DataGatewayDeviceProtocolParsingError:
            raise
        except Exception as e:  # noqa: B902
            raise DataGatewayDeviceProtocolParsingError(f'{self.value}: invalid payload', e)


DEVICE_PROTOCOL_MAP = {
    DeviceProtocolType.WATER5_V_NERO_V0: Water5NeroV0DevicePacket,
    DeviceProtocolType.NCP_SMP_V0: NcpSmpV0DevicePacket,
    DeviceProtocolType.SMP_V0: SmpV0DevicePacket,
    DeviceProtocolType.SMP_M_GAS_METER_V0: SmpMGasMeterV0DevicePacket,
    DeviceProtocolType.SMP_M_ENERGY_METER_V0: SmpMEnergyMeterV0DevicePacket,
    DeviceProtocolType.SMP_M_ENERGY_METER_V1: SmpMEnergyMeterV1DevicePacket,
    DeviceProtocolType.SMP_M_JUPITER_08B_V0: SmpMJupiter08BV0DevicePacket,
    DeviceProtocolType.SMP_M_JUPITER_12B_V0: SmpMJupiter12BV0DevicePacket,
    DeviceProtocolType.SMP_M_JUPITER_16B_V0: SmpMJupiter16BV0DevicePacket,
    DeviceProtocolType.SMP_M_WATER_METER_04B_V0: SmpMWaterMeter04BV0DevicePacket,
    DeviceProtocolType.SMP_M_WATER_METER_08B_V0: SmpMWaterMeter08BV0DevicePacket,
    DeviceProtocolType.SMP_M_WATER_METER_12B_V0: SmpMWaterMeter12BV0DevicePacket,
    DeviceProtocolType.SMP_M_WATER_METER_16B_V0: SmpMWaterMeter16BV0DevicePacket,

    DeviceProtocolType.SMP_M_HEAT_PROXY_METER_16B_V0: SmpMHeatProxyMeter16BV0DevicePacket,
    DeviceProtocolType.SMP_M_HEAT_GROUP_METER_V0: SmpMHeatGroupMeterV0DevicePacket,

    DeviceProtocolType.WATER5_V_JUPITER_FREESCALE_V0: Water5JupiterFreeScaleV0DevicePacket,
    DeviceProtocolType.WATER5_V_JUPITER_STM_V0: Water5JupiterSTMV0DevicePacket,
    DeviceProtocolType.WATER5_V_FLUO_STM_V0: Water5FluoSTMV0DevicePacket,
    DeviceProtocolType.WATER5_V_FLUO_FREESCALE_V0: Water5FluoFreeScaleV0DevicePacket,
    DeviceProtocolType.WATER5_V_FLUO_A_V0: Water5FluoAV0DevicePacket,
    DeviceProtocolType.WATER5_V_FLUO_S_V0: Water5FluoSV0DevicePacket,
    DeviceProtocolType.WATER5_V_GAS_V0: Water5GasV0DevicePacket,

    DeviceProtocolType.WATER5_V_JUPITER_LORA_V0: Water5JupiterLoraV0DevicePacket,
    DeviceProtocolType.WATER5_V_FLUO_LORA_V0: Water5JupiterLoraV0DevicePacket,

    DeviceProtocolType.SMP_M_INTERNAL_INFO_DATA: SmpMInternalInfoDataV0DevicePacket,

    DeviceProtocolType.SMP_M_DOWNLINK_V0: SmpMDownlinkV0DevicePacket,
}

assert set(DEVICE_PROTOCOL_MAP.keys()) == set(DeviceProtocolType)
