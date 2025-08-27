# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import datetime
import time


class DateUtil:

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    date_format_alt = "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def get_datetime_str_as_time(cls, str_time: str = None):
        if str_time is None:
            return datetime.datetime.strptime(DateUtil.get_current_datetime(), cls.date_format)

        try:
            return datetime.datetime.strptime(str_time, cls.date_format)
        except ValueError:
            date_format = cls.date_format_alt
            if "T" not in str_time:
                date_format = "%Y-%m-%d %H:%M:%S"
                if "." in str_time:
                    date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.datetime.strptime(str_time, date_format)

    @classmethod
    def get_current_datetime(cls):
        return datetime.datetime.utcnow()

    @classmethod
    def get_current_datetime_as_str(cls):
        now = datetime.datetime.utcnow()
        return now.strftime(cls.date_format)

    @classmethod
    def get_datetime_as_str(cls, date_time, format=None):
        if format is None:
            return date_time.strftime(cls.date_format)
        else:
            return date_time.strftime(format)

    @classmethod
    def get_current_datetime_alt(cls):
        now = datetime.datetime.utcnow()
        return now.strftime(cls.date_format_alt)

    @classmethod
    def get_time_diff_in_seconds(cls, from_time, to_time=None):
        if to_time is None:
            current_timestamp = DateUtil.get_current_datetime()
        else:
            current_timestamp = DateUtil.get_datetime_str_as_time(str(to_time))
        if isinstance(from_time, str):
            from_time = DateUtil.get_datetime_str_as_time(from_time)
        return (current_timestamp - from_time).total_seconds()
    
    @classmethod
    def get_datetime_with_time_delta(cls, time: str, unit: str, count: int, previous: bool=False) -> str:
        """
        Returns timestamp with delta calculated as per unit and count.
        :time: The timestamp from which the delta is to be calculated.
        :unit: The unit of time given.
        :count: The quantity of time for the delta.
        :previous: The boolean flag to indicate whether the delta is for the past or future.

        :returns: The timestamp with the delta accomodated.
        """
        time = DateUtil.get_datetime_str_as_time(time)

        difference = datetime.timedelta()
        if unit == "day":
            difference = datetime.timedelta(days=count)
        elif unit == "hour":
            difference = datetime.timedelta(hours=count)
        elif unit == "minute":
            difference = datetime.timedelta(minutes=count)
        elif unit == "second":
            difference = datetime.timedelta(seconds=count)
        elif unit == "microsecond":
            difference = datetime.timedelta(microseconds=count)

        time = (time + difference) if not previous else (time - difference)
        return time.strftime(cls.date_format)
