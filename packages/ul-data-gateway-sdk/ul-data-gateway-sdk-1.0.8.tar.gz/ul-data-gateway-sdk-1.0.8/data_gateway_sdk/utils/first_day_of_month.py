from datetime import datetime, time, tzinfo

from dateutil.relativedelta import relativedelta


def first_day_of_month(dt: datetime, device_tz: tzinfo) -> datetime:
    return datetime.combine(dt + relativedelta(day=1), time(0), device_tz)
