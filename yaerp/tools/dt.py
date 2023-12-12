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
        input = input.lower().strip()
        if date_time:
            cdt = date_time
        else:
            tz = tzlocal()
            cdt = datetime.now(tz=tz)
        if zeroed_time:
            cdt = datetime(year=cdt.year, month=cdt.month, day=cdt.day, tzinfo=cdt.tzinfo)
        match(input):
            case 'now':
                pass
            case 'today':
                pass
            case 'yesterday':
                cdt = cdt + relativedelta(days=-1)
            case 'tomorrow':
                cdt = cdt + relativedelta(days=+1)
            case 'prev_week':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weeks=-1)
            case 'monday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=MO)
            case 'tuesday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=TU)
            case 'wednesday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=WE)
            case 'thursday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=TH)
            case 'friday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=FR)
            case 'saturday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=SA)
            case 'sunday':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weekday=SU)
            case 'next_week':
                cdt = dt(cdt, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(weeks=+1)
            case 'prev_month_first_day':
                cdt = dt(cdt, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(months=-1)
            case 'prev_month_last_day':
                cdt = dt(cdt, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(days=-1)
            case 'this_month_first_day':
                cdt = dt(cdt, day=1, zeroed_time=zeroed_time)
            case 'this_month_last_day':
                cdt = dt(cdt, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(months=+1, days=-1)
            case 'next_month_first_day':
                cdt = dt(cdt, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(months=+1)
            case 'next_month_last_day':
                cdt = dt(cdt, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(months=+2, seconds=-1)
            case 'prev_year_first_day':
                cdt = dt(cdt, month=1, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(years=-1)
            case 'this_year_first_day':
                cdt = dt(cdt, month=1, day=1, zeroed_time=zeroed_time)
            case 'next_year_first_day':
                cdt = dt(cdt, month=1, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(years=+1)
            case 'prev_year_last_day':
                cdt = dt(cdt, month=1, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(days=-1)
            case 'this_year_last_day':
                cdt = dt(cdt, month=1, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(years=+1, days=-1)
            case 'next_year_last_day':
                cdt = dt(cdt, month=1, day=1, zeroed_time=zeroed_time)
                cdt = cdt + relativedelta(years=+2, days=-1)
            case __:
                raise ValueError(f'unknown "{__}"')
        return cdt