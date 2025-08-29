import base64
import json
from datetime import datetime, timedelta, timezone
from enum import Enum, unique
from itertools import groupby
from typing import Callable, Optional, List, Dict, Tuple, Set, Union, NamedTuple, Mapping, Any
from uuid import UUID
from zoneinfo import ZoneInfo

import pytz
from data_aggregator_sdk.constants.enums import NetworkTypeEnum, NetworkSysTypeEnum, EncryptionType as DaEncryptionType, \
    IntegrationV0MessageErrorType, DeviceHack
from data_aggregator_sdk.data_aggregator_api_sdk import DeviceData as DADeviceData, ApiDataGatewayNetworkDevice, \
    DataAggregatorApiSdk
from data_aggregator_sdk.errors import DataAggregatorRequestError, DataAggregatorResponseError
from data_aggregator_sdk.integration_message import IntegrationV0MessageMeta, IntegrationV0MessageGateway, \
    IntegrationV0MessageData, IntegrationV0MessageError
from data_aggregator_sdk.types.get_data_gateway_network_device_list import ApiDataGatewaysNetworkResponse
from pydantic import BaseModel
from timezonefinder import TimezoneFinder
from ul_api_utils.utils.json_encoder import CustomJSONEncoder
from ul_unipipeline.message.uni_message import UniMessage
from ul_unipipeline.worker.uni_worker import UniWorker

from data_gateway_sdk.device_data_encryption import EncryptionType
from data_gateway_sdk.device_data_protocol import DeviceProtocolType
from data_gateway_sdk.errors import DataGatewayDeviceProtocolParsingError
from data_gateway_sdk.protocols.device_packet.device_packet import DevicePacket
from data_gateway_sdk.protocols.nero_bs_packet.http_nero_bs_packet import BaseStationInfoGeo
from src.conf.self_logging import self_logging

logger = self_logging.getLogger(__name__)


class DataGatewayNetwork(NamedTuple):
    id: UUID
    name: str
    type_network: NetworkTypeEnum
    sys_type: NetworkSysTypeEnum
    specifier: Optional[str]
    params: Optional[Dict[str, Any]]


class OutputMessage(UniMessage):
    data: IntegrationV0MessageGateway
    specifier: str
    params: Dict[str, Any]


class OutputListMessage(UniMessage):
    messages: List[OutputMessage]


class DeviceDataStructSendingRecipe(NamedTuple):
    net_sys_type: NetworkSysTypeEnum
    network: Optional[DataGatewayNetwork | ApiDataGatewaysNetworkResponse]
    message: IntegrationV0MessageGateway


class PayloadInfo(BaseModel):
    encrypted_payload: Optional[str] = ''
    decrypted_payload: Optional[str] = ''
    encryption_type: Optional[EncryptionType] = None


ALL_SUPPORTED_OUTPUT_NETWORK_TYPES = {
    NetworkSysTypeEnum.OUTPUT_NEW_LK,
    NetworkSysTypeEnum.OUTPUT_DATA_AGGREGATOR_DEVICE_DATA,
    NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA,
}


ALL_SUPPORTED_OUTPUT_NETWORK_TYPES_BATCH = {
    (NetworkSysTypeEnum.OUTPUT_NEW_LK, ''),
    (NetworkSysTypeEnum.OUTPUT_NEW_LK, 'repeater_to_dev__batch'),
    (NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA, ''),
    (NetworkSysTypeEnum.OUTPUT_DATA_AGGREGATOR_DEVICE_DATA, ''),
}


class DeviceDataStruct(NamedTuple):
    """
    Data structure of payload, packets and sending recipes for workers

    Attributes
    ----------
    payload : PayloadInfo
        data structure of payload for workers
    sending_recipes : List[DeviceDataStructSendingRecipe]
        array of data structures of sending recipes for workers
    device_packets : List[DevicePacket]
        array of data structures of packets for workers

    Methods
    -------
    send(sending_map: Mapping[NetworkSysTypeEnum, Callable[[UniWorker, OutputMessage], None]], self_worker: Optional[UniWorker] = None) -> None:
        Preparation of sending recipes for workers
        Filtering recipes for OUTPUT_DATA_LOGGER_DEVICE_DATA which must be sent with empty 'specifier' and 'params'
    """
    payload: PayloadInfo
    sending_recipes: List[DeviceDataStructSendingRecipe]
    device_packets: List[DevicePacket]

    def send(
        self,
        sending_map: Mapping[NetworkSysTypeEnum, Callable[[Optional[UniWorker[UniMessage, None]], OutputMessage], None]],
        *,
        self_worker: Optional[UniWorker[UniMessage, None]] = None,
    ) -> None:
        """
        This method preparing sending recipes for workers and send them to worker which defined by 'sending_map' param.

        Parameters
        ----------
        sending_map : Mapping[NetworkSysTypeEnum, Callable[[Optional[UniWorker[UniMessage, None]], OutputMessage], None]]
            Sending map for identifying of worker name to whom must be sent the message
        self_worker : Optional[UniWorker[UniMessage, None]] = None
            Worker object (Optional)

        Returns
        -------
        None
        """
        assert set(sending_map.keys()) <= ALL_SUPPORTED_OUTPUT_NETWORK_TYPES
        for recipe in self.sending_recipes:
            if recipe.net_sys_type is not NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA and recipe.net_sys_type in sending_map:
                assert recipe.network is not None
                sending_map[recipe.net_sys_type](
                    self_worker,
                    OutputMessage(
                        data=recipe.message,
                        specifier=recipe.network.specifier or '',
                        params=recipe.network.params or {},
                    ),
                )
            else:
                sending_map[NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA](
                    self_worker,
                    OutputMessage(
                        data=recipe.message,
                        specifier='',
                        params={},
                    ),
                )


class DeviceDataStructBatch(NamedTuple):
    """
    Data structure which contains array of other data structures of payloads, packets and sending recipes for workers

    Attributes
    ----------
    messages : List[DeviceDataStruct]
        array of data structures of payloads, packets and sending recipes for workers

    Methods
    -------
    send(self_worker: UniWorker, sending_map: Mapping[NetworkSysTypeEnum, Callable[[UniWorker, OutputMessage | List[OutputMessage]], None]]) -> None:
        Preparation of sending recipes for workers
        Filtering recipes for OUTPUT_DATA_AGGREGATOR_DEVICE_DATA and storing it to other array for sending batch of [OutputMessage]
    """
    messages: List[DeviceDataStruct]

    def send(
        self,
        sending_map: Mapping[NetworkSysTypeEnum, Callable[[Optional[UniWorker[UniMessage, None]], OutputMessage | List[OutputMessage]], None]],
        *,
        self_worker: Optional[UniWorker[UniMessage, None]] = None,
    ) -> None:
        """
        This method preparing sending recipes for workers and send them to worker which defined by 'sending_map' param.

        If network is OUTPUT_DATA_AGGREGATOR_DEVICE_DATA then put recipe to other array to send them all to batch worker
            in other case it uses usual filtering from DeviceDataStruct.send method

        Parameters
        ----------
        sending_map : Mapping[NetworkSysTypeEnum, Callable[[Optional[UniWorker[UniMessage, None]], OutputMessage | List[OutputMessage]], None]]
            Sending map for identifying of worker name to whom must be sent the message
        self_worker : Optional[UniWorker[UniMessage, None]] = None
            Worker object (Optional)

        Returns
        -------
        None
        """
        if set(sending_map.keys()) > ALL_SUPPORTED_OUTPUT_NETWORK_TYPES_BATCH:
            logger.error('Sending map keys are not equal to SUPPORTED NETWORK TYPES! :: skip')
            return
        da_output_batch: List[OutputMessage] = []
        new_lk_output_batch: List[OutputMessage] = []
        for message in self.messages:
            for recipe in message.sending_recipes:
                if recipe.net_sys_type is NetworkSysTypeEnum.OUTPUT_DATA_AGGREGATOR_DEVICE_DATA:
                    da_output_batch.append(OutputMessage(
                        data=recipe.message,
                        specifier=recipe.network.specifier or '',  # type: ignore
                        params=recipe.network.params or {},  # type: ignore
                    ))
                elif recipe.net_sys_type is NetworkSysTypeEnum.OUTPUT_NEW_LK:
                    new_lk_output_batch.append(OutputMessage(
                        data=recipe.message,
                        specifier=recipe.network.specifier or '',  # type: ignore
                        params=recipe.network.params or {},  # type: ignore
                    ))
                else:
                    if recipe.net_sys_type is not NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA and recipe.net_sys_type in sending_map:
                        assert recipe.network is not None
                        sending_map[recipe.net_sys_type](
                            self_worker,
                            OutputMessage(
                                data=recipe.message,
                                specifier=recipe.network.specifier or '',
                                params=recipe.network.params or {},
                            ),
                        )
                    else:
                        sending_map[NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA](
                            self_worker,
                            OutputMessage(
                                data=recipe.message,
                                specifier='',
                                params={},
                            ),
                        )

        if da_output_batch and NetworkSysTypeEnum.OUTPUT_DATA_AGGREGATOR_DEVICE_DATA in sending_map:
            logger.info(f'recipes output DA: {da_output_batch}')
            sending_map[NetworkSysTypeEnum.OUTPUT_DATA_AGGREGATOR_DEVICE_DATA](self_worker, da_output_batch)
        if new_lk_output_batch and NetworkSysTypeEnum.OUTPUT_NEW_LK in sending_map:
            logger.info(f'recipes output NEW_LK: {new_lk_output_batch}')
            grouper_params = lambda obj: json.dumps(obj.params)  # noqa: E731
            sorted_payload_by_params = sorted(new_lk_output_batch, key=grouper_params)
            for key_params, sorted_messages in groupby(sorted_payload_by_params, key=grouper_params):
                logger.info(f'recipes output NEW_LK with params: {key_params} :: {sorted_messages}')
                sending_map[NetworkSysTypeEnum.OUTPUT_NEW_LK](self_worker, list(sorted_messages))


class DeviceDataManager(NamedTuple):
    raw_mac: int
    rewritten_mac: int
    kind: 'DeviceDataManagerKind'
    gateway_id: UUID
    current_network: DataGatewayNetwork
    send_always_to_data_logger: bool
    device_data: Optional[DADeviceData]
    current_net_rel: Optional[ApiDataGatewayNetworkDevice]
    default_networks: List[DataGatewayNetwork] = []
    error: IntegrationV0MessageError = IntegrationV0MessageError()

    def make_struct_batch(
        self,
        *,
        payload: List[IntegrationV0MessageGateway],
    ) -> DeviceDataStructBatch:
        device_pack: List[DevicePacket] = []
        messages_batch: List[DeviceDataStruct] = []
        decrypted_payload_hex: str
        logger.info(f'payload type: list of {type(payload[0]).__name__}' if payload else 'payload type: empty list')
        base_messages: List[IntegrationV0MessageGateway] = payload.copy()
        logger.info('payload was copied from input')

        for base_message in base_messages:
            decrypted_payload_hex = base_message.decrypted_payload
            encryption_type = None
            sending_recipes: List[DeviceDataStructSendingRecipe] = []
            payload_str = base_message.raw_payload
            if payload_str != '':
                encryption_type = None
                decrypted_payload = bytes([])
                payload_item = bytes.fromhex(payload_str)
                capture_dt = base_message.date_created

                if self.device_data is not None:
                    assert self.current_net_rel is not None  # only for mypy
                    if self.kind is DeviceDataManagerKind.UPLINK:
                        encryption_type = EncryptionType(self.current_net_rel.uplink_encryption_type.value)
                        key = base64.b64decode(self.current_net_rel.uplink_encryption_key) if self.current_net_rel.uplink_encryption_key else b''
                    else:
                        encryption_type = EncryptionType(self.current_net_rel.downlink_encryption_type.value)
                        key = base64.b64decode(self.current_net_rel.downlink_encryption_key) if self.current_net_rel.downlink_encryption_key else b''
                    try:
                        decrypted_payload = encryption_type.decrypt(payload_item, key)
                        logger.info('payload decrypted')
                    except Exception as e:  # noqa: B902
                        self.error.error_message = str(e)
                        self.error.error_type = IntegrationV0MessageErrorType.data_undecryptable
                        logger.warning(f'payload decryption error :: {e}')
                    else:
                        try:
                            device_pack = DeviceProtocolType(self.current_net_rel.protocol.type.value).parse(decrypted_payload)
                            logger.info('payload parsed')
                        except DataGatewayDeviceProtocolParsingError as e:
                            self.error.error_message = str(e)
                            self.error.error_type = IntegrationV0MessageErrorType.data_unparsable
                            logger.warning(f'payload parsing error {e}')

                decrypted_payload_hex = decrypted_payload.hex()
                server_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                if capture_dt.tzinfo:
                    capture_dt = capture_dt.astimezone(timezone.utc).replace(tzinfo=timezone.utc)
                else:
                    capture_dt = capture_dt.replace(tzinfo=timezone.utc)
                if capture_dt > (server_time + timedelta(minutes=2)):
                    self.error.error_message = f'Message time is in future {capture_dt}, server time {server_time}'
                    self.error.error_type = IntegrationV0MessageErrorType.packet_from_the_future
                elif capture_dt < (server_time - timedelta(days=365)):
                    self.error.error_message = f'Message time is older than 1 year from now {capture_dt}, server time {server_time}'
                    self.error.error_type = IntegrationV0MessageErrorType.packet_from_the_past
                hacks: List[DeviceHack] = []
                device_tz = pytz.timezone('UTC')
                if self.device_data is not None:
                    hacks = getattr(self.device_data, 'hacks', [])
                    if self.device_data.device_tz is not None:
                        device_tz = pytz.timezone(self.device_data.device_tz)

                integration_message_datas: List[Tuple[IntegrationV0MessageData, str]] = [
                    (
                        integration_mes,
                        type(pack.packet).__name__,  # type: ignore
                    ) for pack in device_pack for integration_mes in pack.to_integration_data(
                        received_at=capture_dt,
                        device_tz=device_tz,
                        hacks=hacks,
                    )]
                if not integration_message_datas:
                    integration_message_datas = [(IntegrationV0MessageData(dt=capture_dt), 'EmptyDevicePacket')]

                parsed_base_messages = [IntegrationV0MessageGateway(
                    date_created=capture_dt,
                    data=integration_message_data,
                    meta=base_message.meta,
                    packet_type_name=packet_type_name,
                    id=base_message.id,
                    device_mac=self.rewritten_mac,
                    raw_payload=payload_str,
                    decrypted_payload=decrypted_payload_hex,
                    device_raw_mac=self.raw_mac,
                    protocol_name=self.current_net_rel.protocol.name if self.current_net_rel else None,
                    protocol_type=self.current_net_rel.protocol.type if self.current_net_rel else None,
                    raw_message=json.dumps(base_message, cls=CustomJSONEncoder),
                    gateway_id=self.gateway_id,
                    network_id=self.current_network.id,
                    network_sys_type=self.current_network.sys_type,
                    device_id=self.current_net_rel.device_id if self.current_net_rel else None,
                    protocol_id=self.current_net_rel.protocol.id if self.current_net_rel else None,
                    verified_device=self.device_data is not None,
                    dt_calculated=True if capture_dt != integration_message_data.dt else False,
                    error=self.error,
                ) for integration_message_data, packet_type_name in integration_message_datas]

                if self.send_always_to_data_logger:
                    for parsed_base_message in parsed_base_messages:
                        sending_recipes.append(DeviceDataStructSendingRecipe(
                            network=None,
                            message=parsed_base_message.model_copy(),
                            net_sys_type=NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA,
                        ))
                if self.device_data:
                    for net_rel in self.device_data.all_data_gateway_networks:  # TODO: data-aggregator setting for sending for repeater
                        if net_rel.network.type_network is not NetworkTypeEnum.output:
                            continue

                        if net_rel.network.sys_type not in ALL_SUPPORTED_OUTPUT_NETWORK_TYPES:
                            continue

                        if self.send_always_to_data_logger and net_rel.network.sys_type is NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA:
                            continue

                        for parsed_base_message in parsed_base_messages:
                            message = parsed_base_message.model_copy()
                            message.device_mac = net_rel.mac
                            message.device_id = net_rel.device_id

                            sending_recipes.append(DeviceDataStructSendingRecipe(
                                network=net_rel.network,
                                message=message,
                                net_sys_type=net_rel.network.sys_type,
                            ))
                else:
                    for net in self.default_networks:
                        for parsed_base_message in parsed_base_messages:
                            sending_recipes.append(DeviceDataStructSendingRecipe(
                                network=net,
                                message=parsed_base_message.model_copy(),
                                net_sys_type=net.sys_type,
                            ))

                messages_batch.append(DeviceDataStruct(
                    sending_recipes=sending_recipes,
                    payload=PayloadInfo(encrypted_payload=payload_str, decrypted_payload=decrypted_payload_hex or None, encryption_type=encryption_type),
                    device_packets=device_pack,
                ))
            else:
                if self.send_always_to_data_logger:
                    sending_recipes.append(DeviceDataStructSendingRecipe(
                        network=None,
                        message=base_message.model_copy(),
                        net_sys_type=NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA,
                    ))
                if self.device_data:
                    for net_rel in self.device_data.all_data_gateway_networks:  # TODO: data-aggregator setting for sending for repeater
                        if net_rel.network.type_network is not NetworkTypeEnum.output:
                            continue

                        if net_rel.network.sys_type not in ALL_SUPPORTED_OUTPUT_NETWORK_TYPES:
                            continue

                        if self.send_always_to_data_logger and net_rel.network.sys_type is NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA:
                            continue

                        message = base_message.model_copy()
                        message.device_mac = net_rel.mac
                        message.device_id = net_rel.device_id

                        sending_recipes.append(DeviceDataStructSendingRecipe(
                            network=net_rel.network,
                            message=message,
                            net_sys_type=net_rel.network.sys_type,
                        ))
                else:
                    for net in self.default_networks:
                        sending_recipes.append(DeviceDataStructSendingRecipe(
                            network=net,
                            message=base_message.model_copy(),
                            net_sys_type=net.sys_type,
                        ))

                messages_batch.append(DeviceDataStruct(
                    sending_recipes=sending_recipes,
                    payload=PayloadInfo(encrypted_payload=payload_str, decrypted_payload=decrypted_payload_hex or None, encryption_type=encryption_type),
                    device_packets=device_pack,
                ))

        return DeviceDataStructBatch(
            messages=messages_batch,
        )

    def make_struct(
        self,
        *,
        payload: Union[bytes, IntegrationV0MessageGateway],
        capture_dt: datetime,
        meta: IntegrationV0MessageMeta,
        raw: str,
        message_id: Optional[UUID],
        bs_geo: Optional[BaseStationInfoGeo] = None,
    ) -> DeviceDataStruct:
        device_pack: List[DevicePacket] = []
        base_messages = []
        logger.info(f'payload type of {type(payload)}')
        if isinstance(payload, IntegrationV0MessageGateway):
            base_message = payload.model_copy()
            base_message.meta = meta
            base_message.error = self.error
            base_messages.append(base_message)
            decrypted_payload_hex = payload.decrypted_payload
            encryption_type = None
            payload_str = payload.raw_payload
            logger.info('payload was copied from input')
        else:
            encryption_type = None
            decrypted_payload = bytes([])
            if self.device_data is not None:
                assert self.current_net_rel is not None  # only for mypy
                if self.kind is DeviceDataManagerKind.UPLINK:
                    encryption_type = EncryptionType(self.current_net_rel.uplink_encryption_type.value)
                    key = base64.b64decode(self.current_net_rel.uplink_encryption_key) if self.current_net_rel.uplink_encryption_key else b''
                else:
                    encryption_type = EncryptionType(self.current_net_rel.downlink_encryption_type.value)
                    key = base64.b64decode(self.current_net_rel.downlink_encryption_key) if self.current_net_rel.downlink_encryption_key else b''
                try:
                    decrypted_payload = encryption_type.decrypt(payload, key)
                    logger.info('payload decrypted')
                except Exception as e:  # noqa: B902
                    self.error.error_message = str(e)
                    self.error.error_type = IntegrationV0MessageErrorType.data_undecryptable
                    logger.warning(f'payload decryption error :: {e}')
                else:
                    try:
                        device_pack = DeviceProtocolType(self.current_net_rel.protocol.type.value).parse(decrypted_payload)
                        logger.info('payload parsed')
                    except DataGatewayDeviceProtocolParsingError as e:
                        self.error.error_message = str(e)
                        self.error.error_type = IntegrationV0MessageErrorType.data_unparsable
                        logger.warning(f'payload parsing error {e}')

            decrypted_payload_hex = decrypted_payload.hex()
            server_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            if capture_dt.tzinfo:
                capture_dt = capture_dt.astimezone(timezone.utc).replace(tzinfo=timezone.utc)
            else:
                capture_dt = capture_dt.replace(tzinfo=timezone.utc)
            if capture_dt > (server_time + timedelta(minutes=2)):
                self.error.error_message = f'Message time is in future {capture_dt}, server time {server_time}'
                self.error.error_type = IntegrationV0MessageErrorType.packet_from_the_future
            elif capture_dt < (server_time - timedelta(days=365)):
                self.error.error_message = f'Message time is older than 1 year from now {capture_dt}, server time {server_time}'
                self.error.error_type = IntegrationV0MessageErrorType.packet_from_the_past
            hacks: List[DeviceHack] = []
            device_tz = pytz.timezone('UTC')
            if self.device_data is not None:
                hacks = getattr(self.device_data, 'hacks', [])
                if self.device_data.device_tz is not None:
                    device_tz = pytz.timezone(self.device_data.device_tz)
                elif bs_geo is not None:
                    device_tz = ZoneInfo(TimezoneFinder().certain_timezone_at(lat=bs_geo.latitude, lng=bs_geo.longitude))  # type: ignore

            integration_message_datas: List[Tuple[IntegrationV0MessageData, str]] = [
                (
                    integration_mes,
                    type(pack.packet).__name__,  # type: ignore
                ) for pack in device_pack for integration_mes in pack.to_integration_data(
                    received_at=capture_dt,
                    device_tz=device_tz,
                    hacks=hacks,
                )]
            if not integration_message_datas:
                integration_message_datas = [(IntegrationV0MessageData(dt=capture_dt), 'EmptyDevicePacket')]

            for integration_message_data, packet_type_name in integration_message_datas:
                base_messages.append(IntegrationV0MessageGateway(
                    date_created=capture_dt,
                    data=integration_message_data,
                    meta=meta,
                    packet_type_name=packet_type_name,
                    id=message_id,
                    device_mac=self.rewritten_mac,
                    raw_payload=payload.hex(),
                    decrypted_payload=decrypted_payload_hex,
                    device_raw_mac=self.raw_mac,
                    protocol_name=self.current_net_rel.protocol.name if self.current_net_rel else None,
                    protocol_type=self.current_net_rel.protocol.type if self.current_net_rel else None,
                    raw_message=raw,
                    gateway_id=self.gateway_id,
                    network_id=self.current_network.id,
                    network_sys_type=self.current_network.sys_type,
                    device_id=self.current_net_rel.device_id if self.current_net_rel else None,
                    protocol_id=self.current_net_rel.protocol.id if self.current_net_rel else None,
                    verified_device=self.device_data is not None,
                    dt_calculated=True if capture_dt != integration_message_data.dt else False,
                    error=self.error,
                ))
            payload_str = payload.hex()

        sending_recipes: List[DeviceDataStructSendingRecipe] = []
        if self.send_always_to_data_logger:
            for base_message in base_messages:
                sending_recipes.append(DeviceDataStructSendingRecipe(
                    network=None,
                    message=base_message,
                    net_sys_type=NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA,
                ))
        if self.device_data:
            for net_rel in self.device_data.all_data_gateway_networks:  # TODO: data-aggregator setting for sending for repeater
                if net_rel.network.type_network is not NetworkTypeEnum.output:
                    continue

                if net_rel.network.sys_type not in ALL_SUPPORTED_OUTPUT_NETWORK_TYPES:
                    continue

                if self.send_always_to_data_logger and net_rel.network.sys_type is NetworkSysTypeEnum.OUTPUT_DATA_LOGGER_DEVICE_DATA:
                    continue

                for base_message in base_messages:
                    message = base_message.model_copy()
                    message.device_mac = net_rel.mac
                    message.device_id = net_rel.device_id

                    sending_recipes.append(DeviceDataStructSendingRecipe(
                        network=net_rel.network,
                        message=message,
                        net_sys_type=net_rel.network.sys_type,
                    ))
        else:
            for net in self.default_networks:
                for base_message in base_messages:
                    sending_recipes.append(DeviceDataStructSendingRecipe(
                        network=net,
                        message=base_message.model_copy(),
                        net_sys_type=net.sys_type,
                    ))

        return DeviceDataStruct(
            sending_recipes=sending_recipes,
            payload=PayloadInfo(encrypted_payload=payload_str, decrypted_payload=decrypted_payload_hex or None, encryption_type=encryption_type),
            device_packets=device_pack,
        )


@unique
class DeviceDataManagerKind(Enum):
    UPLINK = 'UPLINK'
    DOWNLINK = 'DOWNLINK'

    def prepare(
        self,
        gateway_id: UUID,
        network_id: UUID,
        macs: List[int],
        *,
        data_aggregator_sdk: DataAggregatorApiSdk,
        send_always_to_data_logger: bool,
        rewrite_mac: Optional[Callable[[int], Tuple[bool, int]]] = None,
        rewrite_enc: Optional[Callable[[int], Optional[Tuple[str, str]]]] = None,
    ) -> Dict[int, 'DeviceDataManager']:
        raw_to_new_macs_map: Dict[int, int] = {}
        rewritten_macs: Set[int] = set()
        forbidden_macs: Set[int] = set()
        raw_mac_to_enc_map: Dict[int, Tuple[EncryptionType, bytes]] = {}
        raw_macs: Set[int] = set()
        for mac in macs:
            forbidden, new_mac = rewrite_mac(mac) if rewrite_mac is not None else (False, mac)
            enc = None
            if rewrite_enc is not None:
                if enc := rewrite_enc(mac):
                    raw_mac_to_enc_map[new_mac] = EncryptionType(enc[0]), base64.b64decode(enc[1])
            if mac != new_mac:
                if not enc:
                    raw_macs.add(mac)
            raw_to_new_macs_map[mac] = new_mac
            rewritten_macs.add(new_mac)
            if forbidden:
                forbidden_macs.add(mac)
        default_networks: List[DataGatewayNetwork] = []
        current_network = None
        new_devices_data: List[DADeviceData] = []
        old_devices_data: List[DADeviceData] = []
        try:
            for net in data_aggregator_sdk.get_data_gateway_networks(gateway_id, None, None, None, None):
                if net.type_network == NetworkTypeEnum.output and net.is_alive:
                    net_params = net.params if isinstance(net.params, dict) else {}
                    if net_params.get('is_default', False):
                        default_networks.append(DataGatewayNetwork(
                            id=net.id,
                            name=net.name,
                            type_network=net.type_network,
                            sys_type=net.sys_type,
                            specifier=net.specifier,
                            params=net.params,
                        ))
                if net.id == network_id:
                    current_network = DataGatewayNetwork(
                        id=net.id,
                        name=net.name,
                        type_network=net.type_network,
                        sys_type=net.sys_type,
                        specifier=net.specifier,
                        params=net.params,
                    )

            new_devices_data = data_aggregator_sdk.get_devices_data(gateway_id, network_id, list(rewritten_macs))
            old_devices_data = data_aggregator_sdk.get_devices_data(gateway_id, network_id, list(raw_macs)) if len(raw_macs) > 0 else []

        except DataAggregatorRequestError as e:
            logger.info(f'data_aggregator_sdk.get_devices_data -> invalid: {e.args}')
        except DataAggregatorResponseError as e:
            logger.error(f'data_aggregator_sdk.get_devices_data -> failed: {e}')
            raise

        manager_by_old_mac: Dict[int, DeviceDataManager] = {}
        for mac in macs:
            error = IntegrationV0MessageError()
            if mac in forbidden_macs:
                logger.error(msg := f'Mac {mac} is forbidden for current bs serial number, packet is skipped')
                error = IntegrationV0MessageError(
                    error_message=msg,
                    error_type=IntegrationV0MessageErrorType.mac_duplicated,
                )

            device_data = _search_device_data(new_devices_data, gateway_id, network_id, raw_to_new_macs_map[mac])
            if device_data is None:
                dev_data = None
                cur_net_rel = None
                logger.info(msg := f'mac: {raw_to_new_macs_map.get(mac, mac)} data not found in: {network_id}')
                if error.error_type == IntegrationV0MessageErrorType.none:
                    error = IntegrationV0MessageError(
                        error_message=msg,
                        error_type=IntegrationV0MessageErrorType.device_unidentified,
                    )
            else:
                logger.info(f'mac: {mac} FOUND in data aggregator in network: {network_id}')
                dev_data, cur_net_rel = device_data

                enc_type: Optional[DaEncryptionType] = None
                enc_key_bytes: Optional[str] = None
                if mac in raw_mac_to_enc_map:
                    enc_type, _enc_key_bytes = raw_mac_to_enc_map[mac]  # type: ignore
                    enc_key_bytes = _enc_key_bytes.decode('utf-8')
                elif mac in raw_macs:
                    _old_device_data = _search_device_data(old_devices_data, gateway_id, network_id, mac)
                    if _old_device_data is not None:
                        _1, old_curr_net_rel = _old_device_data
                        if self is DeviceDataManagerKind.UPLINK:
                            enc_type, enc_key_bytes = old_curr_net_rel.uplink_encryption_type, old_curr_net_rel.uplink_encryption_key
                        else:
                            enc_type, enc_key_bytes = old_curr_net_rel.downlink_encryption_type, old_curr_net_rel.downlink_encryption_key
                if enc_type is not None:
                    if self is DeviceDataManagerKind.UPLINK:
                        cur_net_rel.uplink_encryption_type = enc_type
                        cur_net_rel.uplink_encryption_key = enc_key_bytes
                    # else:  # ToDo: downlink encryption
                    #     cur_net_rel.downlink_encryption_type = enc_type
                    #     cur_net_rel.downlink_encryption_key = enc_key_bytes
            assert current_network is not None      # just for mypy
            manager_by_old_mac[mac] = DeviceDataManager(
                raw_mac=mac,
                rewritten_mac=raw_to_new_macs_map[mac],
                kind=self,
                gateway_id=gateway_id,
                current_network=current_network,
                device_data=dev_data,
                current_net_rel=cur_net_rel,
                default_networks=default_networks,
                send_always_to_data_logger=send_always_to_data_logger,
                error=error,
            )
        return manager_by_old_mac


assert len(DeviceDataManagerKind) == 2, 'should have only 2 values. because logic support only 2'


def _search_device_data(devices_data: List[DADeviceData], gateway_id: UUID, network_id: UUID, mac: int) -> Optional[Tuple[DADeviceData, ApiDataGatewayNetworkDevice]]:
    for device_data in devices_data:
        for net_rel in device_data.all_data_gateway_networks:
            if net_rel.mac == mac and network_id == net_rel.network.id and net_rel.network.data_gateway.id == gateway_id:
                return device_data, net_rel
    return None
