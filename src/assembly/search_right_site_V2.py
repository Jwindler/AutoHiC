#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: search_right_site_V2.py
@time: 10/7/22 10:27 AM
@function: search_right_site upgrade version, used to find the insertion site more accurately
"""

import json
from collections import OrderedDict

import hicstraw

from src.assembly import get_max_peak
from src.assembly.asy_operate import AssemblyOperate
from src.core.utils.logger import logger


def search_right_site_v2(hic_file, assembly_file, ratio, error_site: tuple):
    """
        accuracy search error insert site
    Args:
        hic_file: hic file path
        assembly_file: assembly file path
        ratio: ratio between assembly and hic
        error_site: translocation error site

    Returns:
        error insert site and direction
    """

    # Instantiating AssemblyOperate Class
    asy_operate = AssemblyOperate(assembly_file, ratio)

    error_site_copy = error_site  # copy error site, used to exclude self site when find insert site

    hic = hicstraw.HiCFile(hic_file)  # get hic object
    resolutions = hic.getResolutions()  # get resolution list

    flag_of_first_insert = True  # flag of first insert site

    # save ctg information which in peak
    contain_contig = OrderedDict()

    search_site = None  # search site
    insert_direction = None  # insert direction

    # iterate resolution list, accuracy search insert site
    for resolution in resolutions:
        logger.info("Search resolution: %s \n", resolution)

        # first search
        if flag_of_first_insert:
            search_site = (0, 0)  # init search site

            # get hic matrix of search region
            error_matrix = get_max_peak.get_error_matrix(hic_file, error_site, search_site, resolution,
                                                         flag_of_site=flag_of_first_insert)
            # get error site and bin index
            error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

            # search error peak
            error_peaks = get_max_peak.find_error_peaks(error_matrix_object)

            # calculate self index
            bin_index = [i for i in
                         range(round(error_site_copy[0] / resolution) - 1,
                               round(error_site_copy[1] / resolution) + 1)]
            logger.info("self scripts %s", bin_index)

            logger.info("去除自身的bin")
            final_peaks = get_max_peak.remove_peak(error_peaks, bin_index)

            # get max peak index
            many_key_name = max(final_peaks, key=final_peaks.get)
            logger.info("互作程度最大的index为 %s", many_key_name)

            # update search region
            search_site = (many_key_name * resolution, (many_key_name + 1) * resolution)
            logger.debug("更新查找区间为 %s", search_site)

            flag_of_first_insert = False  # mark first search complete

        else:  # get only one ctg region
            # get hic matrix of search region
            error_matrix = get_max_peak.get_error_matrix(hic_file, error_site, search_site, resolution,
                                                         flag_of_site=flag_of_first_insert)

            # get error site and bin index
            error_matrix_object, bin_index = error_matrix[0], error_matrix[1]

            # get max peak index
            error_max_peak, error_max_peak_index = get_max_peak.find_max_peaks(error_matrix_object)
            logger.info("互作程度最大为 %s", error_max_peak)
            logger.info("互作程度最大的index为 %s", error_max_peak_index)

            # update search region
            search_site = (
                search_site[0] + (error_max_peak_index[1] - 1) * resolution,
                search_site[0] + (error_max_peak_index[1] + 1) * resolution)
            logger.debug("更新查找区间为 %s", search_site)

        # search ctg in insert peak
        contain_contig = asy_operate.find_site_ctgs(assembly_file, search_site[0], search_site[1])

        # json format
        contain_contig = json.loads(contain_contig)

        if len(contain_contig) == 1:  # only one ctg in insert region
            logger.info("插入的ctg为： %s", contain_contig)

            # calculate insert direction
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
    error_site = (495175001, 499375001)  # 插入位置：556，750，001 左右 （936,000,000）
    hic_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.hic"

    ratio = 2  # 染色体长度比例
    assembly_file = "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.assembly"

    search_right_site_v2(hic_file, assembly_file, ratio, error_site)


if __name__ == "__main__":
    main()
