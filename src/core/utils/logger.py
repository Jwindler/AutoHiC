#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: logger.py
@time: 6/14/22 11:38 AM
@function: configure logger
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
        super().__init__(name)

        # set log level
        self.setLevel(level)

        # format setting
        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config)

        # initialing Handler
        if file:
            file_handle = logging.FileHandler(file)
            file_handle.setLevel(level)

            self.addHandler(file_handle)
            file_handle.setFormatter(console_formatter)
        stream_handler = logging.StreamHandler()

        # set handler level
        stream_handler.setLevel(level)

        self.addHandler(stream_handler)
        stream_handler.setFormatter(console_formatter)


# initialing logger
logger = LoggerHandler(file="/home/jzj/Jupyter-Docker/buffer/log.txt")

if __name__ == '__main__':
    logger = LoggerHandler(file="/home/jzj/buffer/test_insert_loci.log")
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
