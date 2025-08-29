import json
import os.path
from datetime import datetime, timezone

from data_gateway_sdk.nero_bs_protocol import NeroBsProtocolType
from data_gateway_sdk.protocols.nero_bs_packet.http_nero_bs_packet import HttpV0NeroBsPacket, BaseStationInfo, BaseStationInfoGeo, BaseStationAdditionalInfo, DevicePackage, \
    DataNbfi, SdrInfo, DevicePackageProtocolTypeEnum, DevicePackageNetworkTypeEnum, SdrConfig, SdrConfigData, DModEnum, BaseStationLogs, BaseStationLogsTypeEnum
from data_gateway_sdk.protocols.nero_bs_packet.kafka_nero_bs_packet import KafkaV0NeroBsPacket, KafkaMessageType, KafkaStationType, \
    KafkaV1NeroBsData

with open(os.path.join(os.path.dirname(__file__), 'bs_http_data.json')) as valid_json_f:
    VALID_BS_HTTP_DATA = json.load(valid_json_f)

PACKET_KAFKA_1 = {"baudrate": 50, "encrypted": True, "freq_channel": 871282100, "freq_expect": 38, "message_id": 106723,
                  "message_type": "nbfi", "modem_id": 8406389, "nbfi_f_ask": 0, "nbfi_iterator": 21, "nbfi_multi": 0,
                  "nbfi_system": 0, "payload": "03c7d800b7e8a521", "sdr": 0, "signal_rssi": -66, "signal_snr": 42,
                  "station_id": 9050, "station_type": "nero", "time_detected": 1665608401, "time_published": 1665608401,
                  "ul_phy": 21}

PACKET_KAFKA_2 = {"baudrate": 50, "encrypted": True, "freq_channel": 871282100, "freq_expect": 38, "message_id": 106723,
                  "message_type": "nbfi", "modem_id": 8406389, "nbfi_f_ask": None, "nbfi_iterator": None, "nbfi_multi": None,
                  "nbfi_system": None, "payload": "03c7d800b7e8a521", "sdr": 0, "signal_rssi": -66, "signal_snr": 42,
                  "station_id": 9050, "station_type": "nero", "time_detected": 1665608401, "time_published": 1665608401,
                  "ul_phy": 21}

PACKET_KAFKA_3 = {"baudrate": 50, "encrypted": True, "freq_channel": 871282100, "freq_expect": 38, "message_id": 106723,
                  "message_type": "nbfi", "modem_id": 8406389, "payload": "03c7d800b7e8a521", "sdr": 0, "signal_rssi": -66, "signal_snr": 42,
                  "station_id": 9050, "station_type": "nero", "time_detected": 1665608401, "time_published": 1665608401,
                  "ul_phy": 21}


def test_parsing_valid_bs_http() -> None:
    assert NeroBsProtocolType.NERO_BS_HTTP_V0.parse(VALID_BS_HTTP_DATA) == HttpV0NeroBsPacket(
        data=[
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 29, 1, tzinfo=timezone.utc),
                raw='000000008b6a3672fa335e6eac5ab668',
                data_nbfi=DataNbfi(mac=0, f_ask=False, iterator=0, multi=False, system=False, payload='8b6a3672fa335e6e'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868792300, freq_channel=89, sdr=0, baud_rate=50, rssi=-65, snr=67),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11986,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 29, 5, tzinfo=timezone.utc),
                raw='000000008b6a3672fa335e6eac5ab668',
                data_nbfi=DataNbfi(mac=0, f_ask=False, iterator=0, multi=False, system=False, payload='8b6a3672fa335e6e'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868819900, freq_channel=227, sdr=0, baud_rate=50, rssi=-68, snr=60),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11987,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 29, 16, tzinfo=timezone.utc),
                raw='8007a40dcf536171e112d18077342161',
                data_nbfi=DataNbfi(mac=8390564, f_ask=False, iterator=13, multi=False, system=False, payload='cf536171e112d180'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868796500, freq_channel=110, sdr=0, baud_rate=50, rssi=-91, snr=24),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11988,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 29, 23, tzinfo=timezone.utc),
                raw='8007a40dcf536171e112d18077342161',
                data_nbfi=DataNbfi(mac=8390564, f_ask=False, iterator=13, multi=False, system=False, payload='cf536171e112d180'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868823900, freq_channel=247, sdr=0, baud_rate=50, rssi=-93, snr=19),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11989,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 30, 59, tzinfo=timezone.utc),
                raw='802f0f00f54cdc01cdbe45a6a559ce7f',
                data_nbfi=DataNbfi(mac=8400655, f_ask=False, iterator=0, multi=False, system=False, payload='f54cdc01cdbe45a6'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868793300, freq_channel=94, sdr=0, baud_rate=50, rssi=-93, snr=39),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11990,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 31, 7, tzinfo=timezone.utc),
                raw='802f0f00f54cdc01cdbe45a6a559ce7f',
                data_nbfi=DataNbfi(mac=8400655, f_ask=False, iterator=0, multi=False, system=False, payload='f54cdc01cdbe45a6'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868820700, freq_channel=231, sdr=0, baud_rate=50, rssi=-99, snr=33),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11991,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 31, 20, tzinfo=timezone.utc),
                raw='8029740acf1586ec0de61a9c9d92105a',
                data_nbfi=DataNbfi(mac=8399220, f_ask=False, iterator=10, multi=False, system=False, payload='cf1586ec0de61a9c'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868784300, freq_channel=49, sdr=0, baud_rate=50, rssi=-66, snr=62),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11992,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 31, 28, tzinfo=timezone.utc), raw='8029740acf1586ec0de61a9c9d92105a',
                data_nbfi=DataNbfi(mac=8399220, f_ask=False, iterator=10, multi=False, system=False, payload='cf1586ec0de61a9c'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868812100, freq_channel=188, sdr=0, baud_rate=50, rssi=-68, snr=52),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11993,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 31, 57, tzinfo=timezone.utc), raw='80d19006f13ebae6a9c7b66f7d2a87f1',
                data_nbfi=DataNbfi(mac=8442256, f_ask=False, iterator=6, multi=False, system=False, payload='f13ebae6a9c7b66f'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868809100, freq_channel=173, sdr=0, baud_rate=50, rssi=-97, snr=15),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11994,  # type: ignore
            ),
            DevicePackage(
                dt=datetime(2023, 2, 1, 13, 31, 59, tzinfo=timezone.utc),
                raw='802f0f009042a07fc08a377e1dba7f62',
                data_nbfi=DataNbfi(mac=8400655, f_ask=False, iterator=0, multi=False, system=False, payload='9042a07fc08a377e'),
                data_unbp=None,
                data_unbp2=None,
                sdr_info=SdrInfo(freq=868779500, freq_channel=25, sdr=0, baud_rate=50, rssi=-98, snr=16),
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                message_id=None,
                id=11995,  # type: ignore
            ),
        ],
        base_station_environment_info=[],
        base_station_info=BaseStationInfo(
            geo=BaseStationInfoGeo(dt=datetime(2023, 2, 2, 15, 23, 15, tzinfo=timezone.utc), longitude=0.0, latitude=0.0, actual=False),
            uptime_s=247767,
            sdr_config=SdrConfig(
                freq=868800000,
                sdr=[
                    SdrConfigData(enable=True, dds_freq=0, dmod=DModEnum.DBPSK, baud_rate=50, unions=4),
                    SdrConfigData(enable=True, dds_freq=0, dmod=DModEnum.DBPSK, baud_rate=100, unions=4),
                ],
            ),
        ),
        base_station_additional_info=BaseStationAdditionalInfo(id=9017, version='1.6.0-3-17.12.2022'),
        base_station_logs=[
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 28, 47, tzinfo=timezone.utc), text='GNSS Info NOT received'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 28, 58, tzinfo=timezone.utc), text='GNSS Info NOT received'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 29, 9, tzinfo=timezone.utc), text='GNSS Info NOT received'),
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 29, 20, tzinfo=timezone.utc), text='GNSS Info NOT received'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 29, 31, tzinfo=timezone.utc), text='GNSS Info NOT received'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 29, 42, tzinfo=timezone.utc), text='GNSS Info NOT received'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 29, 53, tzinfo=timezone.utc), text='GNSS Info NOT received'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.warning, mdl='lte', dt=datetime(2023, 2, 1, 13, 30, 4, tzinfo=timezone.utc), text='GNSS Info NOT received'),
            BaseStationLogs(type=BaseStationLogsTypeEnum.info, mdl='kafka', dt=datetime(2023, 2, 1, 13, 30, 7, tzinfo=timezone.utc), text='librdkafka: [thrd:ssl://broker.bs0.data-gateway.staging.lk.dev-unic-lab.by:32003/]: ssl://broker.bs0.data-gateway.staging.lk.dev-unic-lab.by:32003/1001: Disconnected (after 6216127ms in state UP, 1 identical error(s) suppressed)'),  # noqa: E501
            BaseStationLogs(type=BaseStationLogsTypeEnum.error, mdl='kafka', dt=datetime(2023, 2, 1, 13, 30, 8, tzinfo=timezone.utc), text='error -195 (Local: Broker transport failure), reason: ssl://broker.bs0.data-gateway.staging.lk.dev-unic-lab.by:32003/1001: Disconnected (after 6216127ms in state UP, 1 identical error(s) suppressed)'),  # noqa: E501
        ],
    )


def test_parsing_of_kafka_v0() -> None:
    assert NeroBsProtocolType.NERO_BS_KAFKA_V0.parse(PACKET_KAFKA_1) == KafkaV0NeroBsPacket(
        encrypted=True,
        freq_channel=871282100,
        freq_expect=38,
        message_id=106723,
        modem_id=8406389,
        nbfi_f_ask=0,
        nbfi_iterator=21,
        nbfi_multi=0,
        nbfi_system=0,
        payload='03c7d800b7e8a521',
        signal_rssi=-66,
        signal_snr=42,
        station_id=9050,
        station_type=KafkaStationType.nero,
        time_detected=1665608401,
        time_published=1665608401,
        ul_phy=21,
    )


def test_parsing_of_kafka_v1() -> None:
    assert NeroBsProtocolType.NERO_BS_KAFKA_V1.parse(PACKET_KAFKA_1) == KafkaV1NeroBsData(
        encrypted=True,
        freq_channel=871282100,
        freq_expect=38,
        message_id=106723,
        modem_id=8406389,
        nbfi_f_ask=0,
        nbfi_iterator=21,
        nbfi_multi=0,
        nbfi_system=0,
        payload='03c7d800b7e8a521',
        signal_rssi=-66,
        signal_snr=42,
        station_id=9050,
        station_type=KafkaStationType.nero,
        time_detected=1665608401,
        time_published=1665608401,
        ul_phy=21,
        baudrate=50,
        sdr=0,
        message_type=KafkaMessageType.nbfi,
    )


def test_parsing_of_kafka_v1_none() -> None:
    assert NeroBsProtocolType.NERO_BS_KAFKA_V1.parse(PACKET_KAFKA_2) == KafkaV1NeroBsData(
        encrypted=True,
        freq_channel=871282100,
        freq_expect=38,
        message_id=106723,
        modem_id=8406389,
        payload='03c7d800b7e8a521',
        signal_rssi=-66,
        signal_snr=42,
        station_id=9050,
        station_type=KafkaStationType.nero,
        time_detected=1665608401,
        time_published=1665608401,
        ul_phy=21,
        baudrate=50,
        sdr=0,
        message_type=KafkaMessageType.nbfi,
    )


def test_parsing_of_kafka_v1_abscent() -> None:
    assert NeroBsProtocolType.NERO_BS_KAFKA_V1.parse(PACKET_KAFKA_3) == KafkaV1NeroBsData(
        encrypted=True,
        freq_channel=871282100,
        freq_expect=38,
        message_id=106723,
        modem_id=8406389,
        payload='03c7d800b7e8a521',
        signal_rssi=-66,
        signal_snr=42,
        station_id=9050,
        station_type=KafkaStationType.nero,
        time_detected=1665608401,
        time_published=1665608401,
        ul_phy=21,
        baudrate=50,
        sdr=0,
        message_type=KafkaMessageType.nbfi,
    )
