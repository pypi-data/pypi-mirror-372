"""
Name : gm_login_utils.py
Author  : 池泽琴
Contact : 邮箱地址
Time    : 2023-10-07 14:36
Desc:
"""
import hashlib
import json
import requests
from gmmysql.mysqlexe import OperateMysql


def login_xcj(request, user_name, password="GmsoftTest_1997"):
    client_id = 'plat@DJC'
    plat_name = "行采平台"
    login(request, plat_name, client_id, user_name, password)


def login_zcj(request, user_name, password="GmsoftTest_1997"):
    client_id = 'plat@ZCJ'
    plat_name = "政采平台"
    login(request, plat_name, client_id, user_name, password)


def login(request, plat_name, client_id, user_name, password="GmsoftTest_1997"):
    djc_domain_name, xcj_domain_name, zcj_domain_name, zc_domain_name, jc_domain_name, zcj_pm_domain_name \
        = get_domain_name(request)
    domain_name = djc_domain_name
    # print(domain_name)

    # 认证中心登录
    auth_url = "https://" + domain_name + "/djc-gateway/authing/login"
    redirect_url = "https://" + domain_name + "/gateway/v1/login"
    origin = "https://" + domain_name
    r = requests.session()
    login_auth(r, auth_url, redirect_url, client_id, domain_name, origin, user_name, password, plat_name)

    # 平台登录
    login_url = "https://" + domain_name + "/djc-gateway/authing/oauth/authorize"
    client_id_secret = __get_client_id_secret(client_id)
    access_token = login_plat(r, client_id, client_id_secret, domain_name, login_url, redirect_url, plat_name)
    return access_token


def login_auth(r, auth_url, redirect_url, client_id, scope, origin, username, password, auth_name):
    # 认证中心登录
    md5 = hashlib.md5()
    md5.update(str(password).encode('utf-8'))
    password1 = md5.hexdigest()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    success_uri = "https://" + scope + "/login-app/login-success/index.html"
    if client_id == "cqzcy" or client_id == "cqzbj":
        success_uri = ""

    data = {
        "password": password1,
        "username": username,
        "origin": origin,
        "client_id": client_id,
        "scope": scope,
        "options": '',
        "response_type": 'code',
        "redirect_uri": redirect_url,
        "success_uri": success_uri,
        "state": '{"client_id": "' + client_id + '","scope":"' + scope + '","redirect_uri":"' + redirect_url + '"}'
    }
    # if code != '':
    #     data.update(code=code, mobile=mobile)
    # 认证中心登录 verify="GMDEVSERVER-CA.cer"
    login_res = r.post(auth_url, data=data, headers=headers, verify=False)
    # print(login_res.headers['Set-Cookie'])
    print("\n"+auth_name+"认证中心登录结果-Response code是: {}".format(login_res.status_code))

    if login_res.status_code == 400 and login_res.text.find('"message":"请进行二次验证"') >= 0:
        # 需做二次验证
        code = "111111"
        print(login_res.text)
        check_mobile = json.loads(login_res.text)["additional"]["mobile"]
        data.update(code=code, mobile=check_mobile)
        login_res = r.post(auth_url, data=data, headers=headers, verify=False)
        print("\n" + auth_name + "认证中心登录结果-Response code是: {}".format(login_res.status_code))
        # login_auth(r, auth_url, redirect_url, client_id, scope, username, password, "111111", check_mobile, auth_name)
    elif login_res.status_code == 403 and login_res.text.find('拒绝访问') >= 0:
        # 需做极验证
        print(login_res.text)
        auth_url = auth_url + "?geetest_challenge=111111&geetest_seccode=111111&geetest_validate=111111"
        login_res = r.post(auth_url, data=data, headers=headers, verify=False)
        print("\n" + auth_name + "登录结果-Response code是: {}".format(login_res.status_code))
        # print("czq:"+login_res.text)

    if login_res.status_code == 200:
        # 同步登录相关认证中心
        location_url = json.loads(login_res.text)['location']
        grant_res = r.get(location_url, verify=False)
        print("location请求结果-Response code是: {}".format(grant_res.status_code))
    return login_res


def login_plat(r, client_id, client_id_secret, scope, login_url, redirect_url, plat_name):
    # 平台登录
    authorize_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_url,
        'scope': scope,
        'options': '',
        "state": '{"client_id": "' + client_id + '","scope":"' + scope + '","redirect_uri":"' + redirect_url + '"}'
    }
    # print(authorize_params)
    # 询问认证中心xx平台能否登录
    authorize_res = r.get(login_url, params=authorize_params, verify=False, allow_redirects=False)
    # print(authorize_res.status_code)
    # print(authorize_res.text)
    if authorize_res.status_code == 302:
        # print(authorize_res.headers['location'].find("code="))
        if authorize_res.headers['location'].find("code=") >= 0:
            code = authorize_res.headers['location'].split('code=')[1].split('&')[0]
            print("code：{}".format(code))

            _headers = {
                "Authorization": "Basic "+client_id_secret,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            login_params = {
                'code': code,
                'grant_type': 'authorization_code',
                "redirect_uri": redirect_url
            }
            # print(login_params)
            # print(redirect_url)
            login_plat_res = r.get(login_url.replace("authorize", "token"), params=login_params,
                                   verify=False, headers=_headers)
            # print(login_plat_res.text)
            # print(login_plat_res.headers['Set-Cookie'])
            print(plat_name + "平台登录结果-Response code是：{}".format(login_plat_res.status_code))
            # print("请求结果：{}".format(login_plat_res.text))
            access_token = login_plat_res.text.split('":"')[1].split('","')[0]
            print("access_token：{}".format(access_token))
            return access_token
        else:
            return authorize_res.headers['location']
    else:
        return authorize_res.text


def reset_pwd(mobile):
    # 固定盐值
    fix_Salt_Value = "2314861a-301c-403a-b4c9-5b1734101043"
    pwd = "GmsoftTest_1997"
    sql = "UPDATE logincomm.`TL_Account` " \
          "SET `Passwd`=MD5(CONCAT(MD5('" + pwd + "'),'" + fix_Salt_Value + "')),`nonce` = '' " \
          "WHERE `MOBILE`='" + mobile + "'"
    om = OperateMysql()
    print("\n"+sql)
    om.delete_data(sql)


def get_domain_name(request):
    # 获取域名
    # login_env:1-Test环境、2-Test1环境、3-show环境、4-# 正式环境、5-Dev1环境、6-Test2
    login_env = request.config.getoption("--env")
    if login_env == "test1":
        djc_domain_name = "www.djctest1.gm"
        xcj_domain_name = "www.xcjtest1.gm"
        zcj_domain_name = "www.cqzcjtest1.gm"
        zc_domain_name = "www.zctest1.gm"
        jc_domain_name = "www.jctest1.gm"
        zcj_pm_domain_name = "192.168.2.22:31880"
    elif login_env == "show":
        djc_domain_name = "www.djcshow.gm"
        xcj_domain_name = "www.cqzcjshow.com"
        zcj_domain_name = "www.gpwbeta.com"
        zc_domain_name = "www.zcshow.gm"
        jc_domain_name = "www.jcshow.gm"
        zcj_pm_domain_name = "192.168.2.20:31880"
    elif login_env == "test2":
        djc_domain_name = "www.djctest2.gm"
        xcj_domain_name = "www.xcjtest2.gm"
        zcj_domain_name = "www.cqzcjtest2.gm"
        zc_domain_name = "www.zctest2.gm"
        jc_domain_name = "www.jctest2.gm"
        zcj_pm_domain_name = "192.168.2.22:31880"
    else:
        djc_domain_name = "www.djcdev1.gm"
        xcj_domain_name = "www.xcjdev1.gm"
        zcj_domain_name = "www.cqzcjdev1.gm"
        zc_domain_name = "www.zcdev1.gm"
        jc_domain_name = "gpw.xcj360.com:21880"
        zcj_pm_domain_name = "192.168.2.21:31880"
    return djc_domain_name, xcj_domain_name, zcj_domain_name, zc_domain_name, jc_domain_name, zcj_pm_domain_name


def __get_client_id_secret(client_id='plat@XCJ'):
    # 获取client_id_secret
    if client_id == 'plat@XCJ':
        # plat@XCJ:test的BASE64编码是cGxhdEBYQ0o6dGVzdA==,前面的test是取的application.yml文件中security.user.password
        client_id_secret = 'cGxhdEBYQ0o6dGVzdA=='
    elif client_id == 'plat@DJC':
        # plat@DJC:test的BASE64编码是cGxhdEBESkM6dGVzdA==,前面的test是取的application.yml文件中security.user.password
        client_id_secret = 'cGxhdEBESkM6dGVzdA=='
    else:
        # plat@ZCJ:test的BASE64编码是cGxhdEBaQ0o6dGVzdA==,前面的test是取的application.yml文件中security.user.password
        client_id_secret = 'cGxhdEBaQ0o6dGVzdA=='
    return client_id_secret


if __name__ == '__main__':
    login_xcj("test1", "admin")
