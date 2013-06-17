
import pytz
import datetime
from pytz import timezone
utc = pytz.utc
tzinfo = timezone('Europe/Berlin')

def parse_date(s, tzinfo = utc):
    """parse dates like 20121219T160000Z"""
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    hour = int(s[9:11])
    minute = int(s[11:13])
    second = int(s[13:15])
    return datetime.datetime(year, month, day, hour, minute, second, 0, tzinfo)
