#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: mul_process.py
@time: 8/31/22 5:25 PM
@function: 指定进程数，并行运行
"""

from multiprocessing import Pool

from src.auto_hic.common.hic_adv_model import GenBaseModel
from src.auto_hic.utils.logger import LoggerHandler

logger = LoggerHandler()


def mul_process(hic_file, genome_id, out_file, process_num=10):
    logger.info("Mul Process Initiating ...")

    # 实例化hic处理类
    hic_operate = GenBaseModel(hic_file, genome_id, out_file)

    resolutions = hic_operate.get_resolutions()  # 获取分辨率列表
    hic_len = hic_operate.get_chr_len()  # 获取基因组长度

    logger.info("threads: %s" % process_num)
    pool = Pool(process_num)  # 进程数

    for resolution in resolutions:
        for plus in range(0, hic_len, hic_len // process_num):
            end = plus + hic_len // process_num
            if end > hic_len:
                end = hic_len
            pool.apply_async(hic_operate.gen_png, args=(resolution, plus, end))
    pool.close()
    pool.join()

    logger.info("Mul Process Finished ...")


def main():
    hic_file = "/home/jzj/Auto-HiC/Test/asy_test/make_inv/Np.final.hic"
    mul_process(hic_file, "Np", "/home/jzj/buffer", 10)


if __name__ == "__main__":
    main()
