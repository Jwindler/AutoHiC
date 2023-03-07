#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: search_right_site_v8.py
@time: 2/21/23 11:40 AM
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
from src.core.utils.get_hic_real_len import get_hic_real_len


def get_full_len_matrix(hic_file, asy_file, fit_resolution: int, width_site: tuple, length_site: tuple = None):
    """
    Get full length matrix
    Args:
        hic_file: hic file
        asy_file: assembly file
        width_site:  error site
        length_site:  length site
        fit_resolution:  fit resolution
    Returns:
        full length matrix
    """

    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    if length_site is None:

        # update width site
        update_width_site = (
            math.ceil(width_site[0] / fit_resolution) * fit_resolution,
            width_site[1] // fit_resolution * fit_resolution)
        width_site = update_width_site

        # get full chromosome length
        assembly_len = 0  # define assembly length

        for chrom in hic_object.getChromosomes():
            if chrom.name == "assembly":
                assembly_len = get_hic_real_len(hic_file, asy_file)
    else:
        assembly_len = length_site[1] - length_site[0]

    # 根据指定分辨率，获取矩阵对象
    chr_matrix_object = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", fit_resolution)

    # get fit_resolution max len
    cfg = get_conf()  # get config dict
    res_max_len = cfg["rse_max_len"][fit_resolution]

    # cut full length block number
    len_block_num = math.ceil(assembly_len / res_max_len)
    # each block length
    each_block_len = math.ceil(assembly_len / len_block_num)
    each_block_res_number = round(each_block_len / fit_resolution)
    iter_len = []
    for i in range(len_block_num):
        iter_len.append(each_block_res_number * i * fit_resolution)
    iter_len.append(assembly_len)

    # cut error site block number
    error_len_block_num = math.ceil((width_site[1] - width_site[0]) / res_max_len)
    # each block length
    error_each_block_len = math.ceil((width_site[1] - width_site[0]) / error_len_block_num)
    error_each_block_res_number = round(error_each_block_len / fit_resolution)
    error_iter_len = []
    for i in range(error_len_block_num):
        error_iter_len.append(width_site[0] + error_each_block_res_number * i * fit_resolution)
    error_iter_len.append(width_site[1])

    full_len_matrix = None
    for i in range(len(iter_len) - 1):  # loop full length each block
        temp_error_matrix = None
        for j in range(len(error_iter_len) - 1):
            if length_site is None:
                print(error_iter_len[j], error_iter_len[j + 1] - 1, iter_len[i], iter_len[i + 1] - 1)
                numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(error_iter_len[j], error_iter_len[j + 1] - 1,
                                                                        iter_len[i], iter_len[i + 1] - 1)
            else:
                print(error_iter_len[j], error_iter_len[j + 1] - 1, length_site[0] + iter_len[i],
                      length_site[0] + iter_len[i + 1])
                numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(error_iter_len[j], error_iter_len[j + 1] - 1,
                                                                        length_site[0] + iter_len[i],
                                                                        length_site[0] + iter_len[i + 1])
            if temp_error_matrix is None:
                # 稀疏矩阵
                if numpy_matrix_chr.shape == (1, 1):
                    numpy_matrix_chr = np.zeros((error_each_block_res_number, each_block_res_number))
                temp_error_matrix = numpy_matrix_chr
            elif numpy_matrix_chr.shape == (1, 1):
                temp_error_matrix = np.zeros((error_each_block_res_number, each_block_res_number))
            else:
                temp_error_matrix = np.vstack((temp_error_matrix, numpy_matrix_chr))

        if full_len_matrix is None:
            full_len_matrix = temp_error_matrix
        else:
            full_len_matrix = np.hstack((full_len_matrix, temp_error_matrix))

    return full_len_matrix


def get_insert_peak(peak_matrix, error_site: tuple, fit_resolution: int, remove_self: bool = True, peak_percentile=95):
    """
        get insert peak
    Args:
        peak_matrix: peak matrix( full_len_matrix )
        error_site: error site
        fit_resolution: fit resolution
        remove_self: remove self error peaks
        peak_percentile: peak percentile

    Returns:
        insert peak index
    """
    logger.debug("Test")

    # calculate self index
    bin_index = [i for i in
                 range(int(error_site[0] / fit_resolution) - 2,
                       math.ceil(error_site[1] / fit_resolution) + 2)]
    logger.info("Self error peaks index : %s", bin_index)

    distance_threshold = len(bin_index)

    numpy_matrix_num = len(peak_matrix)  # get matrix length
    numpy_matrix_len = len(peak_matrix[0])  # get matrix width

    peaks_dict = defaultdict()

    for i in range(numpy_matrix_num):
        x = np.arange(0, numpy_matrix_len)  # get matrix index

        y = peak_matrix[i]  # get matrix value

        # get peaks
        # peak_percentile 需要调整，95% 可能峰太多
        peak_id, peak_property = find_peaks(
            y, height=np.percentile(y, peak_percentile), distance=distance_threshold)

        peaks_index = x[peak_id]  # get peaks index
        peaks_height = peak_property['peak_heights']  # get peaks height/value

        # 下面的内容太长，不打印到日志，或者打印到debug日志
        logger.debug("The peak of the matrix {0} index：{1} \n".format(i + 1, peaks_index))
        logger.debug("The peak of the matrix {0} value：{1} \n".format(i + 1, peaks_height))

        for peak_index, peak_height in zip(peaks_index, peaks_height):
            if peak_index not in peaks_dict:
                peaks_dict[peak_index] = [peak_height, 1]
            else:
                peaks_dict[peak_index] = [max(
                    peak_height, peaks_dict[peak_index][0]), peaks_dict[peak_index][1] + 1]

    if remove_self:
        # remove self error peaks index
        final_peaks = get_max_peak.remove_peak(peaks_dict, bin_index)
        sorted_final_peaks = list(sorted(final_peaks.items(), key=lambda t: t[1][0]))

        # get max peak in overlap peaks
        max_overlap_peak_value = max([x[1][0] for x in sorted_final_peaks])
        for overlap_peak in sorted_final_peaks:
            if overlap_peak[1][0] == max_overlap_peak_value:
                final_peaks.clear()
                final_peaks[overlap_peak[0]] = overlap_peak[1][0]
                break
    else:
        final_peaks = peaks_dict

    # get max peak index
    many_key_name = max(final_peaks, key=final_peaks.get)
    logger.info("The greatest interaction peak index %s \n", many_key_name)

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


def search_right_site_v8(hic_file, assembly_file, ratio, error_site: tuple, modified_assembly_file):
    # init assembly operate object
    asy_operate = AssemblyOperate(assembly_file, ratio)

    hic = hicstraw.HiCFile(hic_file)  # get hic object
    resolutions = hic.getResolutions()  # get fit_resolution list

    error_len = error_site[1] - error_site[0]  # error length

    res_error_distance_list = []

    for res in resolutions:
        res_error_distance_list.append(abs(error_len / 3 - res))

    min_index = res_error_distance_list.index(min(res_error_distance_list))  # min value index
    fit_resolution = resolutions[min_index]

    full_len_matrix = get_full_len_matrix(hic_file, assembly_file, fit_resolution, error_site)

    logger.info("Error full length matrix: %s", full_len_matrix.shape)

    insert_peak_index = get_insert_peak(full_len_matrix, error_site, fit_resolution)

    # update Insert region
    update_search_site = (insert_peak_index * fit_resolution, (insert_peak_index + 1) * fit_resolution)
    logger.info("New insert search region: %s", update_search_site)

    # get fit_resolution max len
    get_conf()  # get config dict

    # get insert region max interaction ctg
    update_full_len_matrix = get_full_len_matrix(hic_file, assembly_file, min(resolutions), error_site,
                                                 update_search_site)

    # logger.info("Update insert full length matrix: ", full_len_matrix.shape)

    update_insert_peak_index = get_max_matrix_value(update_full_len_matrix)
    final_insert_region = (update_search_site[0] + update_insert_peak_index * min(resolutions),
                           update_search_site[0] + (update_insert_peak_index + 1) * min(resolutions))

    logger.info("Final insert region: %s", final_insert_region)

    # search ctg in insert peak
    contain_ctg = asy_operate.find_site_ctg_s(assembly_file, final_insert_region[0], final_insert_region[0] + 1)

    # json format
    contain_ctg = json.loads(contain_ctg)

    # cut final insert location ctg left point
    contain_ctg_first = list(contain_ctg.keys())[0]

    first_cut_ctg = {contain_ctg_first: math.ceil(final_insert_region[0] * ratio)}

    # 如果刚好边界等，不需要切割
    if contain_ctg[contain_ctg_first]["start"] != final_insert_region[0]:
        # cut a ctg to two ctg
        if "fragment" in contain_ctg_first or "debris" in contain_ctg_first:  # check whether the ctg is already cut
            asy_operate.re_cut_ctg_s(modified_assembly_file, first_cut_ctg, modified_assembly_file)
        else:
            asy_operate.cut_ctg_s(modified_assembly_file, first_cut_ctg, modified_assembly_file)

    # search ctg in insert peak
    contain_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, final_insert_region[1],
                                              final_insert_region[1] + 1)

    # json format
    contain_ctg = json.loads(contain_ctg)

    # cut final insert location ctg right point
    contain_ctg_second = list(contain_ctg.keys())[0]

    second_cut_ctg = {contain_ctg_second: math.ceil(final_insert_region[1] * ratio)}

    # 如果刚好边界等，不需要切割
    if contain_ctg[contain_ctg_second]["start"] != final_insert_region[1]:
        # cut a ctg to two ctg
        if "fragment" in contain_ctg_second or "debris" in contain_ctg_second:  # check whether the ctg is already cut
            asy_operate.re_cut_ctg_s(modified_assembly_file, second_cut_ctg, modified_assembly_file)
        else:
            asy_operate.cut_ctg_s(modified_assembly_file, second_cut_ctg, modified_assembly_file)

    # search ctg in insert peak
    contain_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, final_insert_region[0], final_insert_region[1])

    # json format
    contain_ctg = json.loads(contain_ctg)

    # return multiple ctg : ctg > 1
    if len(contain_ctg) > 1:
        max_overlap = {}
        contain_ctg_lists = list(contain_ctg.keys())
        max_overlap[contain_ctg_lists[0]] = contain_ctg[contain_ctg_lists[0]]["end"] - final_insert_region[0]
        max_overlap[contain_ctg_lists[-1]] = final_insert_region[1] - contain_ctg[contain_ctg_lists[-1]][
            "start"]

        for contain_ctg_list in contain_ctg_lists[1:-1]:
            max_overlap[contain_ctg_list] = contain_ctg[contain_ctg_list]["length"]
        temp_contain_ctg = {
            max(max_overlap, key=max_overlap.get): contain_ctg[max(max_overlap, key=max_overlap.get)]}

        contain_ctg = temp_contain_ctg

    logger.info("Insert ctg: ： %s", contain_ctg)

    # calculate insert direction
    only_ctg_name = list(contain_ctg.keys())[0]
    left_distance = round(final_insert_region[0] * ratio) - contain_ctg[only_ctg_name]["start"]
    right_distance = contain_ctg[only_ctg_name]["end"] - round(final_insert_region[1] * ratio)

    if left_distance < right_distance:
        logger.info("Insert direction is Left \n")
        insert_direction = "left"
    else:
        logger.info("Insert direction is Right \n")
        insert_direction = "right"

    return contain_ctg, insert_direction


def main():
    error_site = (175835000, 175980000)

    # hic file path
    hic_file = "/home/jzj/Jupyter-Docker/buffer/10_genomes/curated/curated.2.hic"

    # assembly file path
    assembly_file = "/home/jzj/Jupyter-Docker/buffer/10_genomes/curated/curated.2.assembly"

    ratio = 2.0000000008016556
    modified_assembly_file = "/home/jzj/Jupyter-Docker/buffer/test.assembly"
    print(search_right_site_v8(hic_file, assembly_file, ratio, error_site, modified_assembly_file))


if __name__ == "__main__":
    main()
