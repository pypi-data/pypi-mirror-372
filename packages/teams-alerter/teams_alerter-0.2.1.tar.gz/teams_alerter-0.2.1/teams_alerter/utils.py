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


def format_email_template_horse():
    email_object = "Contrôle DATASTREAM - Fiche cheval"
    email_message = """
        Bonjour, <br>
        Veuillez trouver ci-dessous le tableau récapitulatif du contrôle effectué sur la fiche cheval dans Datastream (champs formFigs et totalPrize) le 25/08/2025 à 13:15:00 UTC.
    """
    html = f"""
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f5f7fb;">
            <tr>
                <td align="center" style="padding:24px;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="max-width:100%; background:#ffffff; border-radius:8px; border:1px solid #e6e9ef;">
                    <tr>
                    <td style="text-align: center; padding-top: 12px;">
                        <img style="height: 24px;" src="https://upload.wikimedia.org/wikipedia/fr/f/fd/Logo_Paris_Turf.svg" alt="" srcset="">
                    </td>
                    </tr>

                    <tr>
                    <td style="padding:24px 24px 12px 24px; font-family:Segoe UI, Arial, sans-serif; font-size:20px; line-height:26px; color:#111827; font-weight:700;">
                        Objet : {email_object}
                    </td>
                    </tr>

                    <tr>
                    <td style="padding:0 24px 16px 24px; font-family:Segoe UI, Arial, sans-serif; font-size:14px; line-height:20px; color:#4b5563;">
                        {email_message}
                    </td>
                    </tr>

                    <tr>
                    <td style="padding:0 16px 24px 16px;">
                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-collapse:collapse; font-family:Segoe UI, Arial, sans-serif;">
                        <!-- Header -->
                        <tr>
                            <th align="left" style="padding:12px 10px; font-size:12px; line-height:16px; color:#374151; text-transform:uppercase; letter-spacing:.5px; border-bottom:2px solid #e5e7eb; background:#f9fafb;">ID cheval</th>
                            <th align="left" style="padding:12px 10px; font-size:12px; line-height:16px; color:#374151; text-transform:uppercase; letter-spacing:.5px; border-bottom:2px solid #e5e7eb; background:#f9fafb;">Champ</th>
                            <th align="left" style="padding:12px 10px; font-size:12px; line-height:16px; color:#374151; text-transform:uppercase; letter-spacing:.5px; border-bottom:2px solid #e5e7eb; background:#f9fafb;">Postgres</th>
                            <th align="left" style="padding:12px 10px; font-size:12px; line-height:16px; color:#374151; text-transform:uppercase; letter-spacing:.5px; border-bottom:2px solid #e5e7eb; background:#f9fafb;">Mongo</th>
                            <th align="left" style="padding:12px 10px; font-size:12px; line-height:16px; color:#374151; text-transform:uppercase; letter-spacing:.5px; border-bottom:2px solid #e5e7eb; background:#f9fafb;">Différence</th>
                        </tr>
                        <!-- Row 1 -->
                        <tr>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">12345</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">formFigs</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">8a 6a Da (24) 7a 8a 10a ...</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">Da (24) 7a 8a 10a ...</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">Début tronqué (8a 6a manquants)</td>
                        </tr>
                        <!-- Row 2 -->
                        <tr>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827;">123456</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827;">totalPrize</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827;">108220</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827;">108222</td>
                            <td style="padding:10px; font-size:14px; line-height:20px; color:#111827;">-2</td>
                        </tr>
                        </table>
                    </td>
                    </tr>

                    <tr>
                    <td style="padding:0 24px 16px 24px; font-family:Segoe UI, Arial, sans-serif; font-size:14px; line-height:20px; color:#4b5563;">
                        Cordialement,
                    </td>
                    </tr>

                    <tr>
                    <td style="padding:0 24px 24px 24px; font-family:Segoe UI, Arial, sans-serif; font-size:12px; line-height:18px; color:#6b7280;">
                        <div style="border-top:1px solid #eef2f7; padding-top:12px;text-align: center;">
                        Message automatique – ne pas répondre. <br>
                        © 2025 Paris-Turf – Tous droits réservés <br>
                        <a href="https://www.paris-turf.com">www.paris-turf.com</a>
                        </div>
                    </td>
                    </tr>
                </table>
                </td>
            </tr>
            </table>
    """
    return html
