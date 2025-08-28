import os
import datetime
import socket
import requests
from loguru import logger


def get_hostname():
    hostname = os.environ.get("HOSTALIAS", "")
    if hostname:
        return hostname
    return socket.gethostname()


def send_message(message, *, token, user_id, timeout=5, maxtry=3):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": user_id, "text": message, "parse_mode": "MarkdownV2"}
    try:
        for _ in range(maxtry):
            requests.post(url, params=params, timeout=timeout)
            return
    except Exception as e:
        logger.error(e)


def send_format_msg(message, *, token, user_id, timeout=5, maxtry=3):
    format_msg = "*{}来信@{}，内容如下*\n".format(
        get_hostname(), datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
    )
    format_msg += "```txt\n"
    format_msg += message + "\n"
    format_msg += "```"
    for k in ["-", ".", "~"]:
        format_msg = format_msg.replace(k, "\\" + k)
    send_message(
        format_msg, token=token, user_id=user_id, timeout=timeout, maxtry=maxtry
    )
