"""
Name : gm_upload_utils.py
Author  : xyp
Contact : 邮箱地址
Time    : 2024-04-07 16:46
Desc: requests上传XX数据流
"""
from requests_toolbelt import MultipartEncoder
from typing import Any


def upload_file(filepath: str, filename: str, mime_type: str) -> MultipartEncoder:
    """
    Upload a file using MultipartEncoder.

    :param filepath: Path to the file to upload.
    :param filename: Name of the file to be used in the upload.
    :param mime_type: MIME type of the file.
    :return: MultipartEncoder object containing the file data.
    """
    try:
        with open(filepath, 'rb') as f:
            file_data = f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found at path: {filepath}")
    except Exception as e:
        raise ValueError(f"An error occurred while reading the file: {e}")

        # 直接创建 MultipartEncoder 对象，而不是使用 with 语句
    encoder = MultipartEncoder(fields={'file': (filename, file_data, mime_type)})
    return encoder


# 使用示例
try:
    encoder = upload_file('path/to/your/file.txt', 'myfile.txt', 'text/plain')
    # 这里你可以使用 encoder 对象来发送 HTTP 请求
except ValueError as e:
    print(e)