#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_max_peak.py
@time: 7/28/22 17:42 PM
@function: get the max peak of hic matrix
"""

from collections import defaultdict

import hicstraw
import numpy as np
from scipy.signal import find_peaks

from src.core.utils.logger import logger
from src.core.utils.get_conf import get_conf


def get_error_matrix(
        hic_file,
        error_site: tuple,
        search_site,
        resolution: int,
        flag_of_site=False) -> tuple:
    """
        get error matrix
    Args:
        hic_file: hic file
        error_site: error site
        search_site: search site
        resolution: resolution
        flag_of_site: flag of site

    Returns:
        error matrix
    """

    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    # get all chromosome length
    assembly_len = 0  # Declare variables (Line 67)
    for chrom in hic_object.getChromosomes():
        if chrom.name == "assembly":
            assembly_len = chrom.length

    # 根据指定分辨率，获取矩阵对象
    chr_matrix_object = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", resolution)

    # get error matrix range
    true_start_bin = round(error_site[0] / resolution)
    true_end_bin = round(error_site[1] / resolution)

    # save error site index to exclude self search site
    bin_index = np.arange(true_start_bin, true_end_bin)

    # maybe true_start_bin = true_end_bin lead to no return
    if true_start_bin == true_end_bin:
        bin_index = true_start_bin

    logger.info("获取互作矩阵的分辨率为： %s", resolution)
    logger.info("易位错误的范围（hic）：{0} - {1} ".format(error_site[0], error_site[1]))

    # maybe error loci less than resolution
    if error_site[1] - error_site[0] < resolution:
        middle_resolution = round((resolution - (error_site[1] - error_site[0])) / 2)

        if error_site[0] - middle_resolution < 0:
            search_site_a = 0
        else:
            search_site_a = error_site[0] - middle_resolution
        search_site_b = error_site[1] + middle_resolution
    else:
        search_site_a = error_site[0]
        search_site_b = error_site[1]

    if flag_of_site:  # first search, search error site is whole length
        error_matrix_object = chr_matrix_object.getRecordsAsMatrix(
            search_site_a, search_site_b, search_site[0], assembly_len)
        logger.debug("插入位点查询区间(hic)：{0} - {1}".format(search_site[0], assembly_len))
    else:
        logger.debug("插入位点查询区间(hic)：{0} - {1}".format(search_site[0], search_site[1]))

        error_matrix_object = chr_matrix_object.getRecordsAsMatrix(
            search_site_a, search_site_b, search_site[0], search_site[1])
    return error_matrix_object, bin_index


def find_error_peaks(numpy_matrix, distance=5):
    """
        get error matrix peaks
    Args:
        numpy_matrix: error matrix
        distance: distance

    Returns:
        error peaks
    """

    numpy_matrix_num = len(numpy_matrix)  # get matrix length
    numpy_matrix_len = len(numpy_matrix[0])  # get matrix width

    peaks_dict = defaultdict(int)

    for i in range(numpy_matrix_num):
        x = np.arange(0, numpy_matrix_len)  # get matrix index

        y = numpy_matrix[i]  # get matrix value

        # get peaks
        # peak_id, peak_property = find_peaks(y, height=2000, distance=20)
        # distance should be a hyperparameter
        peak_id, peak_property = find_peaks(
            y, height=np.median(numpy_matrix), distance=distance)

        peaks_index = x[peak_id]  # get peaks index
        peaks_height = peak_property['peak_heights']  # get peaks height/value

        logger.info("第{0}个矩阵的峰值点信息：".format(i + 1))
        logger.info("index：{0}".format(peaks_index))
        logger.debug("value：{0} \n".format(peaks_height))

        for peak_index, peak_height in zip(peaks_index, peaks_height):
            if peak_index not in peaks_dict:
                peaks_dict[peak_index] = peak_height
            else:
                peaks_dict[peak_index] = max(
                    peak_height, peaks_dict[peak_index])

    return peaks_dict


def find_max_peaks(numpy_matrix):
    """
        get max peaks in second search
    Args:
        numpy_matrix: error matrix

    Returns:
        max peaks
    """

    max_matrix_num = np.max(numpy_matrix)
    max_matrix_num_index = np.where(numpy_matrix == max_matrix_num)
    max_matrix_num_index = (max_matrix_num_index[0].astype(int)[0] + 1, max_matrix_num_index[1].astype(int)[0] + 1)

    return max_matrix_num, max_matrix_num_index


def remove_peak(peaks_dict, know_peak):
    """
        remove know peak
    Args:
        peaks_dict: peaks dict
        know_peak: know peak

    Returns:
        new peaks dict
    """

    for i in know_peak:
        try:
            del peaks_dict[i]
        except KeyError:  # KeyError: 'key'
            logger.error("Remove_peak warning: self peak not in peaks_dict")

    return peaks_dict


def main():
    error_site = (556000000, 557500000)
    hic_file = "/home/jzj/Jupyter-Docker/HiC-Straw/Np/0/Np.0.hic"
    resolution = 500000

    temp = get_error_matrix(hic_file, error_site, error_site, resolution)

    error_matrix_object, bin_index = temp[0], temp[1]
    temp_2 = find_error_peaks(error_matrix_object)
    temp_3 = remove_peak(temp_2, bin_index)

    # 获取交集最多的index
    many_key_name = max(temp_3, key=temp_3.get)

    logger.info("交集最多的index为：{0}".format(many_key_name))
    logger.info("应该插入区间为：{0} - {1}".format(many_key_name * resolution, (many_key_name + 1) * resolution))


if __name__ == "__main__":
    main()
