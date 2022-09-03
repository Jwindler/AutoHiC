#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: hic_base_model.py
@time: 6/14/22 3:00 PM
@function: 生成图片的基类
"""

import json
import os

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from conf import Pre_Config
from src.auto_hic.utils.logger import LoggerHandler


class GenBaseModel:
    logger = LoggerHandler()
    logger.info("Base Model Initiating ...")

    def __init__(self, hic_file, save_dir):
        self.hic_file = hic_file
        self.save_dir = save_dir

        self.logger.info(
            "Execute File: {0} --当前进程：{1}".format(self.hic_file, os.getpid()))

    @staticmethod
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

            # 滑动增量
            dim_increase["increase"] = increment_sets[result]

            # 滑动范围
            dim_increase["dim"] = len_width_sets[result]

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
    def plot_hic_map(matrix, resolution, fig_save_dir):
        redmap = LinearSegmentedColormap.from_list(
            "bright_red", [(1, 1, 1), (1, 0, 0)])

        # 可视化
        plt.matshow(
            matrix,
            cmap=redmap,
            vmin=0,
            vmax=GenBaseModel.maxcolor(resolution))

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


def main():
    pass


if __name__ == "__main__":
    main()
