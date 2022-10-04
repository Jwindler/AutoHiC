#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: Swindler
@contact: jzjlab@163.com
@file: mul_gen_png.py
@time: 9/5/22 4:00 PM
@function: 多进程生成互作图片
"""

import os
from multiprocessing import Pool

from src.core.common.hic_adv_model import GenBaseModel
from src.core.utils.logger import LoggerHandler

logger = LoggerHandler()

info_path = ""  # define


def write_records(records):
    """
    写入记录
    Args:
        records: 字段

    Returns:
         None
    """
    with open(info_path, "a+") as f:
        f.writelines(records)


def mul_process(hic_file, genome_id, out_file, methods="global", process_num=10):
    """
    多进程生成互作图片
    Args:
        hic_file: hic文件路径
        genome_id: 基因组id
        out_file: 输出文件路径
        methods: global 全局，diagonal 对角线, 默认全局
        process_num: 进程数，默认10

    Returns:
        None
    """
    logger.info("Multiple Process Initiating ...")

    # 实例化hic处理类
    hic_operate = GenBaseModel(hic_file, genome_id, out_file)

    resolutions = hic_operate.get_resolutions()  # 获取分辨率列表

    logger.info("threads: %s" % process_num)
    pool = Pool(process_num)  # 进程数
    start = 0
    end = hic_operate.get_chr_len()  # 基因组长度

    global info_path  # info.txt 文件路径
    info_path = os.path.join(hic_operate.genome_folder, "info.txt")

    for resolution in resolutions:
        logger.info("Processing resolution: %s" % resolution)

        # 创建分辨率文件夹
        temp_folder = os.path.join(hic_operate.genome_folder, str(resolution))
        hic_operate.create_folder(temp_folder)

        # 范围与增量
        temp_increase = hic_operate.increment(resolution)

        if methods == "global":  # 染色体内滑动，全局
            flag = False  # 提前声明
            for site_1 in range(start, end, temp_increase["increase"]):
                if site_1 + temp_increase["dim"] > end:
                    site_1 = end - temp_increase["dim"]
                    flag = True
                for site_2 in range(start, end, temp_increase["increase"]):
                    if site_2 + temp_increase["dim"] > end:
                        site_2 = end - temp_increase["dim"]
                        pool.apply_async(hic_operate.gen_png, args=(
                            resolution, site_1, site_1 + temp_increase["dim"], site_2, site_2 + temp_increase["dim"],),
                                         callback=write_records)
                        break
                    pool.apply_async(hic_operate.gen_png, args=(
                        resolution, site_1, site_1 + temp_increase["dim"], site_2, site_2 + temp_increase["dim"],),
                                     callback=write_records)
                if flag:
                    break
        else:  # 染色体内滑动，斜对角
            for site in range(start, end, temp_increase["increase"]):
                if site + temp_increase["dim"] > end:
                    site = end - temp_increase["dim"]
                pool.apply_async(hic_operate.gen_png, args=(
                    resolution, site, site + temp_increase["dim"], site, site + temp_increase["dim"],),
                                 callback=write_records)

    pool.close()  # 关闭进程池，不再接受新的进程
    pool.join()  # 主进程阻塞等待子进程的退出

    logger.info("Multiple Process Finished ...")


def main():
    hic_file = "/home/jzj/Data/Test/raw_data/Hv/0/Hv_bgi.0.hic"
    # mul_process(hic_file, "Np_global", "/home/jzj/Downloads", "global", 10)
    mul_process(hic_file, "Hv", "/home/jzj/Downloads", "diagonal", 10)


if __name__ == "__main__":
    main()
