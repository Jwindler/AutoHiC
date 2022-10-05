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
import os


def get_conf(key=None):
    try:
        config_path = os.environ['CONFIG_PATH']
    except Exception:
        print("Please set the environment variable CONFIG_PATH")
        raise ValueError

    # conf_path = '/home/jzj/HiC-OpenCV/conf/config.yml'

    with open(config_path) as f:
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
