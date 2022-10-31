#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: removefile.py
@time: 10/27/22 9:53 PM
@function: 
"""

import os


def copy_file(file_dir):
    path_dir = os.listdir(file_dir)
    jpg_files = [file for file in path_dir if file.endswith('.jpg')]
    json_files = [file for file in path_dir if file.endswith('.json')]
    for jpg_file in jpg_files:
        temp_name = jpg_file.split('.')[0] + ".json"
        if temp_name in json_files:
            continue
        else:
            os.remove(os.path.join(file_dir, jpg_file))


def main():
    # 文件的原始路径
    file_dir = '/home/jzj/Downloads/chr'

    copy_file(file_dir)


if __name__ == '__main__':
    main()
