#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: search_right_site_V5.py
@time: 2/15/23 4:19 PM
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
from src.core import settings  # export ENVIROMENT


def get_full_len_matrix(hic_file, asy_file, fit_resolution: int, width_site: tuple, length_site: tuple = None):
    """
        get full length matrix
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
            numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(width_site[0], width_site[1],
                                                                    iter_len[i], iter_len[i + 1] - 1)
            print(width_site[0], width_site[1], iter_len[i], iter_len[i + 1] - 1)
        else:
            numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(width_site[0], width_site[1],
                                                                    length_site[0] + iter_len[i],
                                                                    length_site[0] + iter_len[i + 1])
        if not np.any(full_len_matrix):
            full_len_matrix = numpy_matrix_chr
        else:
            full_len_matrix = np.hstack((full_len_matrix, numpy_matrix_chr))
    print("full_len_matrix.shape", full_len_matrix.shape)
    return full_len_matrix


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


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
    print("Test")

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
        # TODO: distance should be a hyperparameter,  height=np.percentile(y, 90) 需要调整，90% 可能峰太多
        peak_id, peak_property = find_peaks(
            y, height=np.percentile(y, 95), distance=distance_threshold)

        peaks_index = x[peak_id]  # get peaks index
        peaks_height = peak_property['peak_heights']  # get peaks height/value

        logger.info("第{0}个矩阵的峰 index：{1}".format(i + 1, peaks_index))
        logger.debug("第{0}个矩阵的峰 value：{1} \n".format(i + 1, peaks_height))

        for peak_index, peak_height in zip(peaks_index, peaks_height):
            if peak_index not in peaks_dict:
                peaks_dict[peak_index] = [peak_height, 1]
            else:
                peaks_dict[peak_index] = [max(
                    peak_height, peaks_dict[peak_index][0]), peaks_dict[peak_index][1] + 1]

    if remove_self:
        # remove self error peaks index
        final_peaks = get_max_peak.remove_peak(peaks_dict, bin_index)
        sorted_final_peaks = list(sorted(final_peaks.items(), key=lambda t: t[1][1]))
        overlap_peaks = [x for x in sorted_final_peaks if x[1][1] != 1]

        # get max peak in overlap peaks
        max_overlap_peak_value = max([x[1][0] for x in overlap_peaks])
        for overlap_peak in overlap_peaks:
            if overlap_peak[1][0] == max_overlap_peak_value:
                final_peaks.clear()
                final_peaks[overlap_peak[0]] = overlap_peak[1][0]
                break
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


def search_right_site_v5(hic_file, assembly_file, ratio, error_site: tuple):
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
    logger.debug("New Insert region: %s", update_search_site)

    # get fit_resolution max len
    get_conf()  # get config dict

    # get insert region max interaction ctg
    update_full_len_matrix = get_full_len_matrix(hic_file, assembly_file, min(resolutions), error_site,
                                                 update_search_site)

    # logger.info("Update insert full length matrix: ", full_len_matrix.shape)

    update_insert_peak_index = get_max_matrix_value(update_full_len_matrix)
    final_insert_region = (update_search_site[0] + update_insert_peak_index * min(resolutions),
                           update_search_site[0] + (update_insert_peak_index + 1) * min(resolutions))

    # search ctg in insert peak
    contain_contig = asy_operate.find_site_ctgs(assembly_file, final_insert_region[0], final_insert_region[1])

    # json format
    contain_contig = json.loads(contain_contig)

    # return multiple ctg : ctg > 1
    if len(contain_contig) > 1:
        max_overlap = {}
        contain_contigs_list = list(contain_contig.keys())
        max_overlap[contain_contigs_list[0]] = contain_contig[contain_contigs_list[0]]["end"] - final_insert_region[0]
        max_overlap[contain_contigs_list[-1]] = final_insert_region[1] - contain_contig[contain_contigs_list[-1]][
            "start"]

        for contain_contig_list in contain_contigs_list[1:-1]:
            max_overlap[contain_contig_list] = contain_contig[contain_contig_list]["length"]
        temp_contain_contig = {
            max(max_overlap, key=max_overlap.get): contain_contig[max(max_overlap, key=max_overlap.get)]}

        contain_contig = temp_contain_contig

    logger.info("Insert ctg: ： %s", contain_contig)

    # calculate insert direction
    only_ctg_name = list(contain_contig.keys())[0]
    left_distance = round(update_search_site[0] * ratio) - contain_contig[only_ctg_name]["start"]
    right_distance = contain_contig[only_ctg_name]["end"] - round(update_search_site[1] * ratio)

    if left_distance < right_distance:
        logger.info("Insert direction is Left \n")
        insert_direction = "left"
    else:
        logger.info("Insert direction is Right \n")
        insert_direction = "right"

    return contain_contig, insert_direction


def main():
    error_site = (28772000, 28791000)

    hic_file = "/home/jzj/Data/Elements/buffer/10_genomes/03_silkworm/silkworm.1.hic"
    assembly_file = "/home/jzj/Data/Elements/buffer/10_genomes/03_silkworm/silkworm.1.assembly"
    ratio = 1
    print(search_right_site_v5(hic_file, assembly_file, ratio, error_site))


if __name__ == "__main__":
    main()
