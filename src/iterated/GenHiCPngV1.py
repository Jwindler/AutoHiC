#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: script_test.py
@time: 2022/4/18 下午3:48
@function:
"""


import os
import logging
import json
import hicstraw
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

# ====== Logging Start ======
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s")

# FileHandler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
# ====== Logging End ======


logger.info('Start Generate HiC Model Train Picture ')

# 定义各个分辨率下的ColorRange范围
ColorRangeSets = {
    2500000: 4000,
    1000000: 800,
    500000: 250,
    250000: 80,
    100000: 25,
    50000: 20,
    25000: 20,
    10000: 12,
    5000: 10,
    2500: 10,
    500: 10}

# 增量
IncrementSets = {
    2500000: 250000000,
    1000000: 250000000,
    500000: 250000000,
    250000: 250000000,
    100000: 140000000,
    50000: 70000000,
    25000: 35000000,
    10000: 14000000,
    5000: 7000000,
    2500: 3500000,
    500: 700000}


def main():
    input_file_path = "/home/jzj/Auto-HiC/HiC-Data/GSM1551550_HIC001.hic"
    output_file_path = "/home/jzj/Auto-HiC/HiC-Data/train_data/"

    generate_hic(input_file_path, output_file_path)


def generate_hic(input_file_path, output_file_path):
    """
    根据HiC文件产生各分辨率下的互作热图，并保存
    :param input_file_path:
    :param output_file_path:
    :return:
    """

    logger.info("Start Parsing HiC Data")

    # 载入对象
    hic = hicstraw.HiCFile(input_file_path)

    # 获取基因组ID 和 分辨率
    genome_id = hic.getGenomeID()
    resolutions = hic.getResolutions()

    # 创建HiC文件目录
    png_save_dir = os.path.join(output_file_path, genome_id)
    # 创建文件夹存放各个分辨率的图片
    generate_file(png_save_dir)

    # 创建分辨率目录
    for resolution in resolutions:
        resolution_dir = os.path.join(png_save_dir, str(resolution))
        generate_file(resolution_dir)
        parsing_hic(hic, resolution, resolution_dir)


def generate_file(file_dir):
    # 创建文件夹存
    try:
        os.makedirs(file_dir)

    # 文件夹存在报错
    except FileExistsError:
        logger.error('Result folder already exist', exc_info=True)


def parsing_hic(hic, resolution, resolution_dir):
    # 获取基因组ID 和 分辨率
    genome_id = hic.getGenomeID()

    # 获取每条染色体名称和长度
    chr_len = {}
    chr_list = []
    for chrom in hic.getChromosomes():
        chr_len[chrom.name] = chrom.length
        chr_list.append(chrom.name)

    # 默认删除'All' 染色体
    del chr_len['All']
    chr_list.remove('All')

    # 删除线粒体和叶绿体
    del chr_len['MT']
    chr_list.remove('MT')

    # 染色体数目
    chr_count = len(chr_list)

    # 染色体对
    temp_chr_pair = []

    for i in range(chr_count):  # 对角线
        temp_chr_pair.append((chr_list[i], chr_list[i]))

    temp = 0
    with open('/home/jzj/Auto-HiC/HiC-Data/train_data/log.txt', 'a+') as f:
        for i in range(len(temp_chr_pair)):
            # 获取染色体对 各分辨率下的矩阵对象
            chr_a = temp_chr_pair[i][0]
            chr_b = temp_chr_pair[i][1]

            # chr_a_start = 0
            # chr_b_start = 0

            for j in range(0, chr_len[chr_a], IncrementSets[resolution]):
                if resolution in [
                        2500000,
                        1000000,
                        500000,
                        250000] or j + IncrementSets[resolution] >= chr_len[chr_a]:
                    matrix_object_chr = hic.getMatrixZoomData(
                        chr_a, chr_b, "observed", "KR", "BP", resolution)

                    # 获取指定位置的numpy矩阵
                    numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                        j, chr_len[chr_a], j, chr_len[chr_b])

                    # 图片保存名称
                    png_dir = os.path.join(resolution_dir, str(temp) + ".png")
                    print(png_dir)
                    plot_hic_map(numpy_matrix_chr, resolution, png_dir)

                    records = {
                        png_dir: {
                            "genome_id": genome_id,
                            "chr_A": chr_a,
                            "chr_A_start": j,
                            "chr_A_end": chr_len[chr_a],
                            "chr_B": chr_b,
                            "chr_B_start": j,
                            "chr_B_end": chr_len[chr_b],
                        }
                    }
                    f.writelines(json.dumps(records) + "\n")
                    record_png_information(records)
                else:
                    chr_a_end = j + IncrementSets[resolution]
                    chr_b_end = j + IncrementSets[resolution]

                    matrix_object_chr = hic.getMatrixZoomData(
                        chr_a, chr_b, "observed", "KR", "BP", resolution)

                    # 获取指定位置的numpy矩阵
                    numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                        j, chr_a_end, j, chr_b_end)

                    # 图片保存名称
                    png_dir = os.path.join(resolution_dir, str(temp) + ".png")
                    plot_hic_map(numpy_matrix_chr, resolution, png_dir)

                    records = {
                        png_dir: {
                            "genome_id": genome_id,
                            "chr_A": chr_a,
                            "chr_A_start": j,
                            "chr_A_end": chr_a_end,
                            "chr_B": chr_b,
                            "chr_B_start": j,
                            "chr_B_end": chr_b_end,
                        }
                    }
                    f.writelines(json.dumps(records) + "\n")
                    record_png_information(records)

                # 图片数+1
                temp += 1


def plot_hic_map(dense_matrix, resolution, fig_save_dir):
    redmap = LinearSegmentedColormap.from_list(
        "bright_red", [(1, 1, 1), (1, 0, 0)])

    # 可视化
    plt.matshow(
        dense_matrix,
        cmap=redmap,
        vmin=0,
        vmax=ColorRangeSets[resolution])
    # 保存图像
    plt.savefig(fig_save_dir, dpi=300)
    plt.close()


def record_png_information(records):
    json_str = json.dumps(records)
    # print(json_str)


if __name__ == "__main__":
    main()
