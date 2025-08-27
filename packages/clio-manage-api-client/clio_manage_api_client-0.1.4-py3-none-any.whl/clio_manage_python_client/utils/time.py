import datetime
import calendar

def end_of_the_month():
    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    last_day = datetime.date(today.year, today.month, last_day)
    return datetime.datetime.combine(last_day, datetime.time())
