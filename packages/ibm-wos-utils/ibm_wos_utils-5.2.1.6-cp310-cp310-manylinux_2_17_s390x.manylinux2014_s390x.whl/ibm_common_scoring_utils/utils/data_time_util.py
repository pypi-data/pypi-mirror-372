# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
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