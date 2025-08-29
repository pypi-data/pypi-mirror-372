from enum import Enum, unique
from typing import Dict, Any

from data_gateway_sdk.errors import DataGatewayBSProtocolParsingError
from data_gateway_sdk.protocols.nero_bs_packet.http_nero_bs_packet import HttpV0NeroBsPacket
from data_gateway_sdk.protocols.nero_bs_packet.kafka_nero_bs_packet import KafkaV0NeroBsPacket, KafkaV1NeroBsData, KafkaHeartbeatNeroBsPacket
from data_gateway_sdk.protocols.nero_bs_packet.nero_bs_packet import NeroBsPacket


@unique
class NeroBsProtocolType(Enum):  # DO NOT CHANGE VALUE because it should be compatible with data_aggregator_sdk db
    NERO_BS_KAFKA_SYS_V0 = 'NERO_BS_KAFKA_SYS_V0'
    NERO_BS_KAFKA_V0 = 'NERO_BS_KAFKA_V0'
    NERO_BS_KAFKA_V1 = 'NERO_BS_KAFKA_V1'
    NERO_BS_HTTP_V0 = 'NERO_BS_HTTP_V0'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def parse(self, payload: Dict[str, Any], **kwargs: Any) -> NeroBsPacket:
        assert isinstance(payload, dict), f'payload must be type of {dict}, got type {type(payload)}'
        try:
            return BS_PROTOCOLS_MAP[self].parse(payload, **kwargs)  # type: ignore
        except DataGatewayBSProtocolParsingError:
            raise
        except Exception as e:  # noqa: B902
            raise DataGatewayBSProtocolParsingError(f'{self.value}: invalid payload', e)


BS_PROTOCOLS_MAP = {
    NeroBsProtocolType.NERO_BS_HTTP_V0: HttpV0NeroBsPacket,
    NeroBsProtocolType.NERO_BS_KAFKA_V0: KafkaV0NeroBsPacket,
    NeroBsProtocolType.NERO_BS_KAFKA_V1: KafkaV1NeroBsData,
    NeroBsProtocolType.NERO_BS_KAFKA_SYS_V0: KafkaHeartbeatNeroBsPacket,
}

assert set(BS_PROTOCOLS_MAP.keys()) == set(NeroBsProtocolType)
