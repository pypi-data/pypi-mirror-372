from .stdlib.datetime import date, time, datetime

try:
    from dbf import Date, Time, DateTime
    dates = Date, date
    times = Time, time
    datetimes = DateTime, datetime
except ImportError:
    dates = date,
    times = time,
    datetimes = datetime,

moments = dates + times + datetimes
