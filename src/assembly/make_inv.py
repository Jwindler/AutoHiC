#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: make_inv.py
@time: 8/31/22 10:25 AM
@function: 制造inversion错误
"""

from src.assembly.asy_operate import AssemblyOperate


def make_inv(asy_file, out_file_path):
    # 获取需要反转的ctg序号(ctg>1Mb)
    inv_list = []
    with open(asy_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                temp_line = line.strip().split(" ")

                # 全部反转
                inv_list.append(int(temp_line[1]))
                # ctg长度大于1Mb
                # if int(temp_line[2]) >= 1000000:
                #     inv_list.append(int(temp_line[1]))

    # 获取原始信息
    asy_operate = AssemblyOperate(asy_file, ratio=None)
    ctgs, ctgs_orders = asy_operate._get_ctgs_orders(asy_file)

    with open(out_file_path, "w") as f:

        # 写入ctg信息
        for key, value in ctgs.items():
            f.write(key + " " + value["order"] + " " + value["length"] + "\n")

        # 写入新的ctg顺序
        for ctgs_order in ctgs_orders:
            temp_write_list = []
            for x in ctgs_order:
                # 跟新需要切割的ctg顺序
                if abs(int(x)) in inv_list:
                    if int(x) > 0:
                        temp_write_list.append(str(-int(x)))
                    else:  # 反向
                        temp_write_list.append(str(abs(int(x))))
                else:
                    temp_write_list.append(x)
            f.write(" ".join(temp_write_list) + "\n")


def main():
    asy_file = "/home/jzj/Downloads/Hv_bgi_HiC.assembly"
    out_file_path = "/home/jzj/Downloads/inv_Hv_bgi_HiC.assembly"
    make_inv(asy_file, out_file_path)


if __name__ == "__main__":
    main()
