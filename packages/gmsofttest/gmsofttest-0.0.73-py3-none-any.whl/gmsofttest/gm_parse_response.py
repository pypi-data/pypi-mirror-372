"""
Name : gm_parse_response_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-16 9:33
Desc:
"""

import json
from jsonpath import jsonpath



# 解析get请求返回数据的key对应值；
def extract_json_data(text, jsonpath_expression):
    """解析请求后的返回值"""
    json_text = json.loads(text)  # 转换requests请求返回string为python对象
    data = jsonpath(json_text, jsonpath_expression)  # 使用jsonpath进行解析
    return data


if __name__ == '__main__':
    s = '''
    [ 
        {
          "paramText" : "国内",
          "paramValue" : "0",
          "state" : 1,
          "ownerId" : "130117562645086249"
        },
        {
          "paramText" : "国外",
          "paramValue" : "1",
          "state" : 1,
          "ownerId" : "130117562645086249"
        }
    ]'''
    expr = '$.[paramText,paramValue]'
    json_pa = extract_json_data(s, expr)
    print(json_pa)
