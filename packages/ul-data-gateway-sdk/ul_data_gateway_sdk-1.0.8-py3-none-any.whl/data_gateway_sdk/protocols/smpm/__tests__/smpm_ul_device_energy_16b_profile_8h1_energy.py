from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h1_energy import \
    SmpmUlDeviceEnergy16BProfile8H1EnergyData, SmpmUlDeviceEnergy16bProfile8h1EnergyType
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_profile_8h1_energy() -> None:
    case_serialized = bytes.fromhex("6a060080002000060001280006e000c8")
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_ACTIVE, point_factor_multiplier=2, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_ACTIVE, point_factor_multiplier=2, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0))  # noqa: E501
    case_serialized = bytes.fromhex("6a030080002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=0.0), point_factor=0.0, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6a0f0080002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=0.0), point_factor=0.0, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6a030080002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=0.0), point_factor=6.3, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6a0f0080002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=0.0), point_factor=6.3, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6af30380002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=0.0, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6aff0380002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=0.0, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6af30380002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=6.3, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6aff0380002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H1EnergyData(type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H1EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H1EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H1EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=6.3, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h1EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
