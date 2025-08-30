"""Utility functions for parsing and formatting time in plugins

If you're wondering why we're multiplying by 1000,
it's because Argus is written in Java and requires milis, not seconds.
"""
from argparse import ArgumentTypeError
from datetime import datetime, timedelta

import dateparser


def time_parser(datetime_string: str):
    """Turns a human readable time string into a datetime object.

    NOTE
    ====
    This is strictly a helper. If you want to have a normal datetime object
    in your code. Please just reference to a datetime object. Example:

    >>> def my_funky_func(start: datetime): pass

    All parsing will be done for you, so don't worry about that.

    :param datetime_string: DateTime string that will be parsed
    :return:
    """
    parsed = dateparser.parse(datetime_string)

    if parsed is None:
        raise ArgumentTypeError(
            "Could not parse provided time string."
            "\n\n"
            "A lot of different formats are supported. Both absolute and "
            "relative time strings. Here are some examples:\n"
            '"2 weeks ago", "1 minute ago", "2019-01-27", '
            '"1st of August 10:15 pm".'
            "\n\n"
            "If you have spaces in the time string, make sure that it is "
            'surrounded by a pair of double quotes ("like this")'
        )

    return parsed


def date_or_relative(datetime_string: str):
    """Convince function that merges date-time and time diff formats"""
    return int(time_parser(datetime_string).timestamp() * 1e3)


def time_diff(datetime_string: str):
    """Converts the input from one unit to milliseconds"""
    parsed_input = time_parser(datetime_string)
    return int((datetime.now() - parsed_input).total_seconds() * 1e3)


def timestamp_to_period(timestamp: int, format="iso"):
    """Converts a timestamp to a ISO8601 style period with days"""
    clock_time = datetime.utcfromtimestamp(timestamp)
    if format == "iso":
        return "P{days:03}DT{hours:02}:{minutes:02}:{seconds:02}".format(
            days=timedelta(seconds=timestamp).days,
            hours=clock_time.hour,
            minutes=clock_time.minute,
            seconds=clock_time.second,
        )
    if format == "minutes":
        return "{minutes} minutes".format(
            minutes=timedelta(seconds=timestamp).total_seconds() // 60,
        )


def timestamp_to_date(timestamp: int):
    """Converts a timestamp to a ISO8601 style date and time"""
    return datetime.fromtimestamp(timestamp).isoformat()


def datetime_to_week_number(dt: datetime) -> str:
    """returns the week number a datetime is in as 0-padded string."""
    return dt.strftime("%W")
