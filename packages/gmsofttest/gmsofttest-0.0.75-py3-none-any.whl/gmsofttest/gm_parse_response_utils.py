"""
Name : gm_parse_response_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-16 9:33
Desc:  快速解析请求返回text，并获取自己想要的数据。需学习jsonpath插件
"""

import json
from jsonpath import jsonpath

def gm_extract_json(text, jsonpath_expression):
    """使用jsonpath工具类解析请求返回值"""
    try:
        # 判断是否
        if isinstance(text, dict):
            data = jsonpath(text, jsonpath_expression)  # 使用jsonpath进行解析
        elif isinstance(text, str):
            text1 = json.loads(text)
            data = jsonpath(text1, jsonpath_expression)  # 使用jsonpath进行解析
        elif isinstance(text, list):
            data = jsonpath(text, jsonpath_expression)  # 使用jsonpath进行解析
        else:
            json_text = json.loads(text)  # 如果是非dict、str、list类型，则转换成python对象
            data = jsonpath(json_text, jsonpath_expression)  # 使用jsonpath进行解析
        return data
    except TypeError as e:
        print("入参类型：{}，入参数据：{}，请检查错误:{}".format(type(text), text, e))


if __name__ == '__main__':
    s = """{ "store": 
                { "book": 
                    [
                        { "category": "reference", "author": "Nigel Rees", "title": "Sayings of the Century", "price": 8.95 },
                        { "category": "fiction", "author": "Evelyn Waugh", "title": "Sword of Honour", "price": 12.99 }, 
                        { "category": "fiction", "author": "Herman Melville", "title": "Moby Dick", "isbn": "0-553-21311-3", "price": 8.99 }, 
                        { "category": "fiction", "author": "J. R. R. Tolkien", "title": "The Lord of the Rings", "isbn": "0-395-19395-8", "price": 22.99 } 
                    ], 
                "bicycle": { "color": "red", "price": 19.95 } 
                } 
            }"""

    print(gm_extract_json(s, '$.store.book'))
    print(gm_extract_json(s, '$.store.book[0]'))
    print(gm_extract_json(s, '$.store.book[0,3]'))
    print(gm_extract_json(s, '$.store.book[*].author'))
    print(gm_extract_json(s, '$.store.book[(@.length-1)].title'))
    print(gm_extract_json(s, '$.store.book[3].title'))
    print(gm_extract_json(s, '$.store.book[?(@.price<10)].price'))


    print([i*2 for i in gm_extract_json(s, '$.store.book[*].author')])

    d = """{"id": "1251862962956951552"}"""
    print(type(s))
    print(type(d))
    print(gm_extract_json(d, '$.id'))
    package_id = gm_extract_json(d, '$.id')  # 取第一个评标室已结束的packageid
    print(package_id)
    package_room_state = gm_extract_json(d, '$.evaluateRoomState')  # 取第一个评标室已结束的packageid
    print(package_room_state)




