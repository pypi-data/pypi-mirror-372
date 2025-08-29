from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_3phase_generated import \
    SmpmUlDeviceEnergy16B3PhaseGeneratedData
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_3phase_generated() -> None:
    case_serialized = bytes.fromhex("cb02300f1e00900d0160574cdb5e0105")
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=False, total=123123, phase_a=4313, phase_b=14312123, phase_c=1312123) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=False, total=123123, phase_a=4313, phase_b=14312123, phase_c=1312123))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cb020800000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=0.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=0.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=0, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=0, phase_b=67108864, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=0, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=0, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=0, total=8589934592, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=67108864, total=0, valid=True))  # noqa: E501
    case_serialized = bytes.fromhex("cbf20f00000000000000000000000000")  # overflow
    assert SmpmUlDeviceEnergy16B3PhaseGeneratedData(energy_is_reactive=False, days_ago=timedelta(seconds=10972800.0), valid=True, total=0, phase_a=0, phase_b=0, phase_c=0) == SmpmUlDeviceEnergy16B3PhaseGeneratedData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16B3PhaseGeneratedData.serialize(SmpmUlDeviceEnergy16B3PhaseGeneratedData(days_ago=timedelta(seconds=10972800.0), energy_is_reactive=False, phase_a=67108864, phase_b=67108864, phase_c=67108864, total=8589934592, valid=True))  # noqa: E501
