#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: Pre_Config.py
@time: 5/19/22 7:26 PM
@function: 配置文件
"""

# 最大染色体长度
MAX_CHROMOSOME_LENGTH = 250000000  # 250Mb

# 预定义ColorRange
COLOR_RANGE_SETS = {
    2500000: 6361,
    1250000: 1607,
    1000000: 1650,
    500000: 262,
    250000: 192,
    125000: 126,
    100000: 45,
    50000: 26,
    25000: 15,
    12500: 5,
    10000: 7,
    5000: 5,
    2500: 2,
    1000: 2,
    500: 2}

# 预定义长宽
LEN_WIDTH_SETS = {
    2500000: 250000000,
    1250000: 250000000,
    1000000: 200000000,
    500000: 150000000,
    250000: 100000000,
    125000: 100000000,
    100000: 100000000,
    50000: 50000000,
    25000: 25000000,
    12500: 18070000,
    10000: 14000000,
    5000: 5000000,
    2500: 2500000,
    500: 720000}

# 预定义增量
INCREMENT_SETS = {
    2500000: 100000000,
    1250000: 100000000,
    1000000: 50000000,
    500000: 25000000,
    250000: 20000000,
    125000: 20000000,
    100000: 20000000,
    50000: 20000000,
    25000: 15000000,
    12500: 10000000,
    10000: 10000000,
    5000: 5000000,
    2500: 2500000,
    500: 500000}

# 用于获取错误矩阵时，预防矩阵长度超出分辨率的限制
RSE_MAX_LEN = {
    2500000: 3610000000,
    1250000: 1800000000,
    1000000: 200000000,
    500000: 170000000,
    250000: 170000000,
    125000: 170000000,
    100000: 100000000,
    50000: 50000000,
    25000: 25000000,
    12500: 18000000,
    10000: 14000000,
    5000: 5000000,
    2500: 2500000,
    500: 500000}
