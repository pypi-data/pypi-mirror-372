from typing import Dict, List, Any
from datetime import datetime, tzinfo
from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_warm_reset_v_fluo_freescale
#
# RESULT int:        8259
# RESULT bin:  MSB   0000000000000000000000000000000000000000000000000010000001000011   LSB
# RESULT hex:  LE    43 20 00 00 00 00 00 00
#
#
# name            type  size  value(int)                                                        data(bits)
# --------------------------------------------------------------------------------------------------------
# pack_id         u8       8          67                                                          01000011
# UNUSED          -        1           0                                                         0
# low_voltage     bool     1           0                                                        0
# UNUSED          -        3           0                                                     000
# watchdog_reset  bool     1           1                                                    1
# pin_reset       bool     1           0                                                   0
# power_on_reset  bool     1           0                                                  0
# UNUSED          -        2           0                                                00
# software_reset  bool     1           0                                               0
# RESERVED        u45     45           0  000000000000000000000000000000000000000000000


class Water5DeviceWarmResetVFluoFreescaleData(Packet):
    low_voltage: bool
    watchdog_reset: bool
    pin_reset: bool
    power_on_reset: bool
    software_reset: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((67) & (2 ** (8) - 1)) << size
        size += 8
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.low_voltage, bool)
        result |= ((int(data.low_voltage)) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (3) - 1)) << size
        size += 3
        assert isinstance(data.watchdog_reset, bool)
        result |= ((int(data.watchdog_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.pin_reset, bool)
        result |= ((int(data.pin_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.power_on_reset, bool)
        result |= ((int(data.power_on_reset)) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (2) - 1)) << size
        size += 2
        assert isinstance(data.software_reset, bool)
        result |= ((int(data.software_reset)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceWarmResetVFluoFreescaleData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 67 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        buf.shift(1)
        result__el_tmp1["low_voltage"] = bool(buf.shift(1))
        buf.shift(3)
        result__el_tmp1["watchdog_reset"] = bool(buf.shift(1))
        result__el_tmp1["pin_reset"] = bool(buf.shift(1))
        result__el_tmp1["power_on_reset"] = bool(buf.shift(1))
        buf.shift(2)
        result__el_tmp1["software_reset"] = bool(buf.shift(1))
        buf.shift(45)
        result = Water5DeviceWarmResetVFluoFreescaleData(**result__el_tmp1)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        return [
            IntegrationV0MessageData(
                dt=received_at,
                events=[
                    *([] if any((self.pin_reset, self.low_voltage, self.software_reset, self.watchdog_reset)) else [IntegrationV0MessageEvent.RESET]),
                    *([] if not self.pin_reset else [IntegrationV0MessageEvent.RESET_PIN]),
                    *([] if not self.low_voltage else [IntegrationV0MessageEvent.RESET_LOW_VOLTAGE]),
                    *([] if not self.software_reset else [IntegrationV0MessageEvent.RESET_SOFTWARE]),
                    *([] if not self.power_on_reset else [IntegrationV0MessageEvent.RESET_POWER_ON]),
                    *([] if not self.watchdog_reset else [IntegrationV0MessageEvent.RESET_WATCHDOG]),
                ],
            ),
        ]
