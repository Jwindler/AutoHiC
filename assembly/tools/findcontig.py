#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: findcontig.py
@time: 5/23/22 11:59 AM
@function: 根据错误检测的结果，查找错误区域内的contig,返回结果为包含的contig和其范围
"""

import json


def site_contig(start, end, ratio, assembly):
    """
    根据start,end 返回该区域所包含的contig
    :param start:    查询起始坐标
    :param end:      查询终止坐标
    :param ratio:    .hic中`assembly` 与Genome size的比值
    :param assembly: `.assembly`文件绝对路径
    :return: 位点内contig信息
    """

    contain_contig = {}

    contig_info = {}  # contig 信息{order: {name, length}}

    contig_order = []  # contig 顺序信息列表

    # 基因组上真实的位置信息
    genome_start = start * ratio
    genome_end = end * ratio
    print("查询位点为 ： {0} - {1} \n".format(genome_start, genome_end))

    print("该区域包含的contig : ")
    with open(assembly, "r") as f:
        lines = f.readlines()
        for line in lines:
            # contig :name : order, length
            if line.startswith(">"):
                each_line = line.strip().split()
                contig_info[each_line[1].strip(">")] = {
                    "name": each_line[0],
                    "length": each_line[2]
                }
            # contig 顺序
            else:
                contig_order.append(line.strip().split())

        # 二维降一维
        contig_order = [order for st in contig_order for order in st]

    # 寻找contig
    temp_len = 0
    for i in contig_order:
        if i.startswith("-"):
            i = i[1:]
            temp_len += int(contig_info[i]["length"])
        else:
            temp_len += int(contig_info[i]["length"])

        if genome_start <= temp_len <= genome_end:
            contain_contig[contig_info[i]["name"]] = {
                "length": contig_info[i]["length"],
                "start": temp_len - int(contig_info[i]["length"]),
                "end": temp_len
            }
            temp_len_last = temp_len

    # 获取非全包含的最后一个contig

    # 全包含的最后一个contig
    last_contig = list(contain_contig.keys())[-1]
    if contain_contig[last_contig]["end"] < genome_end:

        last_contig_order = 0
        # 获取全包含的最后一个contig的序号
        for key, value in contig_info.items():
            if value["name"] == last_contig:
                last_contig_order = key

        # 获取非全包含的最后一个contig在contig_order中的index
        try:
            temp = contig_order.index(last_contig_order)

        except ValueError:
            t = "-" + last_contig_order
            temp = contig_order.index(t)

        last_1_index = contig_order[int(temp) + 1]

        contain_contig[contig_info[str(abs(int(last_1_index)))]["name"]] = {
            "length": contig_info[str(abs(int(last_1_index)))]["length"],
            "start": temp_len_last,
            "end": temp_len_last + int(contig_info[str(abs(int(last_1_index)))]["length"])
        }

        contain_contig = json.dumps(
            contain_contig,
            indent=4,
            separators=(
                ',',
                ': '))
        print(contain_contig)

    return contain_contig


def main():
    start_site = 453000000
    end_site = 455000000
    ratio = 2
    assembly = "/home/jzj/Auto-HiC/HiC-Data/Np_HiC/0/Np.0.assembly"
    site_contig(start_site, end_site, ratio, assembly)


if __name__ == "__main__":
    main()
