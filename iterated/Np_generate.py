#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: script_test.py
@time: 2022/4/18 下午3:48
@function: 单独为Np基因组使用的HiC图片生成
"""


import os
import json
import hicstraw
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt


# 滑动增量
INCREAMENT = 1000000

# 长宽
WIDTH = 50000000


def colorrangeset(resolution):
    """
    提供分辨率，返回ColorRange
    :param resolution:  矩阵分辨率
    :return: ColorRange
    """
    if resolution >= 1000000:
        return 2000
    else:
        return 3


def main():
    input_file_path = "/home/jzj/Auto-HiC/HiC-Data/Np_Hic/0/Np.0.hic"
    output_file_path = "/home/jzj/Auto-HiC/HiC-Data/train_data"

    generate_hic(input_file_path, output_file_path)


def generate_hic(input_file_path, output_file_path):
    """
    根据HiC文件产生各分辨率下的互作热图，并保存
    """

    # 载入对象
    hic = hicstraw.HiCFile(input_file_path)

    # 创建HiC文件目录
    png_save_dir = os.path.join(output_file_path, "test")
    # 创建文件夹存放各个分辨率的图片
    generate_file(png_save_dir)

    resolution_dir = os.path.join(png_save_dir, str(50000))
    generate_file(resolution_dir)
    parsing_hic(hic, 50000, resolution_dir)


def generate_file(file_dir):
    # 创建文件夹存
    try:
        os.makedirs(file_dir)

    # 文件夹存在报错
    except FileExistsError:
        raise FileExistsError


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
    # del chr_len['MT']
    # chr_list.remove('MT')

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

            for j in range(0, chr_len[chr_a], INCREAMENT):
                if resolution in [
                        2500000,
                        1250000,
                        1000000,
                        500000,
                        250000] or j + INCREAMENT >= chr_len[chr_a]:
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
                else:
                    chr_a_end = WIDTH + INCREAMENT
                    chr_b_end = WIDTH + INCREAMENT

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
        vmax=colorrangeset(resolution))
    # 保存图像
    plt.savefig(fig_save_dir, dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
