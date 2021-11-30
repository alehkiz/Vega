import random
import time
from datetime import datetime
from dateutil import tz

def str_time_prop(start, end, format='%d-%m-%Y %H:%M:%S', prop=0):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def random_date(start, end):
    return str_time_prop(start, end, '%d-%m-%Y %H:%M:%S', prop = random.random())


def convert_from_utc_to_local(utc):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Sao_Paulo')
    if utc is None or utc is False:
        return None     

    return utc.replace(tzinfo=from_zone).astimezone(to_zone)