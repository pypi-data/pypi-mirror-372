"""
    日志记录控件
"""
import logging
import time
import os
from datetime import datetime


import logging
import os

class Logger:
    def __init__(self, name, level=logging.DEBUG, log_file='application.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 创建一个处理器，将日志写入日志文件
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # 创建一个处理器，将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # 创建一个格式器，定义日志的格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 将格式器添加到处理器
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    log = Logger('hello')
    # log.info('info msg1000013333')
    # log.debug('debug msg')
    # log.warning('warning msg')

    # log.error('error msg')
