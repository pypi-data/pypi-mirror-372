from datetime import datetime
from enum import Enum, unique
from typing import Any, Dict, Union

from data_aggregator_sdk.integration_message import IntegrationV0MessageMeta, IntegrationV0MessageMetaNbFiBS0, IntegrationV0MessageMetaBSChannelProtocol
from pydantic import field_validator

from data_gateway_sdk.errors import DataGatewayBSProtocolParsingError
from data_gateway_sdk.protocols.nero_bs_packet.nero_bs_packet import NeroBsPacket


@unique
class KafkaStationType(Enum):
    nero = 'nero'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class KafkaHeartbeatNeroBsPacket(NeroBsPacket):
    time: float
    latitude: float
    longitude: float
    station_id: int
    soft: str


class KafkaV0NeroBsPacket(NeroBsPacket):
    encrypted: bool = True
    freq_channel: int
    freq_expect: int
    message_id: int
    modem_id: int
    nbfi_f_ask: int = 0
    nbfi_iterator: int = 0
    nbfi_multi: int = 0
    nbfi_system: int = 0
    payload: str
    signal_rssi: int
    signal_snr: int
    station_id: int
    station_type: KafkaStationType = KafkaStationType.nero
    time_detected: int
    time_published: int
    ul_phy: int = 21

    @field_validator('nbfi_f_ask', 'nbfi_iterator', 'nbfi_multi', 'nbfi_system', mode="before")
    @classmethod
    def validate_nbfi_f_ask(cls, value: Union[int, None]) -> int:
        if value is None:
            return 0
        if not isinstance(value, int):
            raise ValueError(f'value must be int. "{type(value).__name__}" was given')
        return value

    @property
    def detected_dt(self) -> datetime:
        return datetime.fromtimestamp(self.time_detected)

    def to_integration_meta(self, **kwargs: Any) -> IntegrationV0MessageMeta:
        return IntegrationV0MessageMeta(
            nbfi_bs0=IntegrationV0MessageMetaNbFiBS0(
                station_id=self.station_id,
                modem_id=self.modem_id,
                encrypted=self.encrypted,
                freq_channel=self.freq_channel,
                freq_expect=self.freq_expect,
                message_id=self.message_id,
                nbfi_f_ask=self.nbfi_f_ask,
                nbfi_iterator=self.nbfi_iterator,
                nbfi_multi=self.nbfi_multi,
                nbfi_system=self.nbfi_system,
                signal_rssi=self.signal_rssi,
                signal_snr=self.signal_snr,
                time_detected=self.time_detected,
                time_published=self.time_published,
                ul_phy=self.ul_phy,
            ),
        )

    @property
    def payload_bytes(self) -> bytes:
        return bytes.fromhex(self.payload)

    @classmethod
    def parse(cls, data: Dict[str, Any], **kwargs: Any) -> 'KafkaV0NeroBsPacket':
        try:
            return KafkaV0NeroBsPacket(
                **data,
            )
        except Exception as e:  # noqa: B902
            raise DataGatewayBSProtocolParsingError('invalid payload', e)


@unique
class KafkaMessageType(Enum):
    unbp = 'unbp'
    nbfi = 'nbfi'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class KafkaV1NeroBsData(KafkaV0NeroBsPacket):
    baudrate: int = -1  # -1 for old protocols
    sdr: int = -1  # -1 for old protocols
    message_type: KafkaMessageType = KafkaMessageType.nbfi  # -1 for old protocols

    def to_integration_meta(self, **kwargs: Any) -> IntegrationV0MessageMeta:
        return IntegrationV0MessageMeta(
            nbfi_bs0=IntegrationV0MessageMetaNbFiBS0(
                station_id=self.station_id,
                modem_id=self.modem_id,
                encrypted=self.encrypted,
                freq_channel=self.freq_channel,
                freq_expect=self.freq_expect,
                message_id=self.message_id,
                nbfi_f_ask=self.nbfi_f_ask,
                nbfi_iterator=self.nbfi_iterator,
                nbfi_multi=self.nbfi_multi,
                nbfi_system=self.nbfi_system,
                signal_rssi=self.signal_rssi,
                signal_snr=self.signal_snr,
                time_detected=self.time_detected,
                time_published=self.time_published,
                ul_phy=self.ul_phy,
                baudrate=self.baudrate,
                sdr=self.sdr,
                message_type=IntegrationV0MessageMetaBSChannelProtocol(self.message_type.value),
            ),
        )

    @property
    def payload_bytes(self) -> bytes:
        return bytes.fromhex(self.payload)

    @classmethod
    def parse(cls, data: Dict[str, Any], **kwargs: Any) -> 'KafkaV1NeroBsData':
        try:
            return KafkaV1NeroBsData(
                **data,
            )
        except Exception as e:  # noqa: B902
            raise DataGatewayBSProtocolParsingError('invalid payload', e)
