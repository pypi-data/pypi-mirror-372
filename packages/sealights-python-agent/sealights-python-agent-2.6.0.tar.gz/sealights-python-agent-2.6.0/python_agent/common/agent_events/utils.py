import datetime


def get_utc_time_in_ms():
    now = datetime.datetime.utcnow()
    return int(now.timestamp() * 1000)
