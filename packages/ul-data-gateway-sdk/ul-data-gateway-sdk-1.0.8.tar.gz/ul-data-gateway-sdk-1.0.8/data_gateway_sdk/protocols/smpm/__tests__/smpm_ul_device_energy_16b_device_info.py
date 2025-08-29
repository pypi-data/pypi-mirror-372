from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_device_info import SmpmUlDeviceEnergy16BDeviceInfoData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_device_info() -> None:
    case_serialized = bytes.fromhex("befbffffffffffeffbfbf70300000000")
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=562949953421311, device_type=31, firmware_version=127, ktt=255, ktn=63) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=562949953421311, device_type=31, firmware_version=127, ktt=255, ktn=63))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=0, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=0, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1f0000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=0, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=0, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be0300000000000000f80f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=0, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=0, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1f00f80f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=0, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=0, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000000000f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=0, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=127, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1f0000f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=0, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=127, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be0300000000000000f8ff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=0, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=127, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1f00f8ff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=0, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=0, ktn=127, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be03000000000000f807000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=255, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=0, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1ff807000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=255, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=0, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be03000000000000f8ff0f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=255, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=0, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1ff8ff0f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=255, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=0, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be03000000000000f807f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=255, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=127, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1ff807f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=255, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=127, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be03000000000000f8ffff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=0, firmware_version=255, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=127, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffff1ff8ffff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=0, firmware_version=255, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=0, firmware_version=255, ktn=127, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e00700000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=0, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=0, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffff0700000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=0, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=0, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e007f80f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=0, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=0, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffff07f80f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=0, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=0, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e00700f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=0, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=127, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffff0700f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=0, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=127, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e007f8ff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=0, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=127, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffff07f8ff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=0, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=0, ktn=127, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e0ff07000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=255, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=0, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffffff07000000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=255, ktt=0, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=0, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e0ffff0f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=255, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=0, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffffffff0f0000000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=255, ktt=511, ktn=0) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=0, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e0ff07f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=255, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=127, ktt=0, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffffff07f00700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=255, ktt=0, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=127, ktt=0, manufacturer_number=1125899906842623))  # noqa: E501
    case_serialized = bytes.fromhex("be030000000000e0ffffff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=0, device_type=63, firmware_version=255, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=127, ktt=511, manufacturer_number=0))  # noqa: E501
    case_serialized = bytes.fromhex("befbffffffffffffffffff0700000000")  # overflow
    assert SmpmUlDeviceEnergy16BDeviceInfoData(manufacturer_number=1125899906842623, device_type=63, firmware_version=255, ktt=511, ktn=127) == SmpmUlDeviceEnergy16BDeviceInfoData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BDeviceInfoData.serialize(SmpmUlDeviceEnergy16BDeviceInfoData(device_type=63, firmware_version=255, ktn=127, ktt=511, manufacturer_number=1125899906842623))  # noqa: E501
