from data_gateway_sdk.protocols.smpm.smpm_dl_device_energy_8b_set_relay import SmpmDlDeviceEnergy8BSetRelayData, SmpmDlDeviceEnergy8bSetRelayId
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_dl_device_energy_8b_set_relay() -> None:
    case_serialized = bytes.fromhex("aa01000000000000")
    assert SmpmDlDeviceEnergy8BSetRelayData(state=False, relay_id=SmpmDlDeviceEnergy8bSetRelayId.ALL) == SmpmDlDeviceEnergy8BSetRelayData.parse(BufRef(case_serialized))  # noqa: E501
    case_serialized = bytes.fromhex("aa71000000000000")  # overflow
    assert SmpmDlDeviceEnergy8BSetRelayData(state=False, relay_id=SmpmDlDeviceEnergy8bSetRelayId.RELAY_ID_7) == SmpmDlDeviceEnergy8BSetRelayData.parse(BufRef(case_serialized))  # noqa: E501
