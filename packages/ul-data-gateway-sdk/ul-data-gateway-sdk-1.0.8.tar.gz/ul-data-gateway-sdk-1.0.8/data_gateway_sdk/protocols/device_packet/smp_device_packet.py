from datetime import datetime, tzinfo
from decimal import Decimal
from typing import Any, List

from data_aggregator_sdk.constants.enums import SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageConsumption, CounterType, ResourceType, \
    IntegrationV0MessageSensor
from pydantic import BaseModel
from pysmp import decode_getset as smp_getset  # type: ignore

from data_gateway_sdk.errors import DataGatewayDeviceProtocolParsingError
from data_gateway_sdk.protocols.device_packet.device_packet import DevicePacket


class SmpDaily(BaseModel):
    info_id_code: int
    sdata_count_ch1_code: int
    sdata_count_ch2_code: int
    sdata_temperature_code: int
    sdata_battery_code: float
    sdata_datetime_code: datetime


class SmpV0DevicePacket(DevicePacket):
    packet: SmpDaily

    @classmethod
    def parse(cls, payload: bytes, **kwargs: Any) -> List['SmpV0DevicePacket']:
        try:
            return [SmpV0DevicePacket(
                packet=SmpDaily(
                    **{cmd.name.replace('SMP_', '').lower(): (val.value.isoformat() if isinstance(val.value, datetime) else val.value) for cmd, val in smp_getset(payload)},  # type: ignore
                ),
            )]
        except Exception as e:  # noqa: B902
            raise DataGatewayDeviceProtocolParsingError(f'invalid payload {payload.hex()}', e)

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                sensors=[
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.packet.sdata_battery_code)),
                        sensor_type=SensorType.BATTERY,
                    ),
                    IntegrationV0MessageSensor(
                        value=Decimal(str(self.packet.sdata_temperature_code)),
                        sensor_type=SensorType.TEMPERATURE,
                    ),
                ],
                consumption=[
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=1,
                        value=Decimal(str(self.packet.sdata_count_ch1_code)),
                        overloading_value=None,
                    ),
                    IntegrationV0MessageConsumption(
                        counter_type=CounterType.COMMON,
                        resource_type=ResourceType.COMMON,
                        channel=2,
                        value=Decimal(str(self.packet.sdata_count_ch2_code)),
                        overloading_value=None,
                    ),
                ],
            ),
        ]
