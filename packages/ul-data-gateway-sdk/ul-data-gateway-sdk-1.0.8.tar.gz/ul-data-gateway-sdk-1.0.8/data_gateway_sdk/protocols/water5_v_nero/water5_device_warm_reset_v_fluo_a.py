from typing import Dict, List, Any
from datetime import datetime, tzinfo

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData


from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_warm_reset_v_fluo_a
#
# RESULT int:        188978561091
# RESULT bin:  MSB   0000000000000000000000000010110000000000000000000000000001000011   LSB
# RESULT hex:  LE    43 00 00 00 2c 00 00 00
#
#
# name            type  size  value(int)                                                        data(bits)
# --------------------------------------------------------------------------------------------------------
# pack_id         u8       8          67                                                          01000011
# UNUSED          -       24           0                                  000000000000000000000000
# UNUSED          -        2           0                                00
# pin_reset       bool     1           1                               1
# low_voltage     bool     1           1                              1
# software_reset  bool     1           0                             0
# watchdog_reset  bool     1           1                            1
# RESERVED        u26     26           0  00000000000000000000000000


class Water5DeviceWarmResetVFluoAData(Packet):
    pin_reset: bool
    low_voltage: bool
    software_reset: bool
    watchdog_reset: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((67) & (2 ** (8) - 1)) << size
        size += 8
        result |= ((0) & (2 ** (24) - 1)) << size
        size += 24
        result |= ((0) & (2 ** (2) - 1)) << size
        size += 2
        assert isinstance(data.pin_reset, bool)
        result |= ((int(data.pin_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.low_voltage, bool)
        result |= ((int(data.low_voltage)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.software_reset, bool)
        result |= ((int(data.software_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.watchdog_reset, bool)
        result |= ((int(data.watchdog_reset)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceWarmResetVFluoAData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 67 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        buf.shift(24)
        buf.shift(2)
        result__el_tmp1["pin_reset"] = bool(buf.shift(1))
        result__el_tmp1["low_voltage"] = bool(buf.shift(1))
        result__el_tmp1["software_reset"] = bool(buf.shift(1))
        result__el_tmp1["watchdog_reset"] = bool(buf.shift(1))
        buf.shift(26)
        result = Water5DeviceWarmResetVFluoAData(**result__el_tmp1)
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
                    *([] if not self.watchdog_reset else [IntegrationV0MessageEvent.RESET_WATCHDOG]),
                ],
            ),
        ]
