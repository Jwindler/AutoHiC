#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: one2onePng.py
@time: 5/25/22 4:28 PM
@function: 用于产生根据染色体范围内部，自身互作情况的热图, assembly情况
"""


import os
import json
import hicstraw
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

from autohic.conf import Pre_Config
# 染色体长度测试配置
import example_config


def maxcolor(resolution):
    """
    根据分辨率返回MaxColor,用于画图
    :param resolution:
    :return: MaxColor 颜色上线
    """

    # 预定义ColorRange
    color_range_sets = Pre_Config.color_range_sets

    result = None  # No_Use
    # 分辨率包括在预定义中
    if resolution in color_range_sets.keys():
        return color_range_sets[resolution]
    else:  # 与预定义分辨率不符,根据分辨率返回分辨率最靠近的值
        min_temp = 9999999  #

        for key, value in color_range_sets.items():
            temp = abs(key - resolution)
            if temp < min_temp:
                min_temp = temp
                result = key

        return color_range_sets[result]


def increment(resolution):
    """
    根据分辨率返回窗口滑动每次滑动的距离和窗口范围
    :param resolution:
    # :param chr_len: 用于后续设计参数
    :return: increment 滑动窗口范围和增量的字典
    """

    dim_increase = {}

    # 预定义长宽
    len_width_sets = Pre_Config.len_width_sets

    # 预定义增量
    increment_sets = Pre_Config.increment_sets

    result = None  # No_Use
    # 分辨率包括在预定义中
    if resolution in increment_sets.keys():
        dim_increase["increase"] = increment_sets[resolution]
        dim_increase["dim"] = len_width_sets[resolution]
        return dim_increase
    else:  # 与预定义分辨率不符,根据分辨率返回分辨率最靠近的值
        min_temp = 9999999  #
        for key, value in increment_sets.items():
            temp = abs(key - resolution)
            if temp < min_temp:
                min_temp = temp
                result = key
        dim_increase["increase"] = increment_sets[result]
        dim_increase["dim"] = len_width_sets[result]

        return dim_increase


def create_folder(file_dir):
    """
    创建文件夹
    :param file_dir:
    :return: None
    """
    # 创建文件夹存
    try:
        os.makedirs(file_dir)

    # 文件夹存在报错
    except FileExistsError:
        raise FileExistsError


def plot_hic_map(matrix, resolution, fig_save_dir):
    redmap = LinearSegmentedColormap.from_list(
        "bright_red", [(1, 1, 1), (1, 0, 0)])

    # 可视化
    plt.matshow(
        matrix,
        cmap=redmap,
        vmin=0,
        vmax=maxcolor(resolution))

    # 保存图像
    plt.savefig(fig_save_dir, dpi=300, format="jpg")
    plt.close()


def info_records(
        temp_folder2,
        genome_id,
        chr_a,
        chr_a_s,
        chr_a_e,
        chr_b,
        chr_b_s,
        chr_b_e):
    record = {
        temp_folder2: {
            "genome_id": genome_id,
            "chr_A": chr_a,
            "chr_A_start": chr_a_s,
            "chr_A_end": chr_a_e,
            "chr_B": chr_b,
            "chr_B_start": chr_b_s,
            "chr_B_end": chr_b_e,
        }
    }

    return json.dumps(record)


def parsing_hic(hic_file, save_dir):
    num = 0

    # HiC对象
    hic = hicstraw.HiCFile(hic_file)

    # 基因组ID
    # genome_id = hic.getGenomeID()
    genome_id = "Np-one2one"

    # 父文件夹
    genome_folder = os.path.join(save_dir, genome_id)
    create_folder(genome_folder)

    # 分辨率数组
    resolutions = hic.getResolutions()

    chrom_len = {}  # 染色体-长度

    for chrom in hic.getChromosomes():
        chrom_len[chrom.name] = chrom.length

    del chrom_len['All']  # 去除"All"
    # 染色体对
    temp_chr_pair = []

    for i in chrom_len.keys():
        for j in chrom_len.keys():
            temp_chr_pair.append((i, j))

    info_file = os.path.join(genome_folder, "info.txt")
    with open(info_file, 'a+') as f:
        for j in resolutions:
            # 范围与增量
            temp_increase = increment(j)

            # 创建分辨率文件夹
            temp_folder = os.path.join(genome_folder, str(j))
            create_folder(temp_folder)

            # 循环染色体对
            for k in temp_chr_pair:
                chr_a = k[0]
                chr_b = k[1]
                matrix_object_chr = hic.getMatrixZoomData(
                    chr_a, chr_b, "observed", "KR", "BP", j)



                temp_config = example_config.width
                for i in temp_config:
                    # print(temp_config[i]["start"], temp_config[i]["end"], "\n")

                    start = temp_config[i]["start"]
                    end = temp_config[i]["end"]
                    for m in range(start, end, temp_increase["increase"]):
                        for n in range(
                                start,
                                end,
                                temp_increase["increase"]):
                            temp_folder2 = os.path.join(
                                temp_folder, str(num) + ".jpg")
                            if m + temp_increase["dim"] > chrom_len[chr_a] and n + \
                                    temp_increase["dim"] < chrom_len[chr_b]:
                                a = chrom_len[chr_a]
                                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                                    a - temp_increase["dim"], a, n, n + temp_increase["dim"])
                                plot_hic_map(numpy_matrix_chr, j, temp_folder2)
                                t = info_records(
                                    temp_folder2,
                                    genome_id,
                                    chr_a,
                                    m,
                                    a,
                                    chr_b,
                                    n,
                                    n +
                                    temp_increase["dim"])
                                f.writelines(t + "\n")
                            elif n + temp_increase["dim"] > chrom_len[chr_b] and m + temp_increase["dim"] < chrom_len[chr_a]:
                                a = chrom_len[chr_b]
                                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                                    m, m + temp_increase["dim"], a - temp_increase["dim"], a)
                                plot_hic_map(numpy_matrix_chr, j, temp_folder2)
                                t = info_records(
                                    temp_folder2,
                                    genome_id,
                                    chr_a,
                                    m,
                                    m +
                                    temp_increase["dim"],
                                    chr_b,
                                    n,
                                    a)
                                f.writelines(t + "\n")

                            elif m + temp_increase["dim"] > chrom_len[chr_a] and n + temp_increase["dim"] > chrom_len[chr_b]:
                                a = chrom_len[chr_a]
                                b = chrom_len[chr_b]
                                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                                    a - temp_increase["dim"], a, b - temp_increase["dim"], b)
                                plot_hic_map(numpy_matrix_chr, j, temp_folder2)
                                t = info_records(
                                    temp_folder2, genome_id, chr_a, m, a, chr_b, n, b)
                                f.writelines(t + "\n")
                            else:
                                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                                    m, m + temp_increase["dim"], n, n + temp_increase["dim"])
                                plot_hic_map(numpy_matrix_chr, j, temp_folder2)
                                t = info_records(
                                    temp_folder2,
                                    genome_id,
                                    chr_a,
                                    m,
                                    m +
                                    temp_increase["dim"],
                                    chr_b,
                                    n,
                                    n +
                                    temp_increase["dim"])
                                f.writelines(t + "\n")
                            num += 1


parsing_hic(
    "/home/jzj/Auto-HiC/HiC-Data/Np_HiC/0/Np.0.hic",
    "/home/jzj/Auto-HiC/HiC-Data/train_data")

