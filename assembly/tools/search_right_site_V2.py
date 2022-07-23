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
import hicstraw
from collections import OrderedDict

from iterated.search_right_site import get_error_matrix
from iterated.search_right_site import find_error_peaks
from iterated.search_right_site import remove_peak
from assembly.tools.find_site_ctgs import find_site_ctgs


def search_right_site_v2(hic_file, assembly_file, ratio, error_site):
    # 获取分辨率数组
    hic = hicstraw.HiCFile(hic_file)
    resolutions = hic.getResolutions()

    flag = True  # 标记是否需要去除自身peak

    # 存放peak中包含的ctg 信息
    contain_contig = OrderedDict()

    # 循环分辨率数组，精确插入位置
    for resolution in resolutions:
        print("Search resolution:\n", resolution)

        # 获取错误矩阵
        error_matrix = get_error_matrix(hic_file, error_site, resolution)

        # 获取错误的区间 和 bin_index
        error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

        # 查找错误的peak位置
        error_peaks = find_error_peaks(error_matrix_object)

        # 去除自身peak
        if flag:
            final_peaks = remove_peak(error_peaks, bin_index)
            flag = False  # 只需要去除一次
        else:
            final_peaks = error_peaks

        # 获取交集最多的index
        many_key_name = max(final_peaks, key=final_peaks.get)
        print("交集最多的index为", many_key_name)

        # 获取错误peak的位置
        error_site = (many_key_name * resolution, (many_key_name + 1) * resolution)

        # 查找错误peak的位置中包含了哪些ctgs
        contain_contig = find_site_ctgs(error_site[0], error_site[1], ratio, assembly_file)

        # json格式输出
        contain_contig = json.loads(contain_contig)

        if len(contain_contig) == 1:
            print("插入的ctg为：", contain_contig)
            break

    return contain_contig


def main():
    error_site = (495140001, 499424992)
    hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.hic"

    ratio = 2  # 染色体长度比例
    assembly_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.assembly"

    search_right_site_v2(hic_file, assembly_file, ratio, error_site)


if __name__ == "__main__":
    main()
