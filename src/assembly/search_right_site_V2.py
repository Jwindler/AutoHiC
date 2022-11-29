#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: search_right_site_V2.py
@time: 10/7/22 10:27 AM
@function: search_right_site的升级版本，用于更加精确的查找插入位点
"""

import json
import math
from collections import OrderedDict

import hicstraw

from src.assembly import get_max_peak
from src.core.utils.logger import logger
from src.assembly.asy_operate import AssemblyOperate


def search_right_site_v2(hic_file, assembly_file, ratio, error_site: tuple):
    """
    精确查找易位错误的插入位点
    Args:
        hic_file: hic文件路径
        assembly_file: assembly文件路径
        ratio: 染色体长度比例
        error_site: 易位错误的位置

    Returns:
            插入的位点 + 方向

    """

    # Instantiating AssemblyOperate Class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    error_site_copy = error_site  # 将错误位点复制一份，用于后续查找插入位点时，排除自身位点

    # 获取分辨率数组
    hic = hicstraw.HiCFile(hic_file)  # 提取hic对象
    resolutions = hic.getResolutions()  # 获取分辨率数组

    flag_of_first_insert = True  # 第一次查找插入位点 Flag

    # 存放peak中包含的ctg 信息
    contain_contig = OrderedDict()

    search_site = None  # 查找的位点
    insert_direction = None  # 插入方向记录

    # 循环分辨率数组，精确查找插入位置
    for resolution in resolutions:
        logger.info("Search resolution: %s \n", resolution)

        # 第一次查找
        if flag_of_first_insert:
            search_site = (0, 0)  # 初始化查找位点

            # 获取查询区间的 互作矩阵
            error_matrix = get_max_peak.get_error_matrix(hic_file, error_site, search_site, resolution,
                                                         flag_of_site=flag_of_first_insert)
            # 获取错误的区间 和 bin_index
            error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

            # 查找错误的peak位置
            error_peaks = get_max_peak.find_error_peaks(error_matrix_object)

            # 计算自身的index
            bin_index = [i for i in
                         range(round(error_site_copy[0] / resolution),
                               round(error_site_copy[1] / resolution) + 1)]
            logger.info("self scripts %s", bin_index)

            logger.info("去除自身的bin")
            final_peaks = get_max_peak.remove_peak(error_peaks, bin_index)

            # 获取交集最多的index
            many_key_name = max(final_peaks, key=final_peaks.get)
            logger.info("互作程度最大的index为 %s", many_key_name)

            # 更新查找区间
            search_site = (many_key_name * resolution, (many_key_name + 1) * resolution)
            logger.debug("更新查找区间为 %s", search_site)

            flag_of_first_insert = False  # 标记第一次查找插入位点 已经完成

        else:  # 后续查找为 获取仅有一个ctg的区间
            # 获取查询区间的 互作矩阵
            error_matrix = get_max_peak.get_error_matrix(hic_file, error_site, search_site, resolution,
                                                         flag_of_site=flag_of_first_insert)

            # 获取错误的区间 和 bin_index
            error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

            # 查找互作值最大的位置
            error_max_peak, error_max_peak_index = get_max_peak.find_max_peaks(error_matrix_object)
            logger.info("互作程度最大为 %s", error_max_peak)
            logger.info("互作程度最大的index为 %s", error_max_peak_index)

            # 更新查找区间
            search_site = (
                search_site[0] + (error_max_peak_index[1] - 1) * resolution,
                search_site[0] + (error_max_peak_index[1] + 1) * resolution)
            logger.debug("更新查找区间为 %s", search_site)

        # 查找插入peak的位置中包含了哪些ctgs
        contain_contig = asy_operate.find_site_ctgs(assembly_file, search_site[0], search_site[1])

        # json格式化
        contain_contig = json.loads(contain_contig)

        if len(contain_contig) == 1:  # 插入区间仅有一个ctg
            logger.info("插入的ctg为： %s", contain_contig)

            # 计算插入在左边还是右边
            only_ctg_name = list(contain_contig.keys())[0]
            left_distance = search_site[0] * ratio - contain_contig[only_ctg_name]["start"]
            right_distance = contain_contig[only_ctg_name]["end"] - search_site[1] * ratio

            if left_distance < right_distance:
                logger.info("插入方向在左边 \n")
                insert_direction = "left"
            else:
                logger.info("插入方向在右边 \n")
                insert_direction = "right"
            break

    return contain_contig, insert_direction


def main():
    # error_site = (453010131, 455241282)  # 插入位置：556，750，001 左右 （1，113，500，002）
    error_site = (495175001, 499375001)  # 插入位置：556，750，001 左右 （936,000,000）
    hic_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.hic"

    ratio = 2  # 染色体长度比例
    assembly_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.assembly"

    search_right_site_v2(hic_file, assembly_file, ratio, error_site)


if __name__ == "__main__":
    main()
