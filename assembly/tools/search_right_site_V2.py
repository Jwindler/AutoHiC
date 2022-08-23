#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: search_right_site_V2.py
@time: 7/21/22 4:11 PM
@function: search_right_site的升级版本，用于更加精确的查找插入位点
"""

import json
<<<<<<< HEAD
import hicstraw
from collections import OrderedDict
<<<<<<< HEAD
=======
import math
>>>>>>> Ubuntu
=======
import math
from collections import OrderedDict

import hicstraw
>>>>>>> Ubuntu

from assembly.tools.find_site_ctgs import find_site_ctgs
from autohic.utils.logger import LoggerHandler
from assembly.tools.search_right_site_mod import find_error_peaks
from assembly.tools.search_right_site_mod import find_max_peaks
from assembly.tools.search_right_site_mod import get_error_matrix
from assembly.tools.search_right_site_mod import remove_peak

# 初始化日志
logger = LoggerHandler()


def search_right_site_v2(hic_file, assembly_file, ratio, error_site):
<<<<<<< HEAD
=======
    error_site_copy = error_site  # 将错误位点复制一份，用于后续的判断

>>>>>>> Ubuntu
    # 获取分辨率数组
    hic = hicstraw.HiCFile(hic_file)
    resolutions = hic.getResolutions()

    flag_of_first_insert = True  # 标记第一次查找插入位点

    # 存放peak中包含的ctg 信息
    contain_contig = OrderedDict()

    search_site = None  # 查找的位点
    insert_side = None  # 插入位点的 左右

    # 循环分辨率数组，精确插入位置
    for resolution in resolutions:
        logger.info("Search resolution: %s \n", resolution)

        # 第一次查找
        if flag_of_first_insert:
            search_site = (0, 0)  # 初始化查找位点
            error_matrix = get_error_matrix(hic_file, error_site, search_site, resolution,
                                            flag_of_site=flag_of_first_insert)
            # 获取错误的区间 和 bin_index
            error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

            # 查找错误的peak位置
            error_peaks = find_error_peaks(error_matrix_object)

            bin_index = [i for i in
                         range(math.floor(error_site_copy[0] / resolution),
                               math.floor(error_site_copy[1] / resolution) + 1)]
            logger.info("self bin %s", bin_index)
            final_peaks = remove_peak(error_peaks, bin_index)

<<<<<<< HEAD
        # 去除自身peak
<<<<<<< HEAD
        if flag:
            final_peaks = remove_peak(error_peaks, bin_index)
            flag = False  # 只需要去除一次
        else:
            final_peaks = error_peaks
=======
        # if flag:
        #     final_peaks = remove_peak(error_peaks, bin_index)
        #     flag = False  # 只需要去除一次
        # else:
        #     final_peaks = error_peaks
        bin_index = [i for i in
                     range(math.floor(error_site_copy[0] / resolution),
                           math.floor(error_site_copy[1] / resolution) + 1)]
        print("self bin", bin_index)
        final_peaks = remove_peak(error_peaks, bin_index)
>>>>>>> Ubuntu
=======
            # 获取交集最多的index
            many_key_name = max(final_peaks, key=final_peaks.get)
            logger.info("互作值最大的index为 %s", many_key_name)
>>>>>>> Ubuntu

            # 更新查找区间
            search_site = (many_key_name * resolution, (many_key_name + 1) * resolution)
            logger.debug("更新查找区间为 %s", search_site)

            flag_of_first_insert = False  # 标记第一次查找插入位点 已经完成

        else:  # 后续查找为 获取仅有一个ctg的区间
            error_matrix = get_error_matrix(hic_file, error_site, search_site, resolution,
                                            flag_of_site=flag_of_first_insert)

            # 获取错误的区间 和 bin_index
            error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

            # 查找互作值最大的位置
            error_max_peak, error_max_peak_index = find_max_peaks(error_matrix_object)
            logger.info("互作值最大为 %s", error_max_peak)
            logger.info("互作值最大的index为 %s", error_max_peak_index)

            # 更新查找区间
            search_site = (
                search_site[0] + (error_max_peak_index[1] - 1) * resolution,
                search_site[0] + (error_max_peak_index[1] + 1) * resolution)
            logger.debug("更新查找区间为 %s", search_site)

        # 查找错误peak的位置中包含了哪些ctgs
        contain_contig = find_site_ctgs(search_site[0], search_site[1], ratio, assembly_file)

        # json格式输出
        contain_contig = json.loads(contain_contig)

        if len(contain_contig) == 1:
            logger.info("插入的ctg为： %s", contain_contig)

            # 计算插入在左边还是右边
            only_ctg_name = list(contain_contig.keys())[0]
            left_distance = search_site[0] * ratio - contain_contig[only_ctg_name]["start"]
            right_distance = contain_contig[only_ctg_name]["end"] - search_site[1] * ratio
            if left_distance < right_distance:
                logger.info("插入位点在左边")
                insert_side = "left"
            else:
                logger.info("插入位点在右边")
                insert_side = "right"
            break

    return contain_contig, insert_side


def main():
<<<<<<< HEAD
<<<<<<< HEAD
    error_site = (495140001, 499424992)
=======
    error_site = (453010131, 455241282)
>>>>>>> Ubuntu
    hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.hic"
=======
    # error_site = (453010131, 455241282)  # 插入位置：556，750，001 左右 （1，113，500，002）
    error_site = (495175001, 499375001)  # 插入位置：556，750，001 左右 （936,000,000）
    hic_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.hic"
>>>>>>> Ubuntu

    ratio = 2  # 染色体长度比例
    assembly_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.assembly"

    search_right_site_v2(hic_file, assembly_file, ratio, error_site)


if __name__ == "__main__":
    main()
