"""
Name : gm_randomdata_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-02-13 10:11
Desc:
"""

"""
Name : generate_basedata.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2022-09-01 13:46
Desc: 生成各种测试数据
"""

from faker import Factory
import time

fake = Factory().create('zh_CN')

def getMobile():
    '''随机手机号'''
    return fake.phone_number()

def getName():
    """随机姓名"""
    return fake.name()

def getAddress():
    """随机地址"""
    return fake.address()

def getEmail():
    """随机email"""
    return fake.email()

def getCompany():
    """随机公司名"""
    return fake.company()

def getCompanySuffix():
    return fake.company_suffix()

def getCity():
    """城市名，带市/县"""
    return fake.city()

def getCityName():
    """城市名，不带市/县"""
    return fake.city_name()

def getProvice():
    """省份"""
    return fake.province()

def getIDcard():
    """身份证号"""
    return fake.ssn()

def getProfile():
    """生成一串用户数据"""
    return fake.profile()

def getInt(min_value=0, max_value=10000, step=1):
    """生成长度在min_chars到max_chars之间整数"""
    return fake.pyint(min_value=min_value, max_value=max_value, step=step)

def getFloat(min_value=0, max_value=10000, step=1):
    """生成长度在min_chars到max_chars之间的浮点数"""
    return fake.pyint(min_value=min_value, max_value=max_value, step=step)

def getStr(min_chars=None, max_chars=20):
    """生成长度在min_chars到max_chars之间的字符串
    :param min_chars:
    :param max_chars:
    :return:
    """
    return fake.pystr(min_chars=min_chars, max_chars=max_chars)

def getLinuxTimestamp(t=1):
    """获取当前linux时间戳"""
    if t == 1:
        st = round(time.time()*1000)
    return st


if __name__ == '__main__':
    print(getMobile())
    print(getCityName())
    print(getInt())
    print(getInt().__str__)
    print(getCompany())
    print(getProfile())
    print(getIDcard())
