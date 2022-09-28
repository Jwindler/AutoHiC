#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: MaxContig.py
@time: 5/19/22 4:07 PM
@function: 根据`.assembly`文件，统计最长，短Contig
"""


def count_contig(input_file):
    """
    根据`.assembly`文件，统计最长，短Contig
    :param input_file: assembly文件的绝对路径
    :return: 最长，短Contig元组
    """
    contig_len = {}

    genome_len = 0  # Genome_sequence_length

    result = {}

    # 获取contig与length关系到字典
    with open(input_file, "r") as f:
        for line in f.readlines():
            if line.startswith(">"):
                temp = line.strip().split()
                contig_len[temp[0]] = temp[2]
        contig_total = temp[1]  # Contig 个数
    # 获取基因组总长度
    for value in contig_len.values():
        genome_len += int(value)

    # 按照值大小，对字典排序，获取最大，小contig
    contig_len = {
        k: v for k,
        v in sorted(
            contig_len.items(),
            key=lambda item: item[1])}
    contig_len = list(contig_len.items())

    max_contig = contig_len[0]  # 最长的contig
    min_contig = contig_len[-1]  # 最短的contig

    result["Genome_sequence_length"] = genome_len
    result["Contig_total"] = contig_total
    result["Max_contig"] = max_contig
    result["Min_contig"] = min_contig

    print(result)

    return result


def main():
    temp = count_contig(
        "/home/jzj/Auto-HiC/Test/Np-Self/Np.rawchrom.assembly")
    # print(temp)


if __name__ == "__main__":
    main()
