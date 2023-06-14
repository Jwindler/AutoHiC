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
        console_formatter = logging.Formatter(
            fmt='[%(asctime)s] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S')

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
logger = LoggerHandler()

if __name__ == '__main__':
    logger = LoggerHandler()
    logger.debug('debug ')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
