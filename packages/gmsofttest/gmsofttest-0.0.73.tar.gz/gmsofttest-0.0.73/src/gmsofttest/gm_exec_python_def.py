"""
Name : gm_exec_python_def.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2024-07-04 20:15
Desc:  在python中执行函数并返回执行结果
"""

import datetime
import random
import pandas
import openpyxl
import os
import sys
import json
import re


def exec_python_def(command):
    code_to_command = f"result = {command}"  # 这里假设mystr本身应该是一个表达式或函数调用
    local_vars = {}
    # 使用exec执行代码，并传入局部作用域字典
    exec(code_to_command, globals(), local_vars)
    # 从局部作用域字典中获取执行结果
    result = local_vars.get('result')
    return result


