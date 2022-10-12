#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: hic_adv_model_v2.py
@time: 9/2/22 10:42 AM
@function: 解析Hic文件，生成图片（全局，会产生许多无互作图片）
"""

import json
import os
import uuid

import hicstraw
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from src.core.utils.logger import LoggerHandler
from src.core.utils.get_conf import get_conf
from src.assembly.make_asy import random_color


class GenBaseModel:
    logger = LoggerHandler()

    # 获取配置字典
    cfg = get_conf()

    def __init__(self, hic_file, genome_id, out_file):
        self.logger.info("Base Model Initiating ...")
        self.hic_file = hic_file  # 原始hic文件路径
        self.genome_id = genome_id  # 基因组id
        self.out_file = out_file  # 输出文件路径

        # 创建项目文件夹
        # 父文件名
        self.father_file = os.path.basename(self.hic_file).split(".")[0]

        # 父文件夹
        self.genome_folder = os.path.join(self.out_file, self.genome_id)
        self.logger.info("Create Genome Folder: %s" % self.genome_folder)
        self.create_folder(self.genome_folder)

    def get_resolutions(self):
        hic = hicstraw.HiCFile(self.hic_file)  # 实例化hic对象
        return hic.getResolutions()

    def get_chr_len(self):
        hic_len = 0  # 基因组长度
        hic = hicstraw.HiCFile(self.hic_file)  # 实例化hic对象
        for chrom in hic.getChromosomes():
            hic_len = chrom.length
        return hic_len

    @staticmethod
    def maxcolor(resolution):
        """
        根据分辨率返回MaxColor,用于画图
        :param resolution:
        :return: MaxColor 颜色上线
        """

        # 预定义ColorRange
        color_range_sets = GenBaseModel.cfg["color_range_sets"]

        temp_return = None  # 默认返回值

        # 分辨率包括在预定义中
        if resolution in color_range_sets.keys():
            return color_range_sets[resolution]
        else:  # 与预定义分辨率不符,根据分辨率返回分辨率最靠近的值
            for key, value in color_range_sets.items():
                if resolution < key:
                    temp_return = value
                    continue
                else:
                    return color_range_sets[key]

            return temp_return

    @staticmethod
    def increment(resolution):
        """
        根据分辨率返回窗口滑动每次滑动的距离和窗口范围
        :param resolution:
        # :param chr_len: 用于后续设计参数
        :return: increment 滑动窗口范围和增量的字典
        """

        dim_increase = {}

        # 预定义长宽
        len_width_sets = GenBaseModel.cfg["len_width_sets"]

        # 预定义增量
        increment_sets = GenBaseModel.cfg["increment_sets_detail"]

        # 分辨率包括在预定义中
        if resolution in increment_sets.keys():
            dim_increase["increase"] = increment_sets[resolution]
            dim_increase["dim"] = len_width_sets[resolution]
            return dim_increase
        else:  # 与预定义分辨率不符,根据分辨率返回分辨率最靠近的值，向下取
            for key, value in increment_sets.items():
                if resolution < key:
                    # 滑动增量
                    dim_increase["increase"] = increment_sets[key]

                    # 滑动范围
                    dim_increase["dim"] = len_width_sets[key]
                    continue
                else:
                    # 滑动增量
                    dim_increase["increase"] = increment_sets[key]

                    # 滑动范围
                    dim_increase["dim"] = len_width_sets[key]

                    return dim_increase
            return dim_increase

    @staticmethod
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
            GenBaseModel.logger.debug("Folder Already Exists")

    @staticmethod
    def plot_hic_map(matrix, resolution, fig_save_dir, ran_color=False):
        """
        画图
        Args:
            matrix: 互作矩阵
            resolution: 分辨率
            fig_save_dir: 图片保存路径
            ran_color: 是否随机颜色

        Returns:
            None
        """
        redmap = LinearSegmentedColormap.from_list(
            "bright_red", [(1, 1, 1), (1, 0, 0)])

        vmax = GenBaseModel.maxcolor(resolution)

        if ran_color:
            vmax = random_color()

        # 可视化
        plt.matshow(
            matrix,
            cmap=redmap,
            vmin=0,
            vmax=vmax)

        plt.axis('off')  # 去坐标轴

        # 去除刻度
        plt.xticks([])
        plt.yticks([])

        # 保存图像
        # bbox_inches='tight',pad_inches = -0.01 去白边
        plt.savefig(
            fig_save_dir,
            dpi=300,
            format="jpg",
            bbox_inches='tight',
            pad_inches=-0.01)
        plt.close()

    @staticmethod
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

    def gen_png(self, resolution, a_start, a_end, b_start, b_end, ran_color=False):
        """
        生成png
        Args:
            resolution: 分辨率
            a_start: 互作图像左侧的起始位置
            a_end: 互作图像左侧的结束位置
            b_start: 互作图像上侧的起始位置
            b_end: 互作图像上侧的结束位置
            ran_color: 是否随机颜色

        Returns:
            None
        """
        hic = hicstraw.HiCFile(self.hic_file)  # 实例化hic对象

        # 创建分辨率文件夹
        temp_folder = os.path.join(self.genome_folder, str(resolution))

        # 获取指定分辨率下的矩阵对象
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", resolution)

        temp_q = uuid.uuid4().hex  # 生成随机字符串，命令

        # 图片文件名
        temp_folder2 = os.path.join(temp_folder, str(temp_q) + ".jpg")

        # 提取互作矩阵
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(a_start, a_end, b_start, b_end)

        # 互作图像生成
        if ran_color:
            self.plot_hic_map(numpy_matrix_chr, resolution, temp_folder2, ran_color=True)
        else:
            self.plot_hic_map(numpy_matrix_chr, resolution, temp_folder2)

        # 构建记录字典
        temp_field = self.info_records(
            temp_folder2,
            self.genome_id,
            "assembly",
            a_start,
            a_end,
            "assembly",
            b_start,
            b_end) + "\n"

        return temp_field


def main():
    temp = GenBaseModel(
        "/home/jzj/Data/Test/raw_data/Hv/0/Hv_bgi.0.hic", "Np",
        "/home/jzj/buffer")
    # temp.gen_png(1250000, 0, 1145951891, 0, 1145951891)

    print(temp.increment(333))
    print(temp.maxcolor(333))


if __name__ == "__main__":
    main()
