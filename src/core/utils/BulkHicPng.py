#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: BulkHicPng.py
@time: 2022/5/9 下午5:17
@function: 根据指定参数，产生互作热图
"""

import logging
import os

import hicstraw

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


class BulkHiCPng:
    def __init__(self, hic_file, save_path, chr_a=None, chr_b=None, resolution=None, increment=None):
        self.hic_file = hic_file
        self.resolution = resolution
        self.increment = increment
        self.chr_a = chr_a
        self.chr_b = chr_b
        self.save_path = save_path

    def color_range(self):

        if self.resolution >= 1000000:
            return 2000
        else:
            return 50

    def slide_increment(self):

        increment_sets = {
            2500000: 250000000,
            1250000: 250000000,
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

        return increment_sets[self.resolution]

    @staticmethod
    def generate_file(file_dir):
        # 创建文件夹存
        try:
            os.makedirs(file_dir)

        # 文件夹存在报错
        except FileExistsError:
            logger.error('Result folder already exist', exc_info=True)

    def parsing_hic(self):

        pass

    def trunk_flow(self):
        # 加载对象
        hic = hicstraw.HiCFile(self.hic_file)

        # 获取基因组ID 和 分辨率
        genome_id = hic.getGenomeID()
        resolutions = hic.getResolutions()

        # 创建HiC文件目录
        png_save_dir = os.path.join(self.save_path, genome_id)
        # 创建文件夹存放各个分辨率的图片
        self.generate_file(png_save_dir)

        # 创建分辨率目录
        for resolution in resolutions:
            resolution_dir = os.path.join(png_save_dir, str(resolution))
            self.generate_file(resolution_dir)
            # self.parsing_hic(hic, resolution, resolution_dir)


def main():
    """
    测试
    :return: None
    """
    pass


if __name__ == "__main__":
    main()
