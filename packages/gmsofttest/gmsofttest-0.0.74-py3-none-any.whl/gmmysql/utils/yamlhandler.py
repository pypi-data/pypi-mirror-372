"""
Name : yamlhandler.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2020/11/19 9:38
Desc:
"""
import yaml
import os


class YamlUtil:
    def __init__(self, *file_name):
        self.file_name = file_name

    # 读取yaml文件
    def read_yaml(self):
        """
        读取yaml
        :param
        :return:
        """
        # 文件夹地址
        yaml_directory_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        # 获取配置文件的全路径,兼容linux和windows
        yaml_path = os.sep.join([yaml_directory_path])

        for i in range(len(self.file_name)):
            yaml_path = os.sep.join([yaml_path, self.file_name[i]])
        try:
            # 处理配置文件中含中文出现乱码，需加入encoding='utf-8'，
            with open(yaml_path, 'r', encoding='utf-8') as f:
                x = yaml.load(f, Loader=yaml.FullLoader)
                return x
        except FileNotFoundError as e:
            print("file not found!!! {}".format(e))
        except TypeError as t:
            print("the type of file is wrong!!! {}".format(t))

    def read_data_yaml(self):
        """
        读取数据yaml
        :param
        :return:
        """
        # 文件夹地址
        yaml_directory_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        # 获取配置文件的全路径,兼容linux和windows
        yaml_path = os.sep.join([yaml_directory_path])
        for i in range(len(self.file_name)):
            yaml_path = os.sep.join([yaml_path, self.file_name[i]])

        try:
            # 处理配置文件中含中文出现乱码，需加入encoding='utf-8'，
            with open(yaml_path, 'r', encoding='utf-8') as f:
                x = yaml.load(f, Loader=yaml.FullLoader)
                return x
        except FileNotFoundError as e:
            print("file not found!!! {}".format(e))
        except TypeError as t:
            print("the type of file is wrong!!! {}".format(t))


if __name__ == "__main__":
    a = YamlUtil('data', 're-guarantee', 'data_check_detail.yaml').read_data_yaml()
    print(a)

