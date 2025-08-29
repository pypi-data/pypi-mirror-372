"""
Name : gm_yaml_process_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-16 14:42
Desc: yaml读取封装
"""


import yaml
import os
import sys

# 读取yaml文件
def read_yaml(*filename):
    """
    读取yaml
    :param
    :return:
    """
    # 文件夹地址, 获取配置文件的全路径,兼容linux和windows
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
    yaml_path = os.sep.join([ROOT_DIR])
    for i in range(len(filename)):
        yaml_path = os.sep.join([yaml_path, filename[i]])
    if not os.path.exists(yaml_path):  # 不存在则只退回一级
        ROOT_DIR = os.path.dirname(os.path.abspath(os.getcwd()))
        yaml_path = os.sep.join([ROOT_DIR])
        for i in range(len(filename)):
            yaml_path = os.sep.join([yaml_path, filename[i]])
        if not os.path.exists(yaml_path):  # 不存在则标识为根目录
            ROOT_DIR = os.path.abspath(os.getcwd())
            yaml_path = os.sep.join([ROOT_DIR])
            for i in range(len(filename)):
                yaml_path = os.sep.join([yaml_path, filename[i]])
    try:
    # 处理配置文件中含中文出现乱码，需加入encoding='utf-8'，
        with open(yaml_path, 'r', encoding='utf-8') as f:
            x = yaml.load(f, Loader=yaml.FullLoader)
            return x
    except FileNotFoundError as e:
        print("file not found!!! {}".format(e))
    except TypeError as t:
        print("the type of file is wrong!!! {}".format(t))


def read_data_yaml(*filename):
    """
    读取数据yaml
    :param
    :return:
    """
    # 文件夹地址
    # yaml_directory_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # 获取配置文件的全路径,兼容linux和windows

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
    yaml_path = os.sep.join([ROOT_DIR])
    for i in range(len(filename)):
        yaml_path = os.sep.join([yaml_path, filename[i]])

    if not os.path.exists(yaml_path):  # 不存在则只退回一级
        ROOT_DIR = os.path.dirname(os.path.abspath(os.getcwd()))
        yaml_path = os.sep.join([ROOT_DIR])
        for i in range(len(filename)):
            yaml_path = os.sep.join([yaml_path, filename[i]])
        if not os.path.exists(yaml_path):  # 不存在则标识为根目录
            ROOT_DIR = os.path.abspath(os.getcwd())
            yaml_path = os.sep.join([ROOT_DIR])
            for i in range(len(filename)):
                yaml_path = os.sep.join([yaml_path, filename[i]])
    try:
        # 处理配置文件中含中文出现乱码，需加入encoding='utf-8'
        with open(yaml_path, 'r', encoding='utf-8') as f:
            x = yaml.load(f, Loader=yaml.FullLoader)
            return x
    except FileNotFoundError as e:
        print("file not found!!! {}".format(e))
    except TypeError as t:
        print("the type of file is wrong!!! {}".format(t))


if __name__ == "__main__":
    a = read_yaml('data', 'xcj', 'data_common_record.yaml')
    s = read_data_yaml('data', 're_guarantee', 'data_common_record.yaml')
    print(a)
    print(s)

