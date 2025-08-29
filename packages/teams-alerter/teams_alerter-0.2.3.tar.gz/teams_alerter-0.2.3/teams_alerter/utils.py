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


def format_email_template(email_object, email_message, table_data):
    html = f"""
        <html>
            <head lang="fr">
                <meta charset="utf-8">
                <meta name="x-apple-disable-message-reformatting">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Contrôle datastream</title>
            </head>
            <body style="margin:0; padding:0; background:#f5f7fb;">
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
                                    <td style="padding:0 24px 16px 24px; font-family:Segoe UI, Arial, sans-serif; font-size:14px; line-height:20px; color:#4b5563;">
                                        Env: <strong>INT</strong> <br>
                                        Timestamp: <time datetime="2025-08-25T13:15:00Z">2025-08-25T13:15:00Z</time> <br>
                                        Champs: <strong>formFigs et/ou totalPrize</strong>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding:0 16px 24px 16px;">
                                        {build_html_table(table_data)}
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
            </body>
        </html>
    """
    return html


def build_html_table(table_data: list):
    html_table = '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-collapse:collapse; font-family:Segoe UI, Arial, sans-serif;">'

    # format header
    html_table += "<tr>"
    for header in table_data[0]:
        html_table += f'<th style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">{header}</th>'
    html_table += "</tr>"

    # format rows
    for row in table_data[1:]:
        html_table += "<tr>"
        for cell in row:
            html_table += f'<td style="padding:10px; font-size:14px; line-height:20px; color:#111827; border-bottom:1px solid #bbbbbb;">{cell}</td>'
        html_table += "</tr>"

    html_table += "</table>"

    return html_table
