from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from dateutil.tz import *
from dateutil.relativedelta import *


def dt(cdt: datetime, 
       year=None, month=None, day=None,
       hour=None, minute=None, second=None, microsecond=None, 
       zeroed_time=False) -> datetime:
    
    c_year = year if year is not None  else cdt.year
    c_month = month if month is not None  else cdt.month
    c_day = day if day is not None  else cdt.day
    if zeroed_time:
        c_hour = 0
        c_minute = 0
        c_second = 0
        c_microsecond = 0
    else:    
        c_hour = hour if hour is not None  else cdt.hour
        c_minute = minute if minute is not None  else cdt.minute
        c_second = second if second is not None  else cdt.second
        c_microsecond = microsecond if microsecond is not None  else cdt.microsecond
    c_tz = cdt.tzinfo
    return datetime(year=c_year, month=c_month, day=c_day,
                    hour=c_hour, minute=c_minute, second=c_second,
                    microsecond=c_microsecond, tzinfo=c_tz)

def datetime_str(input: str, date_time=None, zeroed_time=False) -> datetime:
        if not input:
            raise ValueError
        input = input.upper().strip()
        if date_time:
            cdt = date_time
        else:
            tz = tzlocal()
            cdt = datetime.now(tz=tz)
            # reset microseconds
            cdt = datetime(year=cdt.year, month=cdt.month, day=cdt.day,
                           hour=cdt.hour, minute=cdt.minute, second=cdt.second,
                           tzinfo=cdt.tzinfo)
        if zeroed_time:
            cdt = datetime(year=cdt.year, month=cdt.month, day=cdt.day, tzinfo=cdt.tzinfo)
        match(input):
            case 'NOW':
                pass
            case 'TODAY':
                cdt = dt(cdt, zeroed_time=True)
            case 'YESTERDAY':
                cdt = dt(cdt, zeroed_time=True)
                cdt = cdt + relativedelta(days=-1)
            case 'TOMORROW':
                cdt = dt(cdt, zeroed_time=True)
                cdt = cdt + relativedelta(days=+1)
            case 'FDPM':
                cdt = dt(cdt, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(months=-1)
            case 'LDPM':
                cdt = dt(cdt, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(days=-1)
            case 'FDTM':
                cdt = dt(cdt, day=1, zeroed_time=True)
            case 'LDTM':
                cdt = dt(cdt, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(months=+1, days=-1)
            case 'FDNM':
                cdt = dt(cdt, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(months=+1)
            case 'LDNM':
                cdt = dt(cdt, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(months=+2, seconds=-1)
            case 'FDPY':
                cdt = dt(cdt, month=1, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(years=-1)
            case 'LDPY':
                cdt = dt(cdt, month=1, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(days=-1)
            case 'LSPY':
                cdt = dt(cdt, month=1, day=1, hour=23, minute=59, second=59, microsecond=0)
                cdt = cdt + relativedelta(days=-1)    
            case 'FDTY':
                cdt = dt(cdt, month=1, day=1, zeroed_time=True)
            case 'LDTY':
                cdt = dt(cdt, month=1, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(years=+1, days=-1)
            case 'LSTY':
                cdt = dt(cdt, month=1, day=1, hour=23, minute=59, second=59, microsecond=0)
                cdt = cdt + relativedelta(years=+1, days=-1)    
            case 'FDNY':
                cdt = dt(cdt, month=1, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(years=+1)
            case 'LDNY':
                cdt = dt(cdt, month=1, day=1, zeroed_time=True)
                cdt = cdt + relativedelta(years=+2, days=-1)
            case 'LSNY':
                cdt = dt(cdt, month=1, day=1, hour=23, minute=59, second=59, microsecond=0)
                cdt = cdt + relativedelta(years=+2, days=-1)
            case __:
                return __
        return cdt.isoformat(sep=' ', timespec='seconds')
        