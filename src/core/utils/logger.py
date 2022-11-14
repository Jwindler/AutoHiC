#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: logger.py
@time: 6/14/22 11:38 AM
@function: 构建日志处理的基础类，用于记录
"""

import logging
import colorlog

log_colors_config = {
    'DEBUG': 'black',  # cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


class LoggerHandler(logging.Logger):

    def __init__(
            self,
            name="root",
            level='DEBUG',
            file=None):
        # logger = logging.gerLogger(name)
        super().__init__(name)

        # 设置级别
        self.setLevel(level)

        # 格式设置
        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config)

        # 初始化处理器
        if file:
            file_handle = logging.FileHandler(file)
            file_handle.setLevel(level)

            self.addHandler(file_handle)
            file_handle.setFormatter(console_formatter)
        stream_handler = logging.StreamHandler()

        # 设置handle 的级别
        stream_handler.setLevel(level)

        self.addHandler(stream_handler)
        stream_handler.setFormatter(console_formatter)


# 初始化日志
logger = LoggerHandler(file="/home/jzj/Jupyter-Docker/Download/log.txt")

if __name__ == '__main__':
    logger = LoggerHandler()
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
