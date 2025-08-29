import typing

import math


class BufRef:
    def __init__(self, data: typing.Union[bytes, bytearray, int], starts_at: int = 0, stop_on_buffer_end: bool = False) -> None:
        self.value: typing.Union[bytes, bytearray] = data if not isinstance(data, int) else data.to_bytes(math.ceil(max(data.bit_length(), 1) / 8), "little")
        self._stop_on_buffer_end, self.ends_at = stop_on_buffer_end, starts_at

    def get_bits(self, *, size: int, start: int = 0) -> int:
        bytes_i, bit_i = (self.ends_at + start) // 8, (self.ends_at + start) % 8
        res_size, res, needable_len = 0, 0, bytes_i + math.ceil((bit_i + size) / 8)
        buf_len = len(self.value)
        for i in range(bytes_i, needable_len):
            if i >= buf_len:
                if self._stop_on_buffer_end:
                    break
                raise ValueError(f'buffer has no enough elements. {buf_len} < {needable_len}')
            s = min(8 - bit_i, size - res_size)
            res |= ((self.value[i] >> bit_i) & (2 ** s - 1)) << res_size
            res_size += s
            bit_i = 0
        return res

    def shift(self, size: int) -> int:
        bytes_i, bit_i = self.ends_at // 8, self.ends_at % 8
        res_size, res, needable_len = 0, 0, bytes_i + math.ceil((bit_i + size) / 8)
        buf_len = len(self.value)
        for i in range(bytes_i, needable_len):
            if i >= buf_len:
                if self._stop_on_buffer_end:
                    break
                raise ValueError(f'buffer has no enough elements. {buf_len} < {needable_len}')
            s = min(8 - bit_i, size - res_size)
            res |= ((self.value[i] >> bit_i) & (2 ** s - 1)) << res_size
            res_size += s
            bit_i = 0
        self.ends_at += res_size
        return res

    def get_last_bytes(self) -> bytes:
        size = len(self.value) * 8 - self.ends_at
        return self.get_bits(size=size).to_bytes(length=math.ceil(size / 8), byteorder="little")

    def offset(self, size: int) -> None:
        assert size >= 0, f'{size} was given'
        self.ends_at += size
