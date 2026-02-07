from datetime import datetime,timezone
from zoneinfo import ZoneInfo

bangkok = ZoneInfo("Asia/Bangkok")

def now():
    return datetime.now(timezone.utc)


def convertThaiTime(utc_dt: datetime) -> datetime:
    local_dt = utc_dt.astimezone(bangkok)
    return local_dt

