#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: search_right_site.py
@time: 7/15/22 10:02 AM
@function: 根据易位检测模型返回的错误区间，查找其需要插入的位置
            根据bin 利用滑动窗口来查找
"""
from scipy.signal import find_peaks
import hicstraw
import numpy as np
from collections import defaultdict
from src.core.utils.logger import LoggerHandler

# 初始化日志
logger = LoggerHandler()


def get_error_matrix(hic_file, error_site: tuple, resolution: int) -> tuple:
    """
    :param hic_file:
    :param error_site:
    :param resolution:
    :return:
    """

    # 解析 .hic 文件
    hic_object = hicstraw.HiCFile(hic_file)

    assembly_len = 0
    # 获取全部染色体的总长度
    for chrom in hic_object.getChromosomes():
        if chrom.name == "assembly":
            assembly_len = chrom.length

    # 根据指定分辨率，获取矩阵对象
    chr_matrix_object = hic_object.getMatrixZoomData('assembly', 'assembly', "observed", "KR", "BP", resolution)

    # 根据错误区间 和 分辨率，获取错误区间的真实矩阵 的 范围
    true_start_bin = round(error_site[0] / resolution)
    true_end_bin = round(error_site[1] / resolution)

    bin_index = np.arange(true_start_bin, true_end_bin)

    true_start = true_start_bin * resolution
    true_end = true_end_bin * resolution

    logger.info("获取矩阵的分辨率为： %s", resolution)
    logger.info("错误区间的真实范围为：{0} - {1} ".format(true_start, true_end))
    logger.info("错误区间的bin范围为：{0} - {1} \n".format(true_start_bin, true_end_bin))

    # 当分辨率增大后，assembly_len 不在使用，需要根据情况进行修改 > get_max_peak.py
    # 根据错误区间，获取错误区间的矩阵
    error_matrix_object = chr_matrix_object.getRecordsAsMatrix(true_start, true_end, 0, assembly_len)

    return error_matrix_object, bin_index


def find_error_peaks(numpy_matrix):
    numpy_matrix_num = len(numpy_matrix)  # 获取矩阵的长度
    numpy_matrix_len = len(numpy_matrix[0])  # 获取矩阵的长度

    peaks_dict = defaultdict(int)

    for i in range(numpy_matrix_num):
        x = np.arange(0, numpy_matrix_len)  # 获取矩阵的索引

        y = numpy_matrix[i]  # 获取矩阵的值

        # 查找峰值点
        peak_id, peak_property = find_peaks(y, height=2000, distance=20)

        peaks_index = x[peak_id]  # 获取峰值点的索引
        peaks_height = peak_property['peak_heights']  # 获取峰值点的值

        logger.info("第{0}个矩阵的峰值点信息：".format(i))
        logger.info("index：{0}".format(peaks_index))
        logger.info("value：{0} \n".format(peaks_height))

        # for peak_index in peaks_index:
        #     peaks_dict[peak_index] += 1
        for peak_index, peak_height in zip(peaks_index, peaks_height):
            if peak_index not in peaks_dict:
                peaks_dict[peak_index] = peak_height
            else:
                peaks_dict[peak_index] = max(peak_height, peaks_dict[peak_index])
    return peaks_dict


# 去除已知的峰值点
def remove_peak(peaks_dict, know_peak):
    for i in know_peak:
        try:
            del peaks_dict[i]
        except KeyError:  # 如果key不存在，则会抛出KeyError异常
            pass

    return peaks_dict


def main():
    error_site = (453010131, 455241282)
    hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.hic"
    # resolution = 1250000
    resolution = 500000

    temp = get_error_matrix(hic_file, error_site, resolution)

    error_matrix_object, bin_index = temp[0], temp[1]
    temp_2 = find_error_peaks(error_matrix_object)
    temp_3 = remove_peak(temp_2, bin_index)

    # 获取交集最多的index
    many_key_name = max(temp_3, key=temp_3.get)

    print("交集最多的index为：{0}".format(many_key_name))
    print("应该插入区间为：{0} - {1}".format(many_key_name * resolution, (many_key_name + 1) * resolution))


if __name__ == "__main__":
    main()
