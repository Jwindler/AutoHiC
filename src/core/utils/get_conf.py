#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: get_conf.py
@time: 9/30/22 9:52 PM
@function: 解析配置文件
"""

import yaml


def get_conf(key=None):
    #  TODO： 需要修改如何读取配置文件
    conf_path = '/home/jzj/HiC-OpenCV/conf/config.yml'

    with open(conf_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if key:
            try:
                return data[key]
            except KeyError:
                print("KeyError: %s" % key)
        else:
            # data 是一个字典对象
            return data


def main():
    print(get_conf())


if __name__ == "__main__":
    main()
