import time
from datetime import datetime

import pytz

__timezone = None
"""The default timezone. Use TimeUtil.set_default_timezone in a global context before making use of TimeUtil."""


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class TimeUtil:
    """
    A class that contains various date/time related utility methods. All times are based off of the timezone from
    the timezone() function. The default timezone is set by the timezone variable above this class definition.
    Since this is a global variable, every endpoint from the same server instance will use it. If you need to change
    the timezone, then call TimeUtil.set_default_timezone() somewhere in a global context in your server. A list of
    valid timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_database_time_zones.

    If a timezone that is different from the default is needed but you don't want to change the default, a timezone name
    or UTC offset in seconds may be provided to each function. A UTC offset can be found at
    context.user.session_additional_data.utc_offset_seconds.

    Note that static date fields display their time in UTC instead of in whatever the server's time is. So when dealing
    with static date fields, use "UTC" as your input timezone.
    """
    @staticmethod
    def get_default_timezone():
        """
        Returns the timezone that TimeUtil is currently using as its default.
        """
        global __timezone
        return __timezone

    @staticmethod
    def set_default_timezone(new_timezone: str | int) -> None:
        """
        Set the timezone used by TimeUtil to something new.

        :param new_timezone: The timezone to set the default to. A list of valid timezones can be found at
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. May also accept a UTC offset in seconds.
        """
        global __timezone
        __timezone = TimeUtil.__to_tz(new_timezone)

    @staticmethod
    def __to_tz(timezone: str | int = None):
        """
        :param timezone: Either the name of a timezone, a UTC offset in seconds, or None if the default should be used.
        :return: The timezone object to use for the given input. If the input is None, uses the default timezone.
        """
        if isinstance(timezone, str):
            # PR-46571: Convert timezones to a UTC offset and then use that offset as the timezone. This is necessary
            # because pytz may return timezones from strings in Local Mean Time instead of a timezone with a UTC offset.
            # LMT may be a few minutes off of the actual time in that timezone right now.
            # https://stackoverflow.com/questions/35462876
            offset: int = int(datetime.now(pytz.timezone(timezone)).utcoffset().total_seconds() / 60)
            return pytz.FixedOffset(offset)
        if isinstance(timezone, int):
            return pytz.FixedOffset(timezone // 60)
        return TimeUtil.get_default_timezone()

    @staticmethod
    def current_time(timezone: str | int = None) -> datetime:
        """
        The current time as a datetime object.

        :param timezone: The timezone to initialize the current time with. If no timezone is provided, uses the global
            timezone variable set by the TimeUtil. A list of valid timezones can be found at
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. May also accept a UTC offset in seconds.
        """
        tz = TimeUtil.__to_tz(timezone)
        return datetime.now(tz)

    @staticmethod
    def now_in_millis() -> int:
        """
        The current time in milliseconds since the epoch.
        """
        return round(time.time() * 1000)

    @staticmethod
    def now_in_format(time_format: str, timezone: str | int = None) -> str:
        """
        The current time in some date format.

        :param time_format: The format to display the current time in. Documentation for how the time formatting works
            can be found at https://docs.python.org/3.10/library/datetime.html#strftime-and-strptime-behavior
        :param timezone: The timezone to initialize the current time with. If no timezone is provided, uses the global
            timezone variable set by the TimeUtil. A list of valid timezones can be found at
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. May also accept a UTC offset in seconds.
        """
        return TimeUtil.current_time(timezone).strftime(time_format)

    @staticmethod
    def millis_to_format(millis: int, time_format: str, timezone: str | int = None) -> str:
        """
        Convert the input time in milliseconds to the provided format.

        :param millis: The time in milliseconds to convert from.
        :param time_format: The format to display the input time in. Documentation for how the time formatting works
            can be found at https://docs.python.org/3.10/library/datetime.html#strftime-and-strptime-behavior
        :param timezone: The timezone to initialize the current time with. If no timezone is provided, uses the global
            timezone variable set by the TimeUtil. A list of valid timezones can be found at
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. May also accept a UTC offset in seconds.
        """
        tz = TimeUtil.__to_tz(timezone)
        return datetime.fromtimestamp(millis / 1000, tz).strftime(time_format)

    @staticmethod
    def format_to_millis(time_point: str, time_format: str, timezone: str | int = None) -> int:
        """
        Convert the input time from the provided format to milliseconds.

        :param time_point: The time in some date/time format to convert from.
        :param time_format: The format that the time_point is in. Documentation for how the time formatting works
            can be found at https://docs.python.org/3.10/library/datetime.html#strftime-and-strptime-behavior
        :param timezone: The timezone to initialize the current time with. If no timezone is provided, uses the global
            timezone variable set by the TimeUtil. A list of valid timezones can be found at
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. May also accept a UTC offset in seconds.
        """
        tz = TimeUtil.__to_tz(timezone)
        return int(datetime.strptime(time_point, time_format).replace(tzinfo=tz).timestamp() * 1000)

    # FR-46154: Create a function that determines if a string matches a time format.
    @staticmethod
    def str_matches_format(time_point: str, time_format: str) -> bool:
        """
        Determine if the given string is recognized as a valid time in the given format.

        :param time_point: The time in some date/time format to check.
        :param time_format: The format that the time_point should be in. Documentation for how the time formatting works
            can be found at https://docs.python.org/3.10/library/datetime.html#strftime-and-strptime-behavior
        """
        try:
            # If this function successfully runs, then the time_point matches the time_format.
            TimeUtil.format_to_millis(time_point, time_format, "UTC")
            return True
        except Exception:
            return False
