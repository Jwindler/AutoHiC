#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: chr_len_config.py
@time: 5/26/22 11:00 AM
@function: 用户自定义染色体长度配置
"""


width = {
    1: {
        "start": 0,
        "end": 200000000
    },
    2: {
        "start": 150000000,
        "end": 400000000
    },
    3: {
        "start": 350000000,
        "end": 550000000
    },
    4: {
        "start": 520000000,
        "end": 630000000
    },
    5: {
        "start": 600000000,
        "end": 800000000
    },
    6: {
        "start": 750000000,
        "end": 950000000
    },
    7: {
        "start": 930000000,
        "end": 1145951891
    }
}


def main():

    for i in width:
        print(width[i]["start"], width[i]["end"], "\n")
    class_dic = ['normal', 'abnormal']

if __name__ == "__main__":
    main()
