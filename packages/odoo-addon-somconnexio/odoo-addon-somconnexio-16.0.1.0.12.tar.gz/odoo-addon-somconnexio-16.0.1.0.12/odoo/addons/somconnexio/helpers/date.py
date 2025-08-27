from datetime import date, timedelta
import calendar


def first_day_this_month():
    today = date.today()
    return today.replace(day=1)


def first_day_next_month():
    today = date.today()
    if today.month == 12:
        first_day = date(day=1, month=1, year=today.year + 1)
    else:
        first_day = today.replace(day=1, month=today.month + 1)
    return first_day


def last_day_of_this_month():
    return first_day_next_month() - timedelta(days=1)


def last_day_of_month_of_given_date(given_date):
    last_day = calendar.monthrange(given_date.year, given_date.month)[1]
    return given_date.replace(day=last_day)


def date_to_str(date):
    return date.strftime("%Y-%m-%d")
