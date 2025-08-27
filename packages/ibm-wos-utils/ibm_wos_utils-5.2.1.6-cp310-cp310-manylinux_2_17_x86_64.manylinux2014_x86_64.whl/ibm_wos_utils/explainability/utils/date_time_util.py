# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from time import time
from datetime import datetime


class DateTimeUtil:

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    @classmethod
    def current_milli_time(self):
        return round(time() * 1000)

    @classmethod
    def get_datetime_iso_format(cls, date):
        return date.strftime(cls.date_format)

    @classmethod
    def get_current_datetime(cls):
        return datetime.utcnow()

    @classmethod
    def get_datetime_db_format(cls, date):
        return date.strftime("%Y-%m-%d %H:%M:%S.%f")
