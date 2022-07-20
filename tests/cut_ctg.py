#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: cut_ctg.py
@time: 7/14/22 4:46 PM
@function: 对findcontig返回的contig进行切割
"""

# !/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: insert_site.py
@time: 6/23/22 11:29 AM
@function: 根据contig信息，切割assembly中contig,并更新assembly文件
"""

from collections import OrderedDict

from assembly.tools.find_ctg_site import find_ctg_site


def insert_site(assembly_path, ctg_name, site: int, save_path):
    ctg_info = OrderedDict()  # contig 信息
    ctg_order = []  # contig 顺序

    ctg_name_start_end = find_ctg_site(assembly_path, ctg_name)

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

    # 需要修改contig的序号
    insert_site_order = ctg_info[ctg_name]["order"]

    ctg_info_copy = OrderedDict()  #
    temp_order = 1  # 用于contig信息，重新排序

    for i in ctg_info:

        if i == ctg_name:
            temp_ctg_name = ctg_name + ":::fragment_1"
            ctg_info_copy[temp_ctg_name] = {
                "order": temp_order,
                "length": site - ctg_name_start_end["start"] + 1
            }

            temp_order += 1
            temp_ctg_name_2 = ctg_name + ":::fragment_2"
            ctg_info_copy[temp_ctg_name_2] = {
                "order": temp_order,
                "length": ctg_name_start_end["end"] - site
            }
            temp_order += 1

        else:
            ctg_info_copy[i] = {
                "order": temp_order,
                "length": ctg_info[i]["length"]
            }
            temp_order += 1

    ctg_order_copy = ctg_order

    # 调整染色体顺序
    for index_i, i in enumerate(ctg_order_copy):
        site_flag = False  # 用于标记，防止insert_site_order再次加一
        for index_j, j in enumerate(i):

            j = int(j)

            if site_flag:
                site_flag = False
                continue

            if abs(j) > int(insert_site_order):
                if j < 0:
                    ctg_order_copy[index_i][index_j] = int(
                        ctg_order_copy[index_i][index_j])
                    ctg_order_copy[index_i][index_j] -= 1
                else:
                    ctg_order_copy[index_i][index_j] = int(
                        ctg_order_copy[index_i][index_j])
                    ctg_order_copy[index_i][index_j] += 1
            if abs(j) == int(insert_site_order):
                if j > 0:
                    ctg_order_copy[index_i].insert(index_j + 1, j + 1)
                else:
                    ctg_order_copy[index_i].insert(index_j + 1, j - 1)

                site_flag = True

    # 结果写入文件
    with open(save_path, "w") as f2:
        for i in ctg_info_copy:
            temp_str = i + " " + \
                       str(ctg_info_copy[i]["order"]) + " " + str(ctg_info_copy[i]["length"]) + "\n"
            f2.writelines(temp_str)

        for i in ctg_order_copy:
            for j in i:
                temp_str = str(j) + " "
                f2.writelines(temp_str)
            f2.writelines("\n")


def main():
    assembly_path = "/home/jzj/buffer/test.txt"
    save_path = "/home/jzj/buffer/test2.txt"

    insert_site(assembly_path, ">utg2491", 910482564, save_path)


if __name__ == "__main__":
    main()
