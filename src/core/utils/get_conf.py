#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_conf.py
@time: 9/30/22 9:52 PM
@function: parse config file
"""

import yaml


def get_conf(config_path=None, key=None):
    if config_path is None:
        config_path = '/home/jzj/HiC-OpenCV/conf/config.yml'

    with open(config_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if key:
            try:
                return data[key]
            except KeyError:
                print("KeyError: %s" % key)
        else:
            return data


def main():
    print(get_conf())


if __name__ == "__main__":
    main()
