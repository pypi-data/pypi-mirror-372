from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_8b_get_data import SmpmDlDeviceEnergy8BGetDataData, SmpmDlDeviceEnergy8bGetDataDataRequestMonth, \
    SmpmDlDeviceEnergy8bGetDataDataRequestId
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_dl_device_energy_8b_get_data() -> None:
    case_serialized = bytes.fromhex("8001c5930c780300")
    assert SmpmDlDeviceEnergy8BGetDataData(year=2032, month=SmpmDlDeviceEnergy8bGetDataDataRequestMonth.JAN, day=15, request_data_pack_ids=(SmpmDlDeviceEnergy8bGetDataDataRequestId.DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2, SmpmDlDeviceEnergy8bGetDataDataRequestId.NETWORK_PARAMS_PHASE1)) == SmpmDlDeviceEnergy8BGetDataData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("800130900c780300")  # overflow
    assert SmpmDlDeviceEnergy8BGetDataData(year=2000, month=SmpmDlDeviceEnergy8bGetDataDataRequestMonth.DEC, day=0, request_data_pack_ids=(SmpmDlDeviceEnergy8bGetDataDataRequestId.DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2, SmpmDlDeviceEnergy8bGetDataDataRequestId.NETWORK_PARAMS_PHASE1)) == SmpmDlDeviceEnergy8BGetDataData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("80f933900c780300")  # overflow
    assert SmpmDlDeviceEnergy8BGetDataData(year=2127, month=SmpmDlDeviceEnergy8bGetDataDataRequestMonth.DEC, day=0, request_data_pack_ids=(SmpmDlDeviceEnergy8bGetDataDataRequestId.DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2, SmpmDlDeviceEnergy8bGetDataDataRequestId.NETWORK_PARAMS_PHASE1)) == SmpmDlDeviceEnergy8BGetDataData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("8001f0970c780300")  # overflow
    assert SmpmDlDeviceEnergy8BGetDataData(year=2000, month=SmpmDlDeviceEnergy8bGetDataDataRequestMonth.DEC, day=31, request_data_pack_ids=(SmpmDlDeviceEnergy8bGetDataDataRequestId.DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2, SmpmDlDeviceEnergy8bGetDataDataRequestId.NETWORK_PARAMS_PHASE1)) == SmpmDlDeviceEnergy8BGetDataData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("80f9f3970c780300")  # overflow
    assert SmpmDlDeviceEnergy8BGetDataData(year=2127, month=SmpmDlDeviceEnergy8bGetDataDataRequestMonth.DEC, day=31, request_data_pack_ids=(SmpmDlDeviceEnergy8bGetDataDataRequestId.DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2, SmpmDlDeviceEnergy8bGetDataDataRequestId.NETWORK_PARAMS_PHASE1)) == SmpmDlDeviceEnergy8BGetDataData.parse(BufRef(case_serialized))  # noqa: E501
