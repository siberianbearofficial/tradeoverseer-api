from calendar import isleap


def validate_price(price: str):
    price = price.strip().replace(',', '.')
    if len(price) > 10:
        raise ValueError('Invalid price. Should contain not more than 10 symbols.')
    if not price.replace('.', '').isdigit():
        raise ValueError('Invalid price. Should be a positive float (without "e").')
    float(price)
    return price


def validate_count(count: int):
    return count >= 0


def validate_period(period: str):
    period = period.strip().lower()
    if period not in ['year', 'month', 'day']:
        raise ValueError('Invalid period. Should be one of "year", "month", "day".')


def validate_year_offset(year_offset: int):
    return year_offset >= 0


def days_in_year(year: int):
    return 366 if isleap(year) else 365


def days_in_month(year: int, month: int):
    return 29 if (isleap(year) and month == 2) else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
