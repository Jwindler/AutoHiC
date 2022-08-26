#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: upper_triangular.py
@time: 2022/5/5 上午11:07
@function: 根据染色体，创建上三角的染色体对
"""

import hicstraw


def main():

    hic = hicstraw.HiCFile(
        "/home/jovyan/HiC-Explore/GSM1551550_HIC001/GSM1551550_HIC001.hic")
    genome_id = hic.getGenomeID()
    resolutions = hic.getResolutions()

    chr_len = {}
    chr_list = []
    for chrom in hic.getChromosomes():
        chr_len[chrom.name] = chrom.length
        chr_list.append(chrom.name)
        print(chrom.name, chrom.length)

    # 默认删除'All' 染色体
    chr_list.remove('All')
    chr_list.remove('MT')

    # 染色体数目
    chr_count = len(chr_list)

    temp_chr_pair = []
    # 染色体对
    for i in range(chr_count):
        for j in range(i, chr_count):
            temp_chr_pair.append((chr_list[i], chr_list[j]))


if __name__ == "__main__":
    main()
