#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: random_inv.py
@time: 9/13/22 11:31 AM
@function: 随机反转一些ctg(60%)
"""

import random
from src.assembly.asy_operate import AssemblyOperate


def random_inv(asy_file, out_file_path):
    order_list = []
    with open(asy_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                temp_line = line.strip().split(" ")

                # 获取反转列表
                order_list.append(int(temp_line[1]))

    # 获取原始信息
    asy_operate = AssemblyOperate(asy_file, ratio=None)
    ctgs, ctgs_orders = asy_operate._get_ctgs_orders(asy_file)

    # 生成随机反转列表
    random_inv_list = random.sample(order_list, int(len(order_list) * 0.6))

    with open(out_file_path, "w") as f:

        # 写入ctg信息
        for key, value in ctgs.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # 写入新的ctg顺序
        for ctgs_order in ctgs_orders:
            temp_write_list = []
            for x in ctgs_order:
                # 跟新需要切割的ctg顺序
                if abs(int(x)) in random_inv_list:
                    if int(x) > 0:
                        temp_write_list.append(str(-int(x)))
                    else:  # 反向
                        temp_write_list.append(str(abs(int(x))))
                else:
                    temp_write_list.append(x)
            f.write(" ".join(temp_write_list) + "\n")


def main():
    asy_file = "/home/jzj/Downloads/Hv_bgi.0.assembly"
    out_file_path = "/home/jzj/Downloads/inv_Hv.assembly"
    random_inv(asy_file, out_file_path)


if __name__ == "__main__":
    main()
