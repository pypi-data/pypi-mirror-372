"""
Name : gm_oauth_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2025/8/29 11:23
Desc: 第三方调用djc-gateway/authing/oauth/token接口，用于获取oauth,返回bearer
"""
import base64
import json
import requests
from urllib3.exceptions import InsecureRequestWarning # 过滤ssl警告
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

def get_oauth(domain: str, original_string: str, grant_type: str = 'client_credentials', is_print=None) -> str:
    """
    第三方调用后返回oauth
    :param session: requests对象
    :param domain: 顶级域名,例如https://www.cqzcjetest3.gm
    :param original_string:  第三方传入字符串
    :param grant_type: GET参数，不传入则固定为‘client_credentials’
    :param is_print: 是否打印
    :return: 'bearer ' + result.get('access_token')
    """
    domain = domain.rstrip("/") + "/"

    token_url = domain + 'djc-gateway/authing/oauth/token'
    try:
        encoded_string = 'Basic ' + base64.b64encode(original_string.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': encoded_string
        }
        print(encoded_string)
        print(token_url)
    except Exception as e:
        raise RuntimeError(f"Failed to encode credentials: {e}") from e
    try:
        _coll_resp = requests.post(token_url, headers=headers, params={"grant_type": grant_type}, verify=False)
        print(_coll_resp.url)
        print(_coll_resp.headers)
        result = _coll_resp.json()
        print(result)
        access_token = result.get("access_token")
        _token = f"bearer {access_token}"
        if is_print:
            print(f"获取到token值：{_token}")
    except Exception as e:
        raise RuntimeError(f"Invalid JSON response from OAuth Api: {e}, Response body: {_coll_resp.text}") from e
    return _token


if __name__ == '__main__':
    original_string = 'xcj_app_yuzheng:123'
    domain = 'https://www.cqzcjshow.com'
    get_oauth(domain, original_string)
