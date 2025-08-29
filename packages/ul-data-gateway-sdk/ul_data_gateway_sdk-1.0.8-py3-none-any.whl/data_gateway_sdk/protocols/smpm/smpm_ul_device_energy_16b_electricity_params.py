from decimal import Decimal
from datetime import datetime, tzinfo
from typing import Dict, Any, List

from data_aggregator_sdk.constants.enums import SensorType
from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageSensor

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (128 bits)   smpm_ul_device_energy_16b_electricity_params
#
# RESULT int:        47268593044936706359241417748435900
# RESULT bin:  MSB   00000000 00001001 00011010 10000101 10000101 10000101 01101110 00110111 00011011 10000100 10001101 00010010 00110100 01001000 11010011 10111100   LSB
# RESULT hex:  LE    bc d3 48 34 12 8d 84 1b 37 6e 85 85 85 1a 09 00
#
# name                  type    size  value(int)                                                                                                                        data(bits)
# --------------------  ------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------
# packet_type_id.0.VAL  u7         7          60                                                                                                                           0111100
# packet_type_id.0.DFF  bool       1           1                                                                                                                          1
# packet_type_id.1.VAL  u2         2           3                                                                                                                        11
# packet_type_id.1.DFF  bool       1           0                                                                                                                       0
# current_ch_1          uf14p2    14        2330                                                                                                         00100100011010
# current_ch_2          uf14p2    14        2330                                                                                           00100100011010
# current_ch_3          uf14p2    14        2330                                                                             00100100011010
# voltage_ch1           u9         9         220                                                                    011011100
# voltage_ch2           u9         9         220                                                           011011100
# voltage_ch3           u9         9         220                                                  011011100
# k_ch1                 uf8p2      8         133                                          10000101
# k_ch2                 uf8p2      8         133                                  10000101
# k_ch3                 uf8p2      8         133                          10000101
# freq                  uf12p2    12        2330              100100011010
# RESERVED              u12       12           0  000000000000


class SmpmUlDeviceEnergy16BElectricityParamsData(Packet):
    current_ch_1: float
    current_ch_2: float
    current_ch_3: float
    voltage_ch1: int
    voltage_ch2: int
    voltage_ch3: int
    k_ch1: float
    k_ch2: float
    k_ch3: float
    freq: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((60) & (2 ** (7) - 1)) << size
        size += 7
        result |= ((1) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((3) & (2 ** (2) - 1)) << size
        size += 2
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.current_ch_1, (int, float))
        assert 0.0 <= data.current_ch_1 <= 163.83
        result |= ((int(round(float(data.current_ch_1) * 100.0, 0))) & (2 ** (14) - 1)) << size
        size += 14
        assert isinstance(data.current_ch_2, (int, float))
        assert 0.0 <= data.current_ch_2 <= 163.83
        result |= ((int(round(float(data.current_ch_2) * 100.0, 0))) & (2 ** (14) - 1)) << size
        size += 14
        assert isinstance(data.current_ch_3, (int, float))
        assert 0.0 <= data.current_ch_3 <= 163.83
        result |= ((int(round(float(data.current_ch_3) * 100.0, 0))) & (2 ** (14) - 1)) << size
        size += 14
        assert isinstance(data.voltage_ch1, int)
        assert 0 <= data.voltage_ch1 <= 511
        result |= ((data.voltage_ch1) & (2 ** (9) - 1)) << size
        size += 9
        assert isinstance(data.voltage_ch2, int)
        assert 0 <= data.voltage_ch2 <= 511
        result |= ((data.voltage_ch2) & (2 ** (9) - 1)) << size
        size += 9
        assert isinstance(data.voltage_ch3, int)
        assert 0 <= data.voltage_ch3 <= 511
        result |= ((data.voltage_ch3) & (2 ** (9) - 1)) << size
        size += 9
        assert isinstance(data.k_ch1, (int, float))
        assert -1.0 <= data.k_ch1 <= 1.5499999999999998
        result |= ((int(round(float(data.k_ch1 - -1.0) * 100.0, 0))) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.k_ch2, (int, float))
        assert -1.0 <= data.k_ch2 <= 1.5499999999999998
        result |= ((int(round(float(data.k_ch2 - -1.0) * 100.0, 0))) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.k_ch3, (int, float))
        assert -1.0 <= data.k_ch3 <= 1.5499999999999998
        result |= ((int(round(float(data.k_ch3 - -1.0) * 100.0, 0))) & (2 ** (8) - 1)) << size
        size += 8
        assert isinstance(data.freq, (int, float))
        assert 30.0 <= data.freq <= 70.95
        result |= ((int(round(float(data.freq - 30.0) * 100.0, 0))) & (2 ** (12) - 1)) << size
        size += 12
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BElectricityParamsData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 60 != buf.shift(7):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 1 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 3 != buf.shift(2):
            raise ValueError("packet_type_id: buffer doesn't match value")
        if 0 != buf.shift(1):
            raise ValueError("packet_type_id: buffer doesn't match value")
        result__el_tmp1["current_ch_1"] = round(buf.shift(14) / 100.0, 2)
        result__el_tmp1["current_ch_2"] = round(buf.shift(14) / 100.0, 2)
        result__el_tmp1["current_ch_3"] = round(buf.shift(14) / 100.0, 2)
        result__el_tmp1["voltage_ch1"] = buf.shift(9) + 0
        result__el_tmp1["voltage_ch2"] = buf.shift(9) + 0
        result__el_tmp1["voltage_ch3"] = buf.shift(9) + 0
        result__el_tmp1["k_ch1"] = round(buf.shift(8) / 100.0 + -1.0, 2)
        result__el_tmp1["k_ch2"] = round(buf.shift(8) / 100.0 + -1.0, 2)
        result__el_tmp1["k_ch3"] = round(buf.shift(8) / 100.0 + -1.0, 2)
        result__el_tmp1["freq"] = round(buf.shift(12) / 100.0 + 30.0, 2)
        result = SmpmUlDeviceEnergy16BElectricityParamsData(**result__el_tmp1)
        buf.shift(12)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        sensors = [IntegrationV0MessageSensor(
            channel_id=1,
            sensor_type=SensorType.ENERGY_METER_CURRENT,
            value=Decimal(str(self.current_ch_1)),
        )]

        if self.current_ch_2 and self.current_ch_3:
            sensors.extend(
                [
                    IntegrationV0MessageSensor(
                        channel_id=1,
                        sensor_type=SensorType.ENERGY_METER_CURRENT,
                        value=Decimal(str(self.current_ch_2)),
                    ),
                    IntegrationV0MessageSensor(
                        channel_id=1,
                        sensor_type=SensorType.ENERGY_METER_CURRENT,
                        value=Decimal(str(self.current_ch_3)),
                    ),
                ],
            )

        sensors.append(
            IntegrationV0MessageSensor(
                channel_id=1,
                sensor_type=SensorType.ENERGY_METER_VOLTAGE,
                value=Decimal(str(self.voltage_ch1)),
            ),
        )

        if self.voltage_ch2 and self.voltage_ch3:
            sensors.extend(
                [
                    IntegrationV0MessageSensor(
                        channel_id=1,
                        sensor_type=SensorType.ENERGY_METER_VOLTAGE,
                        value=Decimal(str(self.voltage_ch2)),
                    ),
                    IntegrationV0MessageSensor(
                        channel_id=1,
                        sensor_type=SensorType.ENERGY_METER_VOLTAGE,
                        value=Decimal(str(self.voltage_ch3)),
                    ),
                ],
            )

        sensors.append(
            IntegrationV0MessageSensor(
                channel_id=1,
                sensor_type=SensorType.ENERGY_METER_POWER_FACTOR,
                value=Decimal(str(self.k_ch1)),
            ),
        )

        if self.k_ch2 and self.k_ch3:
            sensors.extend(
                [
                    IntegrationV0MessageSensor(
                        channel_id=1,
                        sensor_type=SensorType.ENERGY_METER_POWER_FACTOR,
                        value=Decimal(str(self.k_ch2)),
                    ),
                    IntegrationV0MessageSensor(
                        channel_id=1,
                        sensor_type=SensorType.ENERGY_METER_POWER_FACTOR,
                        value=Decimal(str(self.k_ch3)),
                    ),
                ],
            )

        sensors.append(
            IntegrationV0MessageSensor(
                channel_id=1,
                sensor_type=SensorType.ENERGY_METER_FREQUENCY,
                value=Decimal(str(self.freq)),
            ),
        )

        return [
            IntegrationV0MessageData(
                dt=received_at,
                sensors=sensors,
            ),
        ]
