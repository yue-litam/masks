import datetime
import json

import config
from httpclient import post
from httpclient import response_body_to_json_object as decode_response_as_json
from logutil import logger

YOUR_ID_TYPE = '身份证'
URI_STATUS_CHECK = config.URI_DOMAIN + "/preorder/status"
URI_CONFIRM_ORDER = config.URI_DOMAIN + "/preorder/add"
header = {
    "sessionid": config.LOGIN_SESSION_ID,
    "Content-Type": "application/json",
    "Accept-Language": "zh-cn",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Mobile/15E148 MicroMessenger/7.0.10(0x17000a21) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wx2ac2313767a99df9/25/page-frame.html",
    "appid": "microService-GUANGZHOU",
}
comfirm_order_data = {
    "name": config.YOUR_NAME,
    "identity": config.YOUR_IDNO,
    "identityType": YOUR_ID_TYPE,
    "idcard": YOUR_ID_TYPE + "," + config.YOUR_IDNO,
    "mobile": config.YOUR_MOBILE,
    "changeable": "yes",
    "time_code": "0",
    "wxmsg": 2,
    "mail_address": "",
    "zone": "广州市",
    "shop_id": "GZ0001"
}


def check_success_or_not(response):
    if response is None:
        return None
    if response.status_code == 200:
        result = decode_response_as_json(response.content)
        if result['errcode'] == 0:
            return result
        elif result['errcode'] == 400:
            logger.info('本轮预约未开始，下单失败。')
        else:
            logger.warning("errcode:" + str(result['errcode']))
            logger.warning("errmsg :" + str(result['errmsg']))
            logger.warning("detail :" + str(result['detailErrMsg']))
    else:
        logger.error('http status_code: ' + str(response.status_code))
    return None


def check_status():
    data = {
        "city_id": 20
    }
    response = post(URI_STATUS_CHECK,
                    data=json.dumps(data),
                    headers=header,
                    timeout=config.CEHCK_STATUS_TIMEOUT_SECONDS)
    result = check_success_or_not(response)
    if result is not None:
        status = result['data']['status']
        if status == 'preorder':
            return True
        elif status == 'finish':
            yesterday = datetime.date.today() + datetime.timedelta(days=-1)
            yesterday_str = str(yesterday.year) + str(yesterday.month) + str(yesterday.day)
            logger.info('本轮预约未开始。上一轮(' + yesterday_str + ')预约已结束。')
        elif status == 'wait':
            logger.info('本轮预约未开始。')
        else:
            exit(1)
    return False


def comfire_order(cat=0):
    data = comfirm_order_data.copy()
    if cat == 1:
        data['category'] = '普通N95口罩'
        data['commodity_id'] = '100005'
        data['number'] = 5
    elif cat == 2:
        data['category'] = '普通防护口罩'
        data['commodity_id'] = '100006'
        data['number'] = 10
    else:
        logger.warning('unknown mask category.')
        return False
    jstr = json.dumps(data, ensure_ascii=False)
    byte = jstr.encode('utf-8')
    response = post(URI_CONFIRM_ORDER,
                    data=byte,
                    headers=header,
                    timeout=config.ORDER_TIMEOUT_SECONDS)
    result = check_success_or_not(response)
    if result is not None:
        status = result['data']['status']
        if status == 'success':
            logger.info('预约成功！')
            return True
        else:
            logger.warn('unknown status: ' + status)
    return False
