"""
Name : gm_request_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-20 13:40
Desc: 封装requests请求方法get、post、put、delete、options、head
"""


import requests


def send_get_request(request, url, headers=None, params=None, data=None, json=None, verify=False):
    response = request.get(url=url, headers=headers, params=params, data=data, json=json,
                               verify=verify)
    return response

def send_post_request(request, url, headers=None, params=None, data=None, json=None, verify=False):
    response = request.post(url=url, headers=headers, params=params, data=data, json=json,
                               verify=verify)
    return response

def send_put_request(request, url, headers=None, params=None, data=None, json=None, verify=False):
    response = request.put(url=url, headers=headers, params=params, data=data, json=json,
                               verify=verify)
    return response

def send_delete_request(request, url, headers=None, params=None, data=None, json=None, verify=False):
    response = request.delete(url=url, headers=headers, params=params, data=data, json=json,
                               verify=verify)
    return response

def send_options_request(request, url, headers=None, params=None, data=None, json=None, verify=False):
    response = request.options(url=url, headers=headers, params=params, data=data, json=json,
                               verify=verify)
    return response

def send_head_request(request, url, headers=None, params=None, data=None, json=None, verify=False ):
    response = request.head(url=url, headers=headers, params=params, data=data, json=json,
                               verify=verify)
    return response
