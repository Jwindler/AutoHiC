#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: cli.py
@time: 2022/4/29 上午10:33
@function: 命令行参数以及程序入口
"""

import logging


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)

    # Formatter
    formatter = logging.Formatter("%(asctime)s %(filename)s %(name)s %(funcName)s %(levelname)s %(message)s")

    # FileHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


class Main():
    def __init__(self):
        pass


if __name__ == "__main__":
    main()
