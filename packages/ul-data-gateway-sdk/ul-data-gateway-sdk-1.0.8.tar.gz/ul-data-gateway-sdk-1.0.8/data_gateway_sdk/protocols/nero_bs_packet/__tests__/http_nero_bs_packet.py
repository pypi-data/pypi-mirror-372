from datetime import datetime
from uuid import UUID

from data_aggregator_sdk.integration_message import IntegrationV0MessageMeta
from pydantic import ValidationError

from data_gateway_sdk.errors import DataGatewayBSProtocolParsingError
from data_gateway_sdk.protocols.nero_bs_packet.http_nero_bs_packet import HttpV0NeroBsPacket, DevicePackage, \
    BaseStationInfo, BaseStationAdditionalInfo, BaseStationLogs, DevicePackageProtocolTypeEnum, \
    DevicePackageNetworkTypeEnum, BaseStationInfoGeo, BaseStationLogsTypeEnum, DataNbfi, DataUnbp, SdrInfo, \
    BaseStationEnvironmentInfo, DModEnum, DataUnbp2

DATETIME = datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11)

DEVICE_PACKET_NBFI = {
    'data': [
        {
            'dt': DATETIME,
            'raw': 'FFFFFFFFFFFFFFFF',
            'type': 'uplink',
            'protocol': 'nbfi',
            'data_nbfi': {'mac': 12345678, 'f_ask': True, 'iterator': 3, 'multi': False, 'system': True, 'payload': 'FFFFFFFFFFFFFFFF'},
            'sdr_info': {'freq': 870282100, 'freq_channel': 871282100, 'sdr': 0, 'baud_rate': 50, 'rssi': -75, 'snr': 65},
        },
    ],
    'base_station_environment_info': [
        {
            'dt': DATETIME,
            'spectrum': [0, 0, 0, 0, 0, 0],
            'sdr': 25,
            'freq_carrier': 0.1,
            'freq_delta': 0.5,
        },
    ],
    'base_station_info': {'geo': {'dt': DATETIME, 'actual': True}, 'uptime_s': 21},
    'base_station_additional_info': {'id': 15015},
    'base_station_logs': [{'type': 'info', 'dt': DATETIME, 'text': ''}],

}

DEVICE_PACKET_UNBP = {
    'data': [
        {
            'dt': DATETIME,
            'raw': 'FFFFFFFFFFFFFFFF',
            'type': 'downlink',
            'protocol': 'unbp',
            'data_unbp': {'mac': 12345678, 'ack': True, 'iterator': 3, 'payload': 'FFFFFFFF'},
            'sdr_info': {'freq': 870282100, 'freq_channel': 871282100, 'sdr': 0, 'baud_rate': 50, 'rssi': -75, 'snr': 65},
        },
    ],
    'base_station_environment_info': [
        {
            'dt': DATETIME,
            'spectrum': [0, 0, 0, 0, 0, 0],
            'sdr': 25,
            'freq_carrier': 0.1,
            'freq_delta': 0.5,
        },
    ],
    'base_station_info': {'geo': {'dt': DATETIME, 'actual': True}, 'uptime_s': 21},
    'base_station_additional_info': {'id': 15015},
    'base_station_logs': [{'type': 'info', 'dt': DATETIME, 'text': ''}],

}

DEVICE_PACKET_UNBP2 = {
    'data': [
        {
            'dt': DATETIME,
            'raw': 'FFFFFFFFFFFFFFFF',
            'type': 'downlink',
            'protocol': 'unbp2',
            'data_unbp2': {'mac': 12345678, 'payload': 'FFFFFFFF'},
            'sdr_info': {'freq': 870282100, 'freq_channel': 871282100, 'sdr': 0, 'baud_rate': 50, 'rssi': -75, 'snr': 65},
        },
    ],
    'base_station_environment_info': [
        {
            'dt': DATETIME,
            'spectrum': [0, 0, 0, 0, 0, 0],
            'sdr': 25,
            'freq_carrier': 0.1,
            'freq_delta': 0.5,
        },
    ],
    'base_station_info': {'geo': {'dt': DATETIME, 'actual': True}, 'uptime_s': 21},
    'base_station_additional_info': {'id': 15015},
    'base_station_logs': [{'type': 'info', 'dt': DATETIME, 'text': ''}],

}

DEVICE_PACKET_WRONG = {
    'data': [
        {
            'dt': datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            'raw': 'FF',
            'type': 'downlink',
            'protocol': 'unbpp',
            'data_unbp': {'mac': 64, 'ack': True, 'iterator': 3, 'payload': 'FF'},
            'sdr_info': {'freq': 0, 'freq_channel': -1, 'sdr': 0, 'baud_rate': -1, 'rssi': -75, 'snr': 65},
        },
    ],
    'base_station_environment_info': [
        {
            'dt': datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            'spectrum': [0, 0, 0, 0, 0, 0],
            'sdr': 25,
            'freq_carrier': 0.1,
            'freq_delta': 0.5,
        },
    ],
    'base_station_info': {
        'geo': {
            'dt': datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            'actual': True,
        },
        'uptime_s': -1,
    },
    'base_station_additional_info': {'id': 15015},
    'base_station_logs': [
        {'type': 'info', 'dt': datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11), 'text': ''},
    ],

}

DEVICE_PACKAGE_NBFI = DevicePackage(
    dt=DATETIME,
    raw='FFFFFFFFFFFFFFFF',
    type=DevicePackageNetworkTypeEnum.uplink,
    protocol=DevicePackageProtocolTypeEnum.nbfi,
    data_nbfi=DataNbfi(mac=12345678, f_ask=True, iterator=3, multi=False, system=True, payload='FFFFFFFFFFFFFFFF'),
    sdr_info=SdrInfo(freq=870282100, freq_channel=871282100, sdr=0, baud_rate=50, rssi=-75, snr=65),
)

DEVICE_PACKAGE_UNBP = DevicePackage(
    dt=DATETIME,
    raw='FFFFFFFFFFFFFFFF',
    type=DevicePackageNetworkTypeEnum.downlink,
    protocol=DevicePackageProtocolTypeEnum.unbp,
    data_unbp=DataUnbp(mac=12345678, iterator=3, payload='FFFFFFFF', ack=True),
    sdr_info=SdrInfo(freq=870282100, freq_channel=871282100, sdr=0, baud_rate=50, rssi=-75, snr=65),
)

DEVICE_PACKAGE_UNBP2 = DevicePackage(
    dt=DATETIME,
    raw='FFFFFFFFFFFFFFFF',
    type=DevicePackageNetworkTypeEnum.downlink,
    protocol=DevicePackageProtocolTypeEnum.unbp2,
    data_unbp2=DataUnbp2(mac=12345678, payload='FFFFFFFF'),
    sdr_info=SdrInfo(freq=870282100, freq_channel=871282100, sdr=0, baud_rate=50, rssi=-75, snr=65),
)


def test_parsing_of_true_device_packet() -> None:
    assert DModEnum.DBPSK.__repr__() == 'DModEnum.DBPSK'
    assert DevicePackageNetworkTypeEnum.downlink.__repr__() == 'DevicePackageNetworkTypeEnum.downlink'
    assert BaseStationLogsTypeEnum.info.__repr__() == 'BaseStationLogsTypeEnum.info'

    assert type(DEVICE_PACKAGE_NBFI.payload_bytes) is bytes
    assert type(DEVICE_PACKAGE_UNBP.payload_bytes) is bytes
    assert type(DEVICE_PACKAGE_UNBP2.payload_bytes) is bytes
    assert type(DEVICE_PACKAGE_NBFI.mac) is int
    assert type(DEVICE_PACKAGE_UNBP.mac) is int
    assert type(DEVICE_PACKAGE_UNBP2.mac) is int

    assert HttpV0NeroBsPacket.parse(DEVICE_PACKET_NBFI) == HttpV0NeroBsPacket(
        data=[
            DEVICE_PACKAGE_NBFI,
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=DATETIME,
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    )

    assert HttpV0NeroBsPacket.parse(DEVICE_PACKET_UNBP) == HttpV0NeroBsPacket(
        data=[
            DEVICE_PACKAGE_UNBP,
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    )

    assert HttpV0NeroBsPacket.parse(DEVICE_PACKET_UNBP2) == HttpV0NeroBsPacket(
        data=[
            DEVICE_PACKAGE_UNBP2,
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    )

    assert type(HttpV0NeroBsPacket(
        data=[
            DEVICE_PACKAGE_UNBP,
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    ).to_integration_meta(base_station_api_user_id=UUID('bca85c53-3819-4470-ad53-b2cba9cce603'), packet=DEVICE_PACKAGE_UNBP)) is IntegrationV0MessageMeta


def test_parsing_of_wrong_device_packet() -> None:
    assert HttpV0NeroBsPacket.parse(DEVICE_PACKET_NBFI) != HttpV0NeroBsPacket(
        data=[
            DevicePackage(
                dt=DATETIME,
                raw='FFFFFFFFFFFFFFFF',
                type=DevicePackageNetworkTypeEnum.uplink,
                protocol=DevicePackageProtocolTypeEnum.nbfi,
                data_nbfi=DataNbfi(mac=64, f_ask=True, iterator=3, multi=False, system=True, payload='FFFFFFFFFFFFFFFF'),
                sdr_info=SdrInfo(freq=870282100, freq_channel=871282100, sdr=0, baud_rate=50, rssi=-75, snr=65),
            ),
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    )
    assert HttpV0NeroBsPacket.parse(DEVICE_PACKET_UNBP) != HttpV0NeroBsPacket(
        data=[
            DevicePackage(
                dt=DATETIME,
                raw='FFFFFFFFFFFFFFFF',
                type=DevicePackageNetworkTypeEnum.downlink,
                protocol=DevicePackageProtocolTypeEnum.unbp,
                data_unbp=DataUnbp(mac=64, iterator=3, payload='FFFFFFFF', ack=True),
                sdr_info=SdrInfo(freq=871282100, freq_channel=871282100, sdr=0, baud_rate=50, rssi=-75, snr=65),
            ),
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    )
    assert HttpV0NeroBsPacket.parse(DEVICE_PACKET_UNBP2) != HttpV0NeroBsPacket(
        data=[
            DevicePackage(
                dt=DATETIME,
                raw='FFFFFFFFFFFFFFFF',
                type=DevicePackageNetworkTypeEnum.downlink,
                protocol=DevicePackageProtocolTypeEnum.unbp2,
                data_unbp2=DataUnbp2(mac=64, payload='FFFFFFFF'),
                sdr_info=SdrInfo(freq=871282100, freq_channel=871282100, sdr=0, baud_rate=50, rssi=-75, snr=65),
            ),
        ],
        base_station_environment_info=[BaseStationEnvironmentInfo(
            dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
            spectrum=[0, 0, 0, 0, 0, 0],
            sdr=25,
            freq_carrier=0.1,
            freq_delta=0.5,
        )],
        base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=21),
        base_station_additional_info=BaseStationAdditionalInfo(id=15015),
        base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
    )


def test_check_validation_of_device_packet() -> None:
    try:
        HttpV0NeroBsPacket(
            data=[
                DevicePackage(
                    dt=DATETIME,
                    raw='FF',
                    type=DevicePackageNetworkTypeEnum.uplink,
                    protocol=DevicePackageProtocolTypeEnum.nbfi,
                    data_nbfi=DataNbfi(mac=0, f_ask=True, iterator=-1, multi=False, system=True, payload='FFFFFFFFFFFFFFF'),
                    sdr_info=SdrInfo(freq=0, freq_channel=-1, sdr=0, baud_rate=-1, rssi=-75, snr=65),
                ),
            ],
            base_station_environment_info=[BaseStationEnvironmentInfo(
                dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
                spectrum=[0, 0, 0, 0, 0, 0],
                sdr=25,
                freq_carrier=0.1,
                freq_delta=0.5,
            )],
            base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=-1),
            base_station_additional_info=BaseStationAdditionalInfo(id=15015),
            base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
        )
    except ValidationError as exc:
        assert type(exc) is ValidationError

    try:
        HttpV0NeroBsPacket(
            data=[
                DevicePackage(
                    dt=DATETIME,
                    raw='FF',
                    type=DevicePackageNetworkTypeEnum.downlink,
                    protocol=DevicePackageProtocolTypeEnum.unbp,
                    data_unbp=DataUnbp(mac=0, iterator=-1, payload='FF', ack=True),
                    sdr_info=SdrInfo(freq=0, freq_channel=-1, sdr=0, baud_rate=-1, rssi=-75, snr=65),
                ),
            ],
            base_station_environment_info=[BaseStationEnvironmentInfo(
                dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
                spectrum=[0, 0, 0, 0, 0, 0],
                sdr=25,
                freq_carrier=0.1,
                freq_delta=0.5,
            )],
            base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=-1),
            base_station_additional_info=BaseStationAdditionalInfo(id=15015),
            base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
        )
    except ValidationError as exc:
        assert type(exc) is ValidationError

    try:
        HttpV0NeroBsPacket(
            data=[
                DevicePackage(
                    dt=DATETIME,
                    raw='FF',
                    type=DevicePackageNetworkTypeEnum.downlink,
                    protocol=DevicePackageProtocolTypeEnum.unbp2,
                    data_unbp2=DataUnbp2(mac=0, payload='FF'),
                    sdr_info=SdrInfo(freq=0, freq_channel=-1, sdr=0, baud_rate=-1, rssi=-75, snr=65),
                ),
            ],
            base_station_environment_info=[BaseStationEnvironmentInfo(
                dt=datetime(year=2022, month=10, day=15, hour=4, minute=16, second=11),
                spectrum=[0, 0, 0, 0, 0, 0],
                sdr=25,
                freq_carrier=0.1,
                freq_delta=0.5,
            )],
            base_station_info=BaseStationInfo(geo=BaseStationInfoGeo(dt=DATETIME, actual=True), uptime_s=-1),
            base_station_additional_info=BaseStationAdditionalInfo(id=15015),
            base_station_logs=[BaseStationLogs(type=BaseStationLogsTypeEnum.info, dt=DATETIME, text='')],
        )
    except ValidationError as exc:
        assert type(exc) is ValidationError

    try:
        HttpV0NeroBsPacket.parse(DEVICE_PACKET_WRONG)
    except DataGatewayBSProtocolParsingError as exc:
        assert type(exc) is DataGatewayBSProtocolParsingError
