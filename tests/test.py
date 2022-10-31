#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: test.py
@time: 9/21/22 5:27 PM
@function: 
"""

import pickle

file = "/home/jzj/Jupyter-Docker/buffer/Axis.pkl"

with open(file, 'rb') as f:  # 打开文件
    result = pickle.load(f)  # 将二进制文件对象转换成 Python 对象

print("Done")


info