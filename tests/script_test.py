#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: mul_GenHicPng.py
@time: 6/24/22 11:53 AM
@function: 多进程生成HiC 图片
"""

from multiprocessing import Pool

from tests.mul_GenHicPng import GsmAll

if __name__ == '__main__':

    gsm = GsmAll(
        "/home/jzj/Jupyter-Docker/HiC-Straw/GSM/GSM1551550.hic",
        "/home/jzj/Downloads")

    resolutions = [
        2500000,
        1000000,
        500000,
        250000,
        100000,
        50000,
        25000,
        10000,
        5000]  # 分辨率

    chroms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
              14, 15, 16, 17, 18, 19, 20, 21, 22, 'X', 'Y']

    pool = Pool(10)  # 开启4个进程
    for resolution in resolutions:
        for chrom in chroms:
            pool.apply_async(
                gsm.run_parsing_hic, args=(
                    resolution, chrom, ))

    pool.close()
    pool.join()

    print("All Processes Done")
