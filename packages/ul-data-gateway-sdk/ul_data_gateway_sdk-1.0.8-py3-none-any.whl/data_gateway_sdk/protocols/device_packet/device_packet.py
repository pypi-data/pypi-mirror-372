from datetime import datetime, tzinfo
from typing import Type, Any, TypeVar, Tuple, List

from data_aggregator_sdk.integration_message import IntegrationV0MessageData
from pydantic import BaseModel, PrivateAttr
from ul_api_utils.conf import APPLICATION_F

from data_gateway_sdk.errors import DataGatewayDeviceProtocolParsingError
from data_gateway_sdk.utils.packet import Packet

T = TypeVar('T')


class DevicePacket(BaseModel):
    @classmethod
    def parse(cls: Type[T], payload: bytes, **kwargs: Any) -> List[T]:
        raise NotImplementedError()

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        raise NotImplementedError()


TClass = TypeVar('TClass', bound='DevicePacketTyped')


class DevicePacketTyped(BaseModel):
    packet: Packet
    _SUPPORTED_PACKETS: Tuple[Type[Packet], ...] = PrivateAttr(default=())

    @classmethod
    def parse(cls: Type[TClass], payload: bytes, **kwargs: Any) -> List[TClass]:
        supported_packets = cls.__private_attributes__["_SUPPORTED_PACKETS"].default    # pydanticV2 migration https://docs.pydantic.dev/latest/concepts/models/#private-model-attributes
        if not APPLICATION_F.has_or_unset(cls.__name__):
            raise DataGatewayDeviceProtocolParsingError(f'payload "{payload.hex()}" not matched with ({", ".join(c.__name__ for c in supported_packets)})')  # type: ignore
        parsed_packets = Packet.parse_packets(payload, supported_packets)  # type: ignore
        if not parsed_packets:
            raise DataGatewayDeviceProtocolParsingError(
                f'payload "{payload.hex()}" not matched with ({", ".join(c.__name__ for c in supported_packets)})')  # type: ignore

        return [cls(packet=parsed_packet) for parsed_packet in parsed_packets]

    def to_integration_data(self, *, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return self.packet.to_integration_data(received_at=received_at, device_tz=device_tz, **kwargs)


class EmptyDevicePacket(DevicePacket):
    @classmethod
    def parse(cls: Type[T], payload: bytes, **kwargs: Any) -> List[T]:
        raise TypeError(f'{cls.__name__} not supported parse message')

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
            ),
        ]
