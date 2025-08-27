# coding:utf-8
import os
import hmac
import time
import socket
import base64
import hashlib
import datetime
import requests
from loguru import logger

local_data = {
    "url": "",
    "secret": "",
}


def setup(url="", secret=""):
    if url:
        local_data["url"] = url
    if secret:
        local_data["secret"] = secret


def gen_sign(timestamp, secret):
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def get_hostname():
    hostname = os.environ.get("HOSTALIAS", "")
    if hostname:
        return hostname
    return socket.gethostname()


def __send_post(msg):
    timestamp = int(time.time())
    sign = gen_sign(timestamp, local_data['secret'])

    params = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "content": {
            "text": msg
        },
    }

    requests.post(local_data['url'], json=params, timeout=5)


def send_message(msg, url="", secret="", maxtry=3, delay=3):
    setup(url.strip(), secret.strip())
    status = False
    for _ in range(maxtry):
        try:
            __send_post(msg)
            logger.info("send \n{}\n successful!", msg)
            status = True
            break
        except Exception as e:
            logger.error("{}", e)
            time.sleep(delay)
    if not status:
        logger.error("send {} fail!", msg)


def send_format_msg(msg, url="", secret="", maxtry=3, delay=3):
    os.environ["TZ"] = "Asia/Shanghai"
    format_msg = "{}来信@{}，内容如下\n".format(get_hostname(), datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))
    format_msg += "-" * 25 + "\n"
    format_msg += msg+"\n"
    format_msg += "-" * 25 + "\n"
    send_message(format_msg, url, secret, maxtry, delay)
