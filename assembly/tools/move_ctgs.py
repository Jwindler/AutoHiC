#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: move_ctgs.py
@time: 7/23/22 9:20 PM
@function: 将多个ctgs移动到指定的ctg后
"""

from collections import OrderedDict

from assembly.tools.get_ctg_order import get_ctg_order


def move_ctgs_toback(assembly_file, move_ctgs_dict):
    # 需要移动的ctgs的序号
    move_ctgs_order = OrderedDict()

    # 查找需要移动的ctgs的序号
    for error in move_ctgs_dict:
        move_ctgs_list = []
        for move_ctg in move_ctgs_dict[error]["move_ctgs"]:
            temp_order = get_ctg_order(assembly_file, move_ctg)
            move_ctgs_list.append(temp_order)
            move_ctgs_order[error] = {
                "move_ctgs_order": move_ctgs_list
            }

        temp_key = [i for i in move_ctgs_dict[error]["insert_site"].keys()]
        temp_insert_site_order = get_ctg_order(assembly_file, temp_key[0])
        move_ctgs_order[error]["insert_site_order"] = temp_insert_site_order

    # 存放ctg_info
    ctg_info = []

    # 存储原始染色体顺序
    original_order = []

    # 获取染色体原始顺序
    with open(assembly_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">") is False:
                temp_line = line.strip().split(" ")
                original_order.append(temp_line)
            else:
                ctg_info.append(line)

    # 循环错误
    for error in move_ctgs_order:
        # 删除移动的ctgs
        for i_index, order_list in enumerate(original_order):
            for j_index, site in enumerate(order_list):
                # 如果是删除位点，则删除
                if site in move_ctgs_order[error]["move_ctgs_order"]:
                    original_order[i_index].remove(site)

        # 插入移动的ctgs
        for i_index, order_list in enumerate(original_order):
            for j_index, site in enumerate(order_list):
                # 如果是删除位点，则删除
                if site == move_ctgs_order[error]["insert_site_order"]:
                    for insert_site in move_ctgs_order[error]["move_ctgs_order"][::-1]:
                        temp_index = original_order[i_index].index(site) + 1
                        original_order[i_index].insert(temp_index, insert_site)
                        temp_index += 1

    # 写入文件
    with open(assembly_file, "w") as f:
        for i in ctg_info:
            f.write(i)
        for i in original_order:
            f.write(" ".join(i) + "\n")
        f.close()


def main():
    move_ctgs_dict = OrderedDict([('error_1', {
        'move_ctgs': {'>utg615:::fragment_2': {'length': '2742410', 'start': 906020262, 'end': 908762672},
                      '>utg4531': {'length': '434140', 'start': 908762672, 'end': 909196812},
                      '>utg16264': {'length': '133803', 'start': 909196812, 'end': 909330615},
                      '>utg3590': {'length': '1136733', 'start': 909330615, 'end': 910467348},
                      '>utg2491:::fragment_1': {'length': '15216', 'start': 910467348, 'end': 910482564}},
        'insert_site': {'>utg85479': {'length': '155329', 'start': 1111992756, 'end': 1112148085}}}), ('error_2', {
        'move_ctgs': {'>utg832:::fragment_2': {'length': '4719480', 'start': 990280002, 'end': 994999482},
                      '>utg2240': {'length': '2444918', 'start': 994999482, 'end': 997444400},
                      '>utg4279': {'length': '939440', 'start': 997444400, 'end': 998383840},
                      '>utg49998': {'length': '166707', 'start': 998383840, 'end': 998550547},
                      '>utg66184': {'length': '83773', 'start': 998550547, 'end': 998634320},
                      '>utg28112': {'length': '176037', 'start': 998634320, 'end': 998810357},
                      '>utg765:::fragment_1': {'length': '39627', 'start': 998810357, 'end': 998849984}},
        'insert_site': {'>utg4426': {'length': '3489386', 'start': 839525662, 'end': 843015048}}})])
    move_ctgs_toback("/home/jzj/buffer/modified_test.assembly", move_ctgs_dict)


if __name__ == "__main__":
    main()
