import datetime

from typing import TypedDict
from google.cloud import logging


class ErrorUtils(TypedDict):
    logger: logging.Logger
    env: str
    app_project_id: str
    topic_project_id: str
    topic_id: str
    app_name: str
    teams_channel: str


class DateUtils:
    @staticmethod
    def get_str_utc_timestamp():
        dt = datetime.datetime.utcnow()
        return dt.strftime("%Y-%m-%dT%H:%M:%S") + ".000000000Z"

    @staticmethod
    def get_str_utc_timestamp_minus_5min():
        dt = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        return dt.strftime("%Y-%m-%dT%H:%M:%S") + ".000000000Z"

    @staticmethod
    def get_str_utc_timestamp_plus_5min():
        dt = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        return dt.strftime("%Y-%m-%dT%H:%M:%S") + ".000000000Z"
