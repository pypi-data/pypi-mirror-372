import json
import traceback

from google.cloud import pubsub_v1
from .utils import ErrorUtils, DateUtils


class TeamsAlerter:

    def __init__(
        self,
        utils: ErrorUtils,
    ):
        self.utils = utils

    @staticmethod
    def handle_error(error: Exception, utils: ErrorUtils) -> None:
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        utc_timestamp = DateUtils.get_str_utc_timestamp()
        utc_timestamp_minus_5min = DateUtils.get_str_utc_timestamp_minus_5min()
        utc_timestamp_plus_5min = DateUtils.get_str_utc_timestamp_plus_5min()
        url_log = f"https://console.cloud.google.com/logs/query;cursorTimestamp={utc_timestamp};startTime={utc_timestamp_minus_5min};endTime={utc_timestamp_plus_5min}?referrer=search&hl=fr&inv=1&invt=Ab5Y1Q&project={utils['app_project_id']}"
        # detail = f"Error type: {error_type}\nError message: {error_message}\nError traceback: {error_traceback}"
        detail = {"type": error_type, "message": error_message, "traceback": error_traceback}
        level = "ERROR"

        teams_alerter = TeamsAlerter(utils)

        teams_alerter.publish_alert(detail, level, url_log, "card", utc_timestamp)

    def publish_alert(self, detail, level, url_log, teams_template, utc_timestamp):

        # Formatage du payload
        payload = json.dumps(
            {
                "app_name": self.utils["app_name"],
                "teams_channel": self.utils["teams_channel"],
                "detail": detail,
                "level": level,
                "environment": self.utils["env"],
                "url_log": url_log,
                "timestamp": utc_timestamp,
                "teams_template": teams_template,
            }
        )

        # Création d'un éditeur
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(self.utils["topic_project_id"], self.utils["topic_id"])

        # Message à publier
        data = payload.encode("utf-8")

        # Publier le message
        try:
            publish_future = publisher.publish(topic_path, data)
            publish_future.result()

        except Exception as e:
            self.utils["logger"](f"🟥Une erreur s'est produite lors de la publication du message : {e}")
