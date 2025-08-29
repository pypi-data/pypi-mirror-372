"""
Name : gm_modify_svn_conf_yaml.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2024-08-13 16:00
Desc:
"""
import tempfile
import subprocess
from ruamel.yaml import YAML
import shutil
import os

gm_svn_conf_domain = 'https://192.168.2.10:8080/svn/GovProEleTrade/conf'

def del_path(path):
    if os.path.exists(path):
        print("sc")
        if os.name == 'nt':
            os.system(' rmdir /S /Q  '+path)
        else:
            os.system(' rm -rf  '+path)

def read_svn_conf(env='test1', host='zcj', conf_file_name=None):
    """
    读取svn上相关配置，默认地址 https://192.168.2.10:8080/svn/GovProEleTrade/conf/..
    :param env: 测试环境
    :param host: 测试机房
    :param conf_file_name: 配置文件名
    :return:
    """

    rootpath = os.path.join(os.path.expanduser('~'), '__pytest_run_temp')
    if os.path.exists(rootpath):
        del_path(rootpath)
    if not os.path.exists(rootpath):
        os.makedirs(rootpath)

    try:
        gm_svn_conf_url = gm_svn_conf_domain + '/' + env + '/' + host + '/' + conf_file_name
        print(f"当前conf配置文件完整路径：{gm_svn_conf_url}, 开始读取操作")
        svn_command = ['svn', 'export', gm_svn_conf_url, rootpath]
        subprocess.run(svn_command, check=True)
        yaml_file_path = os.path.join(rootpath, conf_file_name)
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.safe_load(file)
        return yaml_data
    except subprocess.CalledProcessError as e:
        print(f"SVN命令执行失败: {e}")
    except yaml.YAMLError as exc:
        print(f"YAML文件解析错误: {exc}")
        raise
    finally:
        del_path(rootpath)


def write_svn_conf(env='test1', host='zcj', conf_file_name=None, params_list=None, new_value=None):
    """
    编辑svn上conf文件配置，默认地址 https://192.168.2.10:8080/svn/GovProEleTrade/conf/..
    :param env: 测试环境
    :param host: 测试机房
    :param conf_file_name: 配置文件名
    :return:
    """
    # 创建 YAML 对象
    yaml = YAML()

    rootpath = os.path.join(os.path.expanduser('~'), '__pytest_run_temp1')
    if os.path.exists(rootpath):
        del_path(rootpath)
    if not os.path.exists(rootpath):
        os.makedirs(rootpath)

    try:
        gm_svn_conf_directory_url = gm_svn_conf_domain + '/' + env + '/' + host + '/'
        print(f"当前conf配置文件夹目录：{gm_svn_conf_directory_url}, 开始检出目录")

        # 检出
        checkout_command = ['svn', 'checkout', gm_svn_conf_directory_url, rootpath]
        subprocess.run(checkout_command, check=True)

        # 修改
        yaml_file_path = os.path.join(rootpath, conf_file_name)
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.load(file)

        for key in params_list:
            print(key)
            # yaml_data['rag']['fastgpt']['enabled'] = False
        # with open(yaml_file_path, 'w', encoding='utf-8') as file:
        #     yaml.dump(yaml_data, file)

            # # 提交
        # commit_message = "pytest测试框架自动修改"
        # files_to_commit = '.'  # 表示当前目录下的所有更改，或者使用特定文件的路径
        # svn_command = ['svn', 'commit', '-m', commit_message, files_to_commit]
        # subprocess.run(svn_command, check=True, cwd=rootpath)  # 使用cwd参数切换到工作副本的目录
    except subprocess.CalledProcessError as e:
        print(f"SVN命令执行失败: {e}")
    except yaml.YAMLError as exc:
        print(f"YAML文件解析错误: {exc}")
        raise
    # finally:
    #     del_path(rootpath)


if __name__ == '__main__':
    write_svn_conf('test1', 'xcj', 'djckms.yml', ['rag', 'fastgpt', 'enabled'])
