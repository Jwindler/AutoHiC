#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: get_cfg.py
@time: 2/14/23 8:52 PM
@function: get hic file real length
"""

import math

import hicstraw
import numpy as np

from src.assembly.asy_operate import AssemblyOperate

from src.core.utils.logger import logger


def get_ratio(hic, asy_file) -> int:
    """
        get the ratio of the actual length of the chromosome and the length of the chromosome in the assembly file
    Args:
        hic: hic file path
        asy_file: assembly file path

    Returns:
        ratio: assembly length / hic length
    """

    # class Assembly class
    temp = AssemblyOperate(asy_file, ratio=None)

    # get the length of the chromosome in the assembly file
    asy_length = temp.get_info().get("seq_length", "")

    hic_length = 0

    # get hic object
    hic = hicstraw.HiCFile(hic)
    for chrom in hic.getChromosomes():
        hic_length = chrom.length

    logger.info("Ratio(assembly length / hic length) is %s\n", asy_length / hic_length)

    return asy_length / hic_length


def get_hic_len(hic_file) -> int:
    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    hic_len = None  # hic_object length
    for chrom in hic_object.getChromosomes():
        hic_len = chrom.length
    logger.info("Hic file full length is %s\n" % hic_len)
    return hic_len


def get_hic_real_len(hic_file, asy_file) -> int:
    """
        get hic file real length
    Args:
        hic_file: hic file path
        asy_file: assembly file path

    Returns:
        hic file real length
    """

    # get ratio: asy_length / hic_length
    ratio = get_ratio(hic_file, asy_file)

    all_seqs_len = 0  # sequence total length
    real_seqs_len = 0  # real sequence total length

    ctg_dict = {}  # ctg number and length

    # get ctg dict and total length
    with open(asy_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                # get ctg dict and length
                ctg_len = line.strip().split()[2]
                ctg_dict[int(line.strip().split()[1])] = ctg_len
                all_seqs_len += int(ctg_len)
            else:
                # calculate real sequence length
                for ctg in line.strip().split():
                    real_seqs_len += int(ctg_dict[abs(int(ctg))])
                break
    logger.info("Hic file real len: %s\n", round(real_seqs_len / ratio))
    return round(real_seqs_len / ratio)


def increment(resolution):
    """
        get resolution increment
    Args:
        resolution: hic resolution

    Returns:
        resolution increment
    """

    dim_increase = {
        "increase": resolution * 600,  # 生成图片的话，这个值要小一点 300
        "range": resolution * 700  # 700是最小，否则出现颜色阈值不正常的情况
    }

    return dim_increase


def get_max_hic_len(resolution):
    """
        get resolution increment
    Args:
        resolution: hic resolution

    Returns:
        resolution max length
    """

    return resolution * 1400


def get_max_color(hic_file, resolution):
    full_len_matrix = get_full_len_matrix(hic_file, resolution)

    if resolution <= 1000:
        return 1
    maxcolor = (np.percentile(full_len_matrix, 95))
    if maxcolor < 1:
        maxcolor = 1
    return maxcolor


def get_max_color_v2(hic_file, resolution):
    if resolution <= 2000:
        return 1
    elif resolution <= 12500:
        return 3
    else:
        # get hic object
        hic_object = hicstraw.HiCFile(hic_file)

        matrix_zoom_data = hic_object.getMatrixZoomData(
            'assembly', 'assembly', "observed", "KR", "BP", resolution)
        start = 0
        end = resolution * 700
        matrix_data = matrix_zoom_data.getRecordsAsMatrix(start, end, start, end)
        return np.percentile(matrix_data, 95)


def get_full_len_matrix(hic_file, resolution, assembly_file=None):
    # FIXME: 有问题，需要修改(在小分辨率下，报错过，未修改）

    # get hic object
    hic_object = hicstraw.HiCFile(hic_file)

    hic_len = None  # hic_object length
    if assembly_file is None:
        for chrom in hic_object.getChromosomes():
            hic_len = chrom.length
    else:
        hic_len = get_hic_real_len(hic_file, assembly_file)

    # get resolution max len
    res_max_len = get_max_hic_len(resolution)

    # cut full length block number
    len_block_num = math.ceil(hic_len / res_max_len)
    # each block length
    each_block_len = math.ceil(hic_len / len_block_num)
    each_block_res_number = round(each_block_len / resolution)
    iter_len = []
    for i in range(len_block_num):
        iter_len.append(each_block_res_number * i * resolution)
    iter_len.append(hic_len)

    # according to fit_resolution, get matrix_zoom_data
    matrix_zoom_data = hic_object.getMatrixZoomData(
        'assembly', 'assembly', "observed", "KR", "BP", resolution)

    full_len_matrix = None
    for i in range(len(iter_len) - 1):  # loop full length each block
        temp_matrix = None
        for j in range(len(iter_len) - 1):
            # logger.debug(
            #     "Start_A: {}, End_A: {}, Start_B: {}, End_B: {}".format(iter_len[j], iter_len[j + 1] - 1, iter_len[i],
            #                                                             iter_len[i + 1] - 1))
            matrix_data = matrix_zoom_data.getRecordsAsMatrix(iter_len[j], iter_len[j + 1] - 1,
                                                              iter_len[i], iter_len[i + 1] - 1)
            if temp_matrix is None:
                # 稀疏矩阵
                if matrix_data.shape == (1, 1):
                    matrix_data = np.zeros((each_block_res_number, each_block_res_number))
                temp_matrix = matrix_data
            elif matrix_data.shape == (1, 1):
                temp_matrix = np.zeros((each_block_res_number, each_block_res_number))
            else:
                temp_matrix = np.vstack((temp_matrix, matrix_data))

        if full_len_matrix is None:
            full_len_matrix = temp_matrix
        else:
            full_len_matrix = np.hstack((full_len_matrix, temp_matrix))
    return full_len_matrix


def main():
    hic_file = "/home/jzj/Jupyter-Docker/buffer/genomes/05_pb/pb.2.hic"
    assembly_file = "/home/jzj/Jupyter-Docker/buffer/genomes/05_pb/pb.2.assembly"
    print("hic_real_len: ", get_hic_real_len(hic_file, assembly_file))


if __name__ == "__main__":
    main()
