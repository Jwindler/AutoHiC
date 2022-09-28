#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: get_ratio.py
@time: 8/31/22 9:48 AM
@function: 获取染色体实际长度与assembly文件中染色体长度的比例
"""
import hicstraw

from src.assembly.asy_operate import AssemblyOperate


def get_ratio(hic, asy_file) -> int:
    """
    获取染色体实际长度与assembly文件中染色体长度的比例
    :param hic: hic文件路径
    :param asy_file: assembly文件路径
    :return: 染色体实际长度与assembly文件中染色体长度的比例
    """

    # 实例化Assembly类
    temp = AssemblyOperate(asy_file, ratio=None)

    # 测试获取整体信息
    asy_length = temp.get_info().get("seq_length", "")

    hic_length = 0  # 声明
    # 实例化hicstraw类
    hic = hicstraw.HiCFile(hic)
    for chrom in hic.getChromosomes():
        hic_length = chrom.length

    return asy_length // hic_length


def main():
    # hic文件路径
    hic_file = "/home/jzj/Data/Test/raw_data/Aa/Aa.2.hic"

    # assembly文件路径
    asy_file = "/home/jzj/Data/Test/raw_data/Aa/Aa.2.assembly"

    result = get_ratio(hic_file, asy_file)
    print(result)


if __name__ == "__main__":
    main()
