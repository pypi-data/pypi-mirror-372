from typing import Dict, List, Any
from datetime import datetime, tzinfo

from data_aggregator_sdk.constants.enums import IntegrationV0MessageEvent
from data_aggregator_sdk.integration_message import IntegrationV0MessageData

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.packet import Packet


# PACKET (64 bits)   water5_device_warm_reset_v_metano_a
#
# RESULT int:        9795
# RESULT bin:  MSB   00000000 00000000 00000000 00000000 00000000 00000000 00100110 01000011   LSB
# RESULT hex:  LE    43 26 00 00 00 00 00 00
#
# name              type  size  value(int)                                                        data(bits)
# ----------------  ----  ----  ----------  ----------------------------------------------------------------
# pack_id           u8       8          67                                                          01000011
# UNUSED            -        1           0                                                         0
# watchdog_reset    bool     1           1                                                        1
# low_voltage       bool     1           1                                                       1
# software_reset    bool     1           0                                                      0
# UNUSED            -        1           0                                                     0
# pin_reset         bool     1           1                                                    1
# UNUSED            -        1           0                                                   0
# hard_fault_error  bool     1           0                                                  0
# RESERVED          u48     48           0  000000000000000000000000000000000000000000000000


class Water5DeviceWarmResetVMetanoAData(Packet):
    watchdog_reset: bool
    low_voltage: bool
    software_reset: bool
    pin_reset: bool
    hard_fault_error: bool

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        result |= ((67) & (2 ** (8) - 1)) << size
        size += 8
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.watchdog_reset, bool)
        result |= ((int(data.watchdog_reset)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.low_voltage, bool)
        result |= ((int(data.low_voltage)) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.software_reset, bool)
        result |= ((int(data.software_reset)) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.pin_reset, bool)
        result |= ((int(data.pin_reset)) & (2 ** (1) - 1)) << size
        size += 1
        result |= ((0) & (2 ** (1) - 1)) << size
        size += 1
        assert isinstance(data.hard_fault_error, bool)
        result |= ((int(data.hard_fault_error)) & (2 ** (1) - 1)) << size
        size += 1
        return result.to_bytes(8, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'Water5DeviceWarmResetVMetanoAData':
        result__el_tmp1: Dict[str, Any] = dict()
        if 67 != buf.shift(8):
            raise ValueError("pack_id: buffer doesn't match value")
        buf.shift(1)
        result__el_tmp1["watchdog_reset"] = bool(buf.shift(1))
        result__el_tmp1["low_voltage"] = bool(buf.shift(1))
        result__el_tmp1["software_reset"] = bool(buf.shift(1))
        buf.shift(1)
        result__el_tmp1["pin_reset"] = bool(buf.shift(1))
        buf.shift(1)
        result__el_tmp1["hard_fault_error"] = bool(buf.shift(1))
        buf.shift(48)
        result = Water5DeviceWarmResetVMetanoAData(**result__el_tmp1)
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
                    *([] if not self.hard_fault_error else [IntegrationV0MessageEvent.RESET_HARD_FAULT]),
                ],
            ),
        ]
