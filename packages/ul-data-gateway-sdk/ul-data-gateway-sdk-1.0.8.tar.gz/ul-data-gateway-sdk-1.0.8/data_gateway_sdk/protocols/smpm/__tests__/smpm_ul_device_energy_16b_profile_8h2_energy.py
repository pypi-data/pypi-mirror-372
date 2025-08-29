from datetime import timedelta

from data_gateway_sdk.protocols.smpm.smpm_ul_device_energy_16b_profile_8h2_energy import \
    SmpmUlDeviceEnergy16BProfile8H2EnergyData, SmpmUlDeviceEnergy16bProfile8h2EnergyType
from data_gateway_sdk.utils.buf_ref import BufRef


def test_smpm_ul_device_energy_16b_profile_8h2_energy() -> None:
    case_serialized = bytes.fromhex("6b060080002000060001280006e000c8")
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_ACTIVE, point_factor_multiplier=2, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_ACTIVE, point_factor_multiplier=2, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=5.0))  # noqa: E501
    case_serialized = bytes.fromhex("6b030080002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=0.0), point_factor=0.0, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6b0f0080002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=0.0), point_factor=0.0, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6b030080002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=0.0), point_factor=6.3, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6b0f0080002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=0.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=0.0), point_factor=6.3, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6bf30380002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=0.0, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6bff0380002000060001280006e00000")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=0.0) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=0.0, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6bf30380002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=1, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=6.3, point_factor_multiplier=1, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
    case_serialized = bytes.fromhex("6bff0380002000060001280006e000fc")  # overflow
    assert SmpmUlDeviceEnergy16BProfile8H2EnergyData(type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE, point_factor_multiplier=4, days_ago=timedelta(seconds=5443200.0), profile=(0, 1, 2, 3, 4, 5, 6, 7), point_factor=6.3) == SmpmUlDeviceEnergy16BProfile8H2EnergyData.parse(BufRef(case_serialized))  # noqa: E501
    assert case_serialized == SmpmUlDeviceEnergy16BProfile8H2EnergyData.serialize(SmpmUlDeviceEnergy16BProfile8H2EnergyData(days_ago=timedelta(seconds=5443200.0), point_factor=6.3, point_factor_multiplier=4, profile=(0, 1, 2, 3, 4, 5, 6, 7), type=SmpmUlDeviceEnergy16bProfile8h2EnergyType.ENERGY_CONSUMED_REACTIVE))  # noqa: E501
