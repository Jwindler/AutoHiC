#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: search_right_site_V4.py
@time: 2/7/23 4:02 PM
@function: 
"""

import json
import math
from collections import defaultdict

import hicstraw
import numpy as np
from scipy.signal import find_peaks

from src.assembly import get_max_peak
from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_conf import get_conf
from src.core.utils.logger import logger
from src.core import settings  # export ENVIROMENT


def get_full_len_matrix(hic_file, fit_resolution: int, width_site: tuple, length_site: tuple = None):
    """
        get full length matrix
    Args:
        hic_file: hic file
        width_site:  error site
        length_site:  length site
        fit_resolution:  fit resolution
    Returns:
        full length matrix
    """

    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    if length_site is None:
        # get full chromosome length
        assembly_len = 0  # define assembly length

        for chrom in hic_object.getChromosomes():
            if chrom.name == "assembly":
                # assembly_len = chrom.length
                # FIXME: 由于hic文件中的长度,可能包含了一些冗余片段，导致插入位置寻找错误，所以需要自己计算一个长度
                assembly_len = 444336001
    else:
        assembly_len = length_site[1] - length_site[0]

    # 根据指定分辨率，获取矩阵对象
    chr_matrix_object = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", fit_resolution)

    # get fit_resolution max len
    cfg = get_conf()  # get config dict
    res_max_len = cfg["rse_max_len"][fit_resolution]

    # cut block number
    len_block_num = math.ceil(assembly_len / res_max_len)

    # each block length
    each_block_len = math.ceil(assembly_len / len_block_num)
    each_block_res_number = round(each_block_len / fit_resolution)
    iter_len = []
    for i in range(len_block_num):
        iter_len.append(each_block_res_number * i * fit_resolution)

    iter_len.append(assembly_len)

    full_len_matrix = None
    for i in range(len(iter_len) - 1):
        if length_site is None:
            # FIXME: 提出来的矩阵可能长度不符合 > 主要是错误长度是否和矩阵一致
            numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(width_site[0], width_site[1],
                                                                    int(iter_len[i]), int(iter_len[i + 1]) - 1)
        else:
            numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(width_site[0], width_site[1],
                                                                    length_site[0] + int(iter_len[i]),
                                                                    length_site[0] + int(iter_len[i + 1]))
        if not np.any(full_len_matrix):
            full_len_matrix = numpy_matrix_chr
        else:
            full_len_matrix = np.hstack((full_len_matrix, numpy_matrix_chr))

    return full_len_matrix


def get_insert_peak(peak_matrix, error_site: tuple, fit_resolution: int, remove_self: bool = True):
    """
        get insert peak
    Args:
        peak_matrix: peak matrix( full_len_matrix )
        error_site: error site
        fit_resolution: fit resolution
        remove_self: remove self error peaks

    Returns:
        insert peak index
    """

    # calculate self index
    bin_index = [i for i in
                 range(int(error_site[0] / fit_resolution) - 2,
                       math.ceil(error_site[1] / fit_resolution) + 2)]
    logger.info("Self error peaks index : %s", bin_index)

    # TODO： find_peaks params: distance
    distance_threshold = len(bin_index)

    numpy_matrix_num = len(peak_matrix)  # get matrix length
    numpy_matrix_len = len(peak_matrix[0])  # get matrix width

    peaks_dict = defaultdict(int)

    for i in range(numpy_matrix_num):
        x = np.arange(0, numpy_matrix_len)  # get matrix index

        y = peak_matrix[i]  # get matrix value

        # get peaks
        # TODO: distance should be a hyperparameter
        # FIXME: height=np.percentile(y, 90) 需要调整，90% 可能峰太多
        peak_id, peak_property = find_peaks(
            y, height=np.percentile(y, 95), distance=distance_threshold)

        peaks_index = x[peak_id]  # get peaks index
        peaks_height = peak_property['peak_heights']  # get peaks height/value

        logger.info("第{0}个矩阵的峰 index：{1}".format(i + 1, peaks_index))
        logger.debug("第{0}个矩阵的峰 value：{1} \n".format(i + 1, peaks_height))

        for peak_index, peak_height in zip(peaks_index, peaks_height):
            if peak_index not in peaks_dict:
                peaks_dict[peak_index] = peak_height
            else:
                peaks_dict[peak_index] = max(
                    peak_height, peaks_dict[peak_index])
    if remove_self:
        # remove self error peaks index
        final_peaks = get_max_peak.remove_peak(peaks_dict, bin_index)
    else:
        final_peaks = peaks_dict

    # get max peak index
    many_key_name = max(final_peaks, key=final_peaks.get)
    logger.info("互作程度最大的index为 %s", many_key_name)

    return many_key_name


def get_max_matrix_value(matrix: np.ndarray):
    """
        get max matrix value
    Args:
        matrix: matrix

    Returns:
        max value
    """
    return np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)[1] + 1


def search_right_site_v4(hic_file, assembly_file, ratio, error_site: tuple):
    asy_operate = AssemblyOperate(assembly_file, ratio)

    hic = hicstraw.HiCFile(hic_file)  # get hic object
    resolutions = hic.getResolutions()  # get fit_resolution list

    error_len = error_site[1] - error_site[0]  # error length

    res_error_distance_list = []

    for res in resolutions:
        res_error_distance_list.append(abs(error_len - res))

    min_index = res_error_distance_list.index(min(res_error_distance_list))  # min value index
    fit_resolution = resolutions[min_index]

    full_len_matrix = get_full_len_matrix(hic_file, fit_resolution, error_site)

    # logger.info("Error full length matrix: ", full_len_matrix.shape)

    insert_peak_index = get_insert_peak(full_len_matrix, error_site, fit_resolution)

    # update Insert region
    update_search_site = (insert_peak_index * fit_resolution, (insert_peak_index + 1) * fit_resolution)
    logger.debug("New Insert region: %s", update_search_site)

    # get fit_resolution max len
    get_conf()  # get config dict

    # get insert region max interaction ctg
    update_full_len_matrix = get_full_len_matrix(hic_file, min(resolutions), error_site, update_search_site)

    # logger.info("Update insert full length matrix: ", full_len_matrix.shape)

    update_insert_peak_index = get_max_matrix_value(update_full_len_matrix)
    final_insert_region = (update_search_site[0] + update_insert_peak_index * min(resolutions),
                           update_search_site[0] + (update_insert_peak_index + 1) * min(resolutions))

    # search ctg in insert peak
    contain_contig = asy_operate.find_site_ctgs(assembly_file, final_insert_region[0], final_insert_region[1])
    # FIXME: 可能有多个 contig

    # json format
    contain_contig = json.loads(contain_contig)

    logger.info("Insert ctg: ： %s", contain_contig)

    # calculate insert direction
    only_ctg_name = list(contain_contig.keys())[0]
    left_distance = update_search_site[0] * ratio - contain_contig[only_ctg_name]["start"]
    right_distance = contain_contig[only_ctg_name]["end"] - update_search_site[1] * ratio

    if left_distance < right_distance:
        logger.info("Insert direction is Left \n")
        insert_direction = "left"
    else:
        logger.info("Insert direction is Right \n")
        insert_direction = "right"

    return contain_contig, insert_direction


def main():
    error_site = (430825001, 431125001)

    hic_file = "/home/jzj/Jupyter-Docker/buffer/03_silkworm/silkworm.0.hic"
    assembly_file = "/home/jzj/Jupyter-Docker/buffer/03_silkworm/silkworm.0.assembly"
    ratio = 1
    print(search_right_site_v4(hic_file, assembly_file, ratio, error_site))


if __name__ == "__main__":
    main()
