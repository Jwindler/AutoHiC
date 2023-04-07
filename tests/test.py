#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: test.py
@time: 4/3/23 8:43 PM
@function: 
"""
import os
import re
import yaml
import typer
import subprocess


def main():
    # 指定要搜索的路径和正则表达式
    path = "/home/jzj/buffer"
    hic_pattern = r"[\w\.]*hic"
    hic_files = []
    # 遍历路径下的所有文件和文件夹
    for filename in os.listdir(path):
        # 使用正则表达式匹配文件名
        if re.match(hic_pattern, filename):
            # 打印与模式匹配的文件名
            hic_files.append(filename)
    print(hic_files)

if __name__ == "__main__":
    main()
