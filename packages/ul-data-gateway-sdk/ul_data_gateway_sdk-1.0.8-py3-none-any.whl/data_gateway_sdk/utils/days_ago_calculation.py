from datetime import datetime, timedelta, time, tzinfo

from dateutil.relativedelta import relativedelta
from pytz import timezone


def days_ago_calculation(received_at: datetime, device_tz: tzinfo, days_ago_time: time, days_ago: timedelta | relativedelta) -> datetime:
    return (datetime.combine(
        (received_at.astimezone(device_tz) - days_ago).date(),
        days_ago_time,
        device_tz,
    ) + timedelta(days=1)).astimezone(timezone('UTC')) if days_ago else received_at
