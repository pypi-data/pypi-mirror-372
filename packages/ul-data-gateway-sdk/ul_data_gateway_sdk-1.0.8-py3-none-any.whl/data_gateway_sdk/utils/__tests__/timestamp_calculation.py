from datetime import datetime, timedelta

import pytest

from data_gateway_sdk.utils.timestamp_calculation import timestamp_calculation


@pytest.mark.parametrize(
    'current_pack_time,pack_timestamp,overflow_clock_value_timedelta,expected',
    (
        (
            datetime(year=2023, month=3, day=7),
            timedelta(seconds=int('01111110101011101100111000', 2)),
            timedelta(seconds=int('11111111111111111111111111', 2)),
            datetime(2023, 3, 7, 2, 6, 47),
        ),
        (
            datetime(year=2023, month=1, day=11),
            timedelta(seconds=int('01101100101011101000111000', 2)),
            timedelta(seconds=int('11111111111111111111111111', 2)),
            datetime(2023, 1, 11, 11, 19, 19),
        ),
        (
            datetime(year=2022, month=1, day=2, hour=3),
            timedelta(seconds=int('11110001011111111000111000', 2)),
            timedelta(seconds=int('11111111111111111111111111', 2)),
            datetime(2022, 1, 2, 17, 22),
        ),
    ),
)
def test_timestamp_calculation_(current_pack_time: datetime, pack_timestamp: timedelta, overflow_clock_value_timedelta: timedelta, expected: datetime) -> None:
    assert timestamp_calculation(
        current_pack_time=current_pack_time,
        timestamp=pack_timestamp,
        overflow_clock_value_timedelta=overflow_clock_value_timedelta,
    ) == expected
