from datetime import datetime, tzinfo
from typing import Tuple, TypeVar, Type, List, Any

from data_aggregator_sdk.integration_message import IntegrationV0MessageData
from pydantic import BaseModel

from data_gateway_sdk.utils.buf_ref import BufRef

T = TypeVar('T', bound='Packet')


class Packet(BaseModel):
    @classmethod
    def parse(cls: Type[T], buf: BufRef) -> T:
        raise NotImplementedError()

    def serialize(self) -> bytes:
        raise NotImplementedError()

    def to_integration_data(self, *, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        raise NotImplementedError()

    @staticmethod
    def parse_packets(payload: bytes, pack_types: Tuple[Type[T], ...]) -> List[T]:
        result: List[T] = []
        while True:
            prev_res_len = len(result)
            for pack_type in pack_types:
                try:
                    buf = BufRef(payload)
                    result.append(pack_type.parse(buf))
                    payload = buf.get_last_bytes()
                    break
                except ValueError:
                    continue
            if prev_res_len == len(result):
                return []
            if len(payload) == 0:
                break
            if all(not i for i in payload):
                break
        return result
