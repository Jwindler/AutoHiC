#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: cut_ctg_to3.py
@time: 7/22/22 3:58 PM
@function: 主要用于将一个contig切割成3个contig
"""

from collections import OrderedDict
from assembly.tools.find_ctg_site import find_ctg_site


def cut_ctg_to_three(assembly_path, ctg_name, site_start: int, site_end: int, save_path):
    ctgs_info = OrderedDict()  # ctg序号与长度

    ctgs_orders = []  # ctg排序

    temp_ctg_name_start_end = find_ctg_site(assembly_path, ctg_name)
    ctg_name_start = temp_ctg_name_start_end["start"]
    ctg_name_end = temp_ctg_name_start_end["end"]

    with open(assembly_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                temp_line = line.strip().split(" ")

                ctgs_info[temp_line[0]] = {
                    "order": int(temp_line[1]),
                    "length": int(temp_line[2])
                }
            else:
                temp_line = line.strip().split(" ")
                ctgs_orders.append(temp_line)

    ctgs_info_list = list(ctgs_info.items())

    flag_continue = 2  # 用于跳过2次修改

    # 更新ctgs_info
    for index, value in enumerate(ctgs_info_list):
        if value[1]["order"] < ctgs_info[ctg_name]["order"]:
            continue
        elif value[1]["order"] == ctgs_info[ctg_name]["order"]:
            temp_ctg = (ctg_name + ":::fragment_1", {
                "order": ctgs_info[ctg_name]["order"],
                "length": ctg_name_end - site_start
            })
            ctgs_info_list.insert(index + 1, temp_ctg)

            temp_ctg = (ctg_name + ":::fragment_2", {
                "order": ctgs_info[ctg_name]["order"] + 1,
                "length": site_end - site_start
            })
            ctgs_info_list.insert(index + 2, temp_ctg)

            temp_ctg = (ctg_name + ":::fragment_3", {
                "order": ctgs_info[ctg_name]["order"] + 2,
                "length": ctg_name_end - site_end
            })
            ctgs_info_list.insert(index + 3, temp_ctg)

            del ctgs_info_list[index]

        elif flag_continue != 0:
            flag_continue -= 1
            continue

        elif value[1]["order"] > ctgs_info[ctg_name]["order"]:
            value[1]["order"] = value[1]["order"] + 2

    for index_i, value_i in enumerate(ctgs_orders):
        for index_j, value_j in enumerate(value_i):
            value_j = int(value_j)
            if abs(value_j) < ctgs_info[ctg_name]["order"]:
                continue
            elif abs(value_j) == ctgs_info[ctg_name]["order"]:
                temp_value = value_j
                temp_index = (index_i, index_j)
            else:
                if value_j < 0:
                    ctgs_orders[index_i][index_j] = value_j - 2
                else:
                    ctgs_orders[index_i][index_j] = value_j + 2

    if temp_value < 0:
        ctgs_orders[temp_index[0]].insert(temp_index[1] + 1, str(temp_value - 1))
        ctgs_orders[temp_index[0]].insert(temp_index[1] + 2, str(temp_value - 2))

    else:
        ctgs_orders[temp_index[0]].insert(temp_index[1] + 1, str(temp_value + 1))
        ctgs_orders[temp_index[0]].insert(temp_index[1] + 2, str(temp_value + 2))

    print(ctgs_info_list)

    # 结果写入文件
    with open(save_path, "w") as f2:
        for i in ctgs_info_list:
            temp_str = i[0] + " " + str(i[1]["order"]) + " " + str(i[1]["length"]) + "\n"
            f2.writelines(temp_str)

        for i in ctgs_orders:
            for j in i:
                temp_str = str(j) + " "
                f2.writelines(temp_str)
            f2.writelines("\n")


def main():
    assembly_path = "/home/jzj/buffer/test.assembly"
    save_path = "/home/jzj/buffer/modified_test.assembly"

    ctg_name = ">utg765"
    site_start = 998849984
    site_end = 998849989
    cut_ctg_to_three(assembly_path, ctg_name, site_start, site_end, save_path)


if __name__ == "__main__":
    main()
