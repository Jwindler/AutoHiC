#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: find_site_ctgs.py
@time: 7/20/22 5:25 PM
@function: 根据错误检测的结果，查找错误区域内的contig,返回结果为包含的contig和其范围
"""

import json
import collections


def find_site_ctgs(start, end, ratio, assembly):
    """
    根据start,end 返回该区域所包含的contig
    :param start:    查询起始坐标
    :param end:      查询终止坐标
    :param ratio:    .hic中`assembly` 与Genome size的比值
    :param assembly: `.assembly`文件绝对路径
    :return: 位点内contig信息
    """

    contain_contig = collections.OrderedDict()  # 位点内contig信息

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
    temp_len_s = 0  # 记录当前contig的起始位置
    temp_len_e = 0  # 记录当前contig的终止位置

    for i in contig_order:  # 循环contig

        if i.startswith("-"):  # 反向contig
            i = i[1:]
            temp_len_s = temp_len_e
            temp_len_e += int(contig_info[i]["length"])
        else:
            temp_len_s = temp_len_e
            temp_len_e += int(contig_info[i]["length"])

        # 解冗余
        def callback():
            contain_contig[contig_info[i]["name"]] = {
                "length": contig_info[i]["length"],
                "start": temp_len_s,
                "end": temp_len_e
            }
            return temp_len_e

        # 各个contig与查询位点之间的关系（主要有四种，可以参考两条线段之间的关系）
<<<<<<< HEAD
        if temp_len_s < genome_start:
=======
        if temp_len_s <= genome_start:
>>>>>>> Ubuntu
            if genome_start < temp_len_e < genome_end:
                callback()
            elif temp_len_e > genome_end:
                callback()
        elif temp_len_s > genome_start:
<<<<<<< HEAD
            if temp_len_e < genome_end:
=======
            if temp_len_e <= genome_end:
>>>>>>> Ubuntu
                callback()
            elif temp_len_s < genome_end < temp_len_e:
                callback()

    # json格式输出
    contain_contig = json.dumps(
        contain_contig,
        indent=4,
        separators=(
            ',',
            ': '))
    print(contain_contig)

    return contain_contig


def main():
    # HiC文件位置
<<<<<<< HEAD
    start_site = 495140001
    end_site = 499424992

    ratio = 2  # 染色体长度比例

    assembly = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.assembly"
    temp = find_site_ctgs(start_site, end_site, ratio, assembly)
    error_contain_ctgs = json.loads(temp)  # 将字符串转换为字典
    error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表
    print(error_contain_ctgs[0])
=======
    start_site = 453010131
    end_site = 455241282

    ratio = 2  # 染色体长度比例

    assembly = "/home/jzj/Auto-HiC/HiC-API/tests/modified_test.assembly"
    temp = find_site_ctgs(start_site, end_site, ratio, assembly)
    error_contain_ctgs = json.loads(temp)  # 将字符串转换为字典
    error_contain_ctgs = list(error_contain_ctgs.items())  # 将字典转换为列表
    print(error_contain_ctgs)
>>>>>>> Ubuntu

if __name__ == "__main__":
    main()
