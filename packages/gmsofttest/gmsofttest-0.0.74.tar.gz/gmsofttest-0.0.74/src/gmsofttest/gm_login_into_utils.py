"""
Name : gm_login_into_utils.py
Author  : 池泽琴
Contact : 邮箱地址
Time    : 2025-04-21 16:49
Desc:获取登录单位信息、用户信息
"""
import json

from gmsofttest.gm_login2_utils import LoginDomain


def get_login_org_id(session, env, host):
    # 获取当前登录用户的单位ID
    # _headers = {
    #     "Content-Type": "application/json;charset=UTF-8",
    #     "Accept": "application/json;charset=UTF-8",
    #     'Authorization': "bearer " + token
    # }
    login_domain = f'{env}_{host}'  # 根据env参数替换环境 test1_xcj
    url = getattr(LoginDomain, login_domain).value + "gateway/v1/user"
    print(url)
    # headers = _headers,
    user_res = session.get(url, verify=False)
    # print(user_res.text)
    orgId = json.loads(user_res.text)["org"]["orgId"]
    return str(orgId)


def get_login_user_id(session, env, host):
    # 获取当前登录用户的单位ID
    login_domain = f'{env}_{host}'  # 根据env参数替换环境 test1_xcj
    url = getattr(LoginDomain, login_domain).value + "gateway/v1/user"
    user_res = session.get(url, verify=False)
    userId = json.loads(user_res.text)["userId"]
    return str(userId)


def get_login_user_info(session, env, host):
    # 获取当前登录用户的单位ID
    login_domain = f'{env}_{host}'  # 根据env参数替换环境 test1_xcj
    url = getattr(LoginDomain, login_domain).value + "gateway/v1/user"
    user_res = session.get(url, verify=False)
    return user_res


if __name__ == '__main__':
    import requests
    r = requests.Session()
    get_login_org_id(r, 'test1', 'xcj')