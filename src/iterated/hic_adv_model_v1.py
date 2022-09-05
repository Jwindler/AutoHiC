#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: hic_adv_model_v1.py
@time: 8/31/22 3:26 PM
@function: 原生hic文件处理类，便于多进程生成图片
"""

import json
import os
import uuid

import hicstraw
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from conf import Pre_Config
from src.auto_hic.utils.logger import LoggerHandler


class GenBaseModel:
    logger = LoggerHandler()
    logger.info("Base Model Initiating ...")

    def __init__(self, hic_file, genome_id, out_file):
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

    def gen_png(self, resolution, start, end):

        hic = hicstraw.HiCFile(self.hic_file)  # 实例化hic对象

        # 创建分辨率文件夹
        temp_folder = os.path.join(self.genome_folder, str(resolution))
        self.create_folder(temp_folder)

        # 获取指定分辨率下的矩阵对象
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "KR", "BP", resolution)

        # 创建info.txt
        info_file = os.path.join(self.genome_folder, "info.txt")
        # 打开info.txt 进行记录
        with open(info_file, "a+") as f:

            # 范围与增量
            temp_increase = self.increment(resolution)

            # 染色体内滑动
            for site_1 in range(start, end, temp_increase["increase"]):
                for site_2 in range(
                        start, end, temp_increase["increase"]):

                    flag = False  # 跳出外循环标志

                    temp_q = uuid.uuid1()

                    # 图片文件名
                    temp_folder2 = os.path.join(
                        temp_folder, str(temp_q) + ".jpg")

                    # 染色体总长度小于 预定义的 宽度
                    if end < temp_increase["dim"]:
                        flag = True  # 跳出外循环标记
                        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                            start, end, start, end)

                        # 图片生成
                        self.plot_hic_map(
                            numpy_matrix_chr, resolution, temp_folder2)

                        # 构建记录
                        t = self.info_records(
                            temp_folder2,
                            self.genome_id,
                            "assembly",
                            start,
                            end,
                            "assembly",
                            start,
                            end)
                        f.writelines(t + "\n")
                        break

                    # 一个范围小于边界
                    elif site_1 + temp_increase["dim"] < end < site_2 + temp_increase["dim"]:
                        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                            site_1, site_1 + temp_increase["dim"], end - temp_increase["dim"], end)
                        self.plot_hic_map(
                            numpy_matrix_chr, resolution, temp_folder2)
                        t = self.info_records(
                            temp_folder2,
                            self.genome_id,
                            "assembly",
                            site_1,
                            site_1 +
                            temp_increase["dim"],
                            "assembly",
                            end - temp_increase["dim"],
                            end)
                        f.writelines(t + "\n")
                        break

                    # 一个范围小于边界
                    elif site_2 + temp_increase["dim"] < end < site_1 + temp_increase["dim"]:
                        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                            end - temp_increase["dim"], end, site_2, site_2 + temp_increase["dim"])
                        self.plot_hic_map(
                            numpy_matrix_chr, resolution, temp_folder2)
                        t = self.info_records(
                            temp_folder2,
                            self.genome_id,
                            "assembly",
                            end - temp_increase["dim"],
                            end,
                            "assembly",
                            site_2,
                            site_2 + temp_increase["dim"])
                        f.writelines(t + "\n")
                        break

                    # 范围内
                    else:
                        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                            site_1, site_1 + temp_increase["dim"], site_2, site_2 + temp_increase["dim"])
                        self.plot_hic_map(
                            numpy_matrix_chr, resolution, temp_folder2)
                        t = self.info_records(
                            temp_folder2,
                            self.genome_id,
                            "assembly",
                            site_1,
                            site_1 +
                            temp_increase["dim"],
                            "assembly",
                            site_2,
                            site_2 +
                            temp_increase["dim"])
                        f.writelines(t + "\n")
                if flag:
                    break


def main():
    temp = GenBaseModel(
        "/home/jzj/Auto-HiC/Test/Np-Self/Np.0.hic", "Np",
        "/home/jzj/buffer")
    temp.gen_png(1250000, 0, 1145951891)


if __name__ == "__main__":
    main()
