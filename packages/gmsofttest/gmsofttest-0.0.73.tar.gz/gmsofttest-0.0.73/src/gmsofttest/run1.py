"""
Name : run.py.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2024-02-19 10:10
Desc:
"""

from  gm_yaml_process_utils import read_yaml,read_data_yaml

if __name__ == '__main__':
    d = read_yaml('data', 're_guarantee', 'data_common_record.yaml')
    print(d)