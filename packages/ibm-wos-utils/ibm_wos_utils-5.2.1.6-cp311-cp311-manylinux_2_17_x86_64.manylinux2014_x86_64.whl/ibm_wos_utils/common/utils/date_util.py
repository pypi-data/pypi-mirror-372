# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

from datetime import datetime, timedelta, timezone
import time


class DateUtil:

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    date_format_alt = "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def get_datetime_str_as_time(cls, str_time: str = None):
        if str_time is None:
            return datetime.strptime(DateUtil.get_current_datetime(), cls.date_format)

        try:
            return datetime.strptime(str_time, cls.date_format)
        except ValueError:
            date_format = cls.date_format_alt
            if "T" not in str_time:
                date_format = "%Y-%m-%d %H:%M:%S"
                if "." in str_time:
                    date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(str_time, date_format)
    
    @classmethod
    def current_milli_time(cls):
        return round(time.time() * 1000)

    @classmethod
    def get_current_datetime(cls, format: str=None):
        now = datetime.now(timezone.utc)
        return now.strftime(cls.date_format if format is None else format)

    @classmethod
    def get_current_datetime_as_str(cls):
        now = datetime.utcnow()
        return now.strftime(cls.date_format)

    @classmethod
    def get_datetime_as_str(cls, date_time, format=None):
        if format is None:
            return date_time.strftime(cls.date_format)
        else:
            return date_time.strftime(format)

    @classmethod
    def get_current_datetime_alt(cls):
        now = datetime.utcnow()
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

        difference = timedelta()
        if unit == "day":
            difference = timedelta(days=count)
        elif unit == "hour":
            difference = timedelta(hours=count)
        elif unit == "minute":
            difference = timedelta(minutes=count)
        elif unit == "second":
            difference = timedelta(seconds=count)
        elif unit == "microsecond":
            difference = timedelta(microseconds=count)

        time = (time + difference) if not previous else (time - difference)
        return time.strftime(cls.date_format)
    
    @classmethod
    def nano_to_iso(cls, nano_seconds: int) -> str:
        """
        Converts the given time in nano-seconds to the ISO format.
        :nano_seconds: The time in nano-seconds.

        :returns: The timestamp in ISO format.
        """
        timestamp = None

        # Converting nano-seconds to seconds.
        seconds = nano_seconds / 10**9

        # Converting seconds to a date-timestamp
        dt_object = datetime.fromtimestamp(seconds, timezone.utc)

        # Converting the date-timestamp to iso-format
        timestamp = f"{dt_object.isoformat(timespec='auto')}Z"

        return timestamp
    
    @classmethod
    def iso_to_nano(cls, timestamp: str) -> int:
        """
        Converts the given timestamp in ISO format to nano-seconds.
        :timestamp: The timestamp in ISO format.

        :returns: The time in nano-seconds.
        """
        nano = None

        dt_obj = datetime.strptime(timestamp, cls.date_format).astimezone(timezone.utc)
        timestamp_seconds = dt_obj.timestamp()
        nano = int(timestamp_seconds * 1e9)

        return nano
    
    @classmethod
    def divide_time_range(cls, start_time_str: str, end_time_str: str, parts: int, format: str=None):
        """
        Divides a time range into a specified number of parts.
        :start_time_str: Start time as string.
        :end_time_str: End time as string.
        :parts: Number of parts to divide the time range into.
        :format: The format in which the timestamps are given.

        Returns:
            list: A list of time strings representing the divisions.
        """
        divisions = []
        
        # Setting default format
        format = format if format is not None else cls.date_format

        # Changing the time string to datetime
        start_time = datetime.strptime(start_time_str, format)
        end_time = datetime.strptime(end_time_str, format)

        # Calculating the seconds within the given time window
        total_seconds = (end_time - start_time).total_seconds()

        # Dividing the time with number of parts to be formed
        interval_seconds = total_seconds / parts

        # Generating timestamps for eac part
        for i in range(parts + 1):
            current_seconds = interval_seconds * i
            current_time = start_time + timedelta(seconds=current_seconds)
            divisions.append(current_time.strftime(format))
        
        return divisions
