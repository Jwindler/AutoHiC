#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: search_right_site_mod.py
@time: 7/28/22 17:42 PM
@function: 解决TODO,分辨率问题 line：52
"""
from collections import defaultdict

import hicstraw
import numpy as np
from scipy.signal import find_peaks

from autohic.utils.logger import LoggerHandler

# 实例化日志对象
logger = LoggerHandler()


def get_error_matrix(
        hic_file,
        error_site: tuple,
        search_site,
        resolution: int,
        flag_of_site=False) -> tuple:
    """
    :param hic_file:
    :param error_site:
    :param search_site:
    :param resolution:
    :param flag_of_site:
    :return:
    """

    # 解析 .hic 文件
    hic_object = hicstraw.HiCFile(hic_file)

    assembly_len = 0  # 获取全部染色体的总长度
    for chrom in hic_object.getChromosomes():
        if chrom.name == "assembly":
            assembly_len = chrom.length

    # 根据指定分辨率，获取矩阵对象
    chr_matrix_object = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", resolution)

    # 根据错误区间 和 分辨率，获取错误区间的真实矩阵 的 范围
    true_start_bin = round(error_site[0] / resolution)
    true_end_bin = round(error_site[1] / resolution)

    # 保存错误区间的 index，用于排除自身查找位置
    bin_index = np.arange(true_start_bin, true_end_bin)

    true_start = true_start_bin * resolution
    true_end = true_end_bin * resolution

    logger.info("获取矩阵的分辨率为： %s", resolution)
    logger.info("错误区间的范围（hic）为：{0} - {1} ".format(error_site[0], error_site[1]))

    if flag_of_site:  # 第一次查找，查寻错误区间为总长度
        error_matrix_object = chr_matrix_object.getRecordsAsMatrix(
            error_site[0], error_site[1], search_site[0], assembly_len)
        logger.debug("插入位点查询区间(hic)为：{0} - {1}".format(search_site[0], assembly_len))
    else:
        logger.debug("插入位点查询区间(hic)为：{0} - {1}".format(search_site[0], search_site[1]))

        error_matrix_object = chr_matrix_object.getRecordsAsMatrix(
            error_site[0], error_site[1], search_site[0], search_site[1])
    return error_matrix_object, bin_index


def find_error_peaks(numpy_matrix):
    numpy_matrix_num = len(numpy_matrix)  # 获取矩阵的长度
    numpy_matrix_len = len(numpy_matrix[0])  # 获取矩阵的长度

    peaks_dict = defaultdict(int)

    for i in range(numpy_matrix_num):
        x = np.arange(0, numpy_matrix_len)  # 获取矩阵的索引

        y = numpy_matrix[i]  # 获取矩阵的值

        # 查找峰值点
        # peak_id, peak_property = find_peaks(y, height=2000, distance=20)
        peak_id, peak_property = find_peaks(
            y, height=np.median(numpy_matrix), distance=20)

        peaks_index = x[peak_id]  # 获取峰值点的索引
        peaks_height = peak_property['peak_heights']  # 获取峰值点的值

        logger.info("第{0}个矩阵的峰值点信息：".format(i + 1))
        logger.info("index：{0}".format(peaks_index))
        logger.info("value：{0} \n".format(peaks_height))

        for peak_index, peak_height in zip(peaks_index, peaks_height):
            if peak_index not in peaks_dict:
                peaks_dict[peak_index] = peak_height
            else:
                peaks_dict[peak_index] = max(
                    peak_height, peaks_dict[peak_index])

    return peaks_dict


def find_max_peaks(numpy_matrix):
    """
    二次查找时，获取错误矩阵中最大互作点的值与索引
    :param numpy_matrix: 错误矩阵
    :return: 最大互作点的值与索引
    """
    max_matrix_num = np.max(numpy_matrix)
    max_matrix_num_index = np.where(numpy_matrix == max_matrix_num)
    max_matrix_num_index = (max_matrix_num_index[0].astype(int)[0] + 1, max_matrix_num_index[1].astype(int)[0] + 1)

    return max_matrix_num, max_matrix_num_index


# 去除已知的峰值点
def remove_peak(peaks_dict, know_peak):
    for i in know_peak:
        try:
            del peaks_dict[i]
        except KeyError:  # 如果key不存在，则会抛出KeyError异常
            pass

    return peaks_dict


def main():
    error_site = (556000000, 557500000)
    hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.hic"
    resolution = 500000

    # 待修改
    temp = get_error_matrix(hic_file, error_site, error_site, resolution)

    error_matrix_object, bin_index = temp[0], temp[1]
    temp_2 = find_error_peaks(error_matrix_object)
    temp_3 = remove_peak(temp_2, bin_index)

    # 获取交集最多的index
    many_key_name = max(temp_3, key=temp_3.get)

    logger.info("交集最多的index为：{0}".format(many_key_name))
    logger.info("应该插入区间为：{0} - {1}".format(many_key_name *
                                           resolution, (many_key_name + 1) * resolution))


if __name__ == "__main__":
    main()
