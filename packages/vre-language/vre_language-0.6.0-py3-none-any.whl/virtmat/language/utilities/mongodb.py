"""utility functions to work with mongodb"""
from datetime import datetime
from dateutil import tz


def get_iso_datetime(utc_datetime, timespec='seconds', add_tzinfo=True, sep='T'):
    """mongodb stores all times in UTC so we need to convert to ISO local"""
    if isinstance(utc_datetime, str):
        utc_datetime = datetime.fromisoformat(utc_datetime)
    utc_zone = tz.tzutc()
    our_zone = tz.tzlocal()
    loc_time = utc_datetime.replace(tzinfo=utc_zone).astimezone(our_zone)
    if not add_tzinfo:
        loc_time = loc_time.replace(tzinfo=None)
    return loc_time.isoformat(timespec=timespec, sep=sep)
