#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: search_right_site_V3.py
@time: 1/6/23 09:242 AM
@function: search_right_site upgrade version, used to find the insertion site more accurately
"""

import json
from collections import defaultdict

import hicstraw
import numpy as np
from scipy.signal import find_peaks

from src.assembly import get_max_peak
from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.get_conf import get_conf
from src.core.utils.logger import logger
from src.core import settings  # export ENVIROMENT


def get_full_len_matrix(hic_file, error_site: tuple, fit_resolution: int):
    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    assembly_len = 0  # define assembly length

    # get all chromosome length
    for chrom in hic_object.getChromosomes():
        if chrom.name == "assembly":
            assembly_len = chrom.length

    # 根据指定分辨率，获取矩阵对象
    chr_matrix_object = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", fit_resolution)

    # get fit_resolution max len
    cfg = get_conf()  # get config dict
    res_max_len = cfg["rse_max_len"][fit_resolution]

    # cut block number
    block_num = int(assembly_len / res_max_len) + 1

    iter_len = np.linspace(0, assembly_len, block_num + 1)
    incr_distance = iter_len[1]  # block space

    full_len_matrix = None
    for i in iter_len[1:]:
        numpy_matrix_chr = chr_matrix_object.getRecordsAsMatrix(error_site[0], error_site[1], int(i - incr_distance),
                                                                int(i))
        if not np.any(full_len_matrix):
            full_len_matrix = numpy_matrix_chr
        else:
            full_len_matrix = np.hstack((full_len_matrix, numpy_matrix_chr))

    return full_len_matrix


def get_insert_peak(peak_matrix, error_site: tuple, fit_resolution: int):
    # calculate self index
    bin_index = [i for i in
                 range(round(error_site[0] / fit_resolution) - 1,
                       round(error_site[1] / fit_resolution) + 1)]
    logger.info("Self error peaks index : %s", bin_index)

    # find_peaks params: distance
    distance_threshold = (error_site[1] - error_site[0]) / fit_resolution

    numpy_matrix_num = len(peak_matrix)  # get matrix length
    numpy_matrix_len = len(peak_matrix[0])  # get matrix width

    peaks_dict = defaultdict(int)

    for i in range(numpy_matrix_num):
        x = np.arange(0, numpy_matrix_len)  # get matrix index

        y = peak_matrix[i]  # get matrix value

        # get peaks
        # distance should be a hyperparameter
        peak_id, peak_property = find_peaks(
            y, height=np.percentile(y, 90), distance=distance_threshold)

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

    # remove self error peaks index
    final_peaks = get_max_peak.remove_peak(peaks_dict, bin_index)

    # get max peak index
    many_key_name = max(final_peaks, key=final_peaks.get)
    logger.info("互作程度最大的index为 %s", many_key_name)

    return many_key_name


def search_right_site_v3(hic_file, assembly_file, ratio, error_site: tuple):
    asy_operate = AssemblyOperate(assembly_file, ratio)

    hic = hicstraw.HiCFile(hic_file)  # get hic object
    resolutions = hic.getResolutions()  # get fit_resolution list

    error_len = error_site[1] - error_site[0]  # error length

    res_error_distance_list = []

    for res in resolutions:
        res_error_distance_list.append(abs(error_len - res))

    min_index = res_error_distance_list.index(min(res_error_distance_list))  # min value index
    fit_resolution = resolutions[min_index]

    full_len_matrix = get_full_len_matrix(hic_file, error_site, fit_resolution)
    print("Error full length matrix: ", full_len_matrix.shape)

    insert_peak_index = get_insert_peak(full_len_matrix, error_site, fit_resolution)

    # update search region
    update_search_site = (insert_peak_index * fit_resolution, (insert_peak_index + 1) * fit_resolution)
    logger.debug("New search region: %s", update_search_site)

    # get fit_resolution max len
    cfg = get_conf()  # get config dict

    # iterate resolution list, accuracy search insert site
    for resolution in resolutions.reverse():
        if update_search_site[1] - update_search_site[0] > cfg["rse_max_len"][resolution]:

            # search ctg in insert peak
            contain_contig = asy_operate.find_site_ctgs(assembly_file, update_search_site[0], update_search_site[1])

            # json format
            contain_contig = json.loads(contain_contig)

            if len(contain_contig) == 1:  # only one ctg in insert region
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
                break
            else:
                # FIXME: 不用获取全长矩阵了,直接获取最大互作的位点，更新即可
                full_len_matrix = get_full_len_matrix(hic_file, update_search_site, fit_resolution)

                distance_threshold = (error_site[1] - error_site[0]) / fit_resolution

                numpy_matrix_num = len(full_len_matrix)  # get matrix length
                numpy_matrix_len = len(full_len_matrix[0])  # get matrix width

                peaks_dict = defaultdict(int)

                for i in range(numpy_matrix_num):
                    x = np.arange(0, numpy_matrix_len)  # get matrix index

                    y = full_len_matrix[i]  # get matrix value

                    # get peaks
                    # distance should be a hyperparameter
                    peak_id, peak_property = find_peaks(
                        y, height=np.percentile(y, 90), distance=distance_threshold)

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

                # get max peak index
                many_key_name = max(peaks_dict, key=peaks_dict.get)
                logger.info("互作程度最大的index为 %s", many_key_name)
        else:
            continue


def main():
    error_site = (831625000, 835125000)

    hic_file = "/home/jzj/Downloads/curated/curated.0.hic"
    assembly_file = "/home/jzj/Downloads/curated/curated.0.assembly"
    ratio = 2
    search_right_site_v3(hic_file, assembly_file, ratio, error_site)


if __name__ == "__main__":
    main()
