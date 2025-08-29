import math
from datetime import datetime, timedelta


START_POINT = datetime(year=2020, month=1, day=1)


def timestamp_calculation(
        current_pack_time: datetime,
        timestamp: timedelta,
        overflow_clock_value_timedelta: timedelta,
        start_point: datetime = START_POINT,
) -> datetime:
    delta = int((current_pack_time.replace(tzinfo=None) - start_point).total_seconds())
    previous_overflow_value = delta // overflow_clock_value_timedelta.total_seconds() * overflow_clock_value_timedelta.total_seconds()
    value_slot_size = math.ceil(math.log2(int(overflow_clock_value_timedelta.total_seconds())))
    value_mask = (2 ** value_slot_size - 1)
    older_mask = (2 ** (64 - value_slot_size) - 1) << value_slot_size
    prev_result_i = int(previous_overflow_value) & (2 ** 64 - 1)
    input_value_i = int(timestamp.total_seconds()) & value_mask
    has_overflow = input_value_i & value_mask < prev_result_i & value_mask
    prev_result_ii = prev_result_i & older_mask
    result_i = prev_result_ii
    result_i |= input_value_i
    if has_overflow:
        result_i += 2 ** value_slot_size - 1
    if result_i > delta + 15 * 60 * 60:  # If device timezone is +14h + max unsynchronized delta(1h)
        result_i -= overflow_clock_value_timedelta.total_seconds()
    elif result_i < delta - 13 * 60 * 60:  # If device timezone is -12h + max unsynchronized delta(1h)
        result_i += overflow_clock_value_timedelta.total_seconds()
    return start_point + timedelta(seconds=result_i)
