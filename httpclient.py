# reference blog:
# https://blog.csdn.net/lanyang123456/article/details/72594982
import json
from json import JSONDecodeError

import requests

from logutil import logger

# 如果开启了Charles或者Fiddler等代理软件
ssl_certificate = '/Users/liyutao/Library/Application Support/Charles/ca/charles-proxy-ssl-proxying-certificate.pem'
charles_proxies = {
    "http": "http://127.0.0.1:8888",
    "https": "https://127.0.0.1:8888"
}


def get(url, data=None, headers=None, proxies=None, verify=None, timeout=15):
    if headers is None:
        headers = {}
    if data is None:
        data = {}
    if proxies is None:
        proxies = {}
    logger.debug("execute request: method: get, url: %s, params: %s, headers: %s"
                 % (url, str(data), str(headers)))
    try:
        return requests.get(url, params=data, headers=headers, proxies=proxies, verify=verify, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        logger.error('[Connect Timeout]连接超时')
        return None
    except requests.exceptions.ReadTimeout:
        logger.error('[Read Timeout]响应超时')
        return None


def post(url, data, headers=None, proxies=None, verify=None, timeout=15):
    if headers is None:
        headers = {}
    if data is None:
        data = {}
    if proxies is None:
        proxies = {}
    logger.debug("execute request: method: post, url: %s, params: %s, headers: %s"
                 % (url, str(data), str(headers)))
    try:
        return requests.post(url, data=data, headers=headers, proxies=proxies, verify=verify, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        logger.error('[Connect Timeout]连接超时')
        return None
    except requests.exceptions.ReadTimeout:
        logger.error('[Read Timeout]响应超时')
        return None


def response_body_to_json_object(body):
    json_string = bytes.decode(body)
    try:
        return json.loads(json_string)
    except JSONDecodeError:
        logger.error("解析出错的Json内容为: " + json_string)
        raise RuntimeError("解析 Json 字符串出错")


if __name__ == "__main__":
    logger.info('[Start]开始请求 Google.com')
    get('https://www.google.com', timeout=2)
