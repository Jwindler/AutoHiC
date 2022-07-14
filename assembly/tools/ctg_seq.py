#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: ctg_seq.py
@time: 6/23/22 5:43 PM
@function: 根据assembly文件返回查询contig的起始与终止位置
"""

from collections import OrderedDict


def get_ctg_seq(assembly_path, ctg_name):
    ctg_info = OrderedDict()  # contig 信息
    ctg_order = []  # contig 顺序

    # 获取contig 信息
    with open(assembly_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                temp_line = line.strip().split(" ")

                ctg_info[temp_line[0]] = {
                    "order": temp_line[1],
                    "length": temp_line[2]
                }
            else:
                temp_line = line.strip().split(" ")
                ctg_order.append(temp_line)

    ctg_order = [order for st in ctg_order for order in st]

    ctg_s_e = {}
    temp_length = 1  # 辅助计算contig长度

    # 根据染色体上ctg的顺序，获取每个contig的起始与终止位置
    for i in ctg_order:
        i = abs(int(i))
        for j in ctg_info:
            if int(ctg_info[j]["order"]) == i:
                ctg_s_e[j] = {
                    "start": temp_length,
                    "end": temp_length + int(ctg_info[j]["length"]) - 1
                }
                temp_length += int(ctg_info[j]["length"])

    return ctg_s_e[ctg_name]


def main():
    temp = get_ctg_seq("/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.assembly", ">utg2491")
    print(temp)


if __name__ == "__main__":
    main()
