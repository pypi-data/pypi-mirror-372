from typing import TypeVar, Type, Dict, Any

from data_aggregator_sdk.integration_message import IntegrationV0MessageMeta
from pydantic import BaseModel

T = TypeVar('T', bound='NeroBsPacket')


class NeroBsPacket(BaseModel):

    @classmethod
    def parse(cls: Type[T], data: Dict[str, Any], **kwargs: Any) -> T:
        raise NotImplementedError()

    def to_integration_meta(self, **kwargs: Any) -> IntegrationV0MessageMeta:
        raise NotImplementedError()
