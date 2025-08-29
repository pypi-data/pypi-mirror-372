"""
Name : stock_enum.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-11 15:14
Desc: 采购数据枚举类
"""
import json
from enum import Enum


# 采购枚举
class StockEnum(Enum):
    """采购数据枚举，来源于码表"""
    ITEMTYPE = 301  # 项目类型
    STOCKORGANFORMS = 302  # 采购组织形式
    COMMIT = 302  # 自行或委托
    STOCKMODE = 304  # 采购方式
    STOCKCATATYPE = 305  # 采购目录分类
    ORIGINTYPE = 307   # 是否进口商品
    BRANDTYPE = 308  # 品目类别
    FINANCEKIND = 310  # 资金性质
    PAYCHANNEL = 311  # 支付渠道
    FINANCCATAGORY = 312   # 资金类别
    SERVERCATEGORY = 313  # 服务类别
    ACCOUNT = 314  # 管理账号
    UNIT = 321  # 计量单位
    GOODS = '货物类'
    ENGINEERING = '工程类'
    SERVICES = '服务类'


class EOpenBidHallEnum(Enum):
    CHOOSEEVAL = 37
    CHOOSEOPENBID = 36