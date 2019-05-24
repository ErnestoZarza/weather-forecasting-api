from datetime import datetime

UNITS = {"temperature": "°C", "pressure": "hPa", "humidity": "%"}


def is_valid_date(date):
    """This methos determines if a date is
    within a range of 5 days from the current date"""
    delta = date - datetime.now()
    return 5 > delta.days > 0
