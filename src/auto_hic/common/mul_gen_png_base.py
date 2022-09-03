#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: mul_gen_png_base.py
@time: 6/24/22 11:53 AM
@function: 多进程生成HiC 图片
"""

import os
import uuid
from multiprocessing import Pool

import hicstraw

from src.auto_hic.common.hic_base_model import GenBaseModel
from src.auto_hic.utils.logger import LoggerHandler


class GsmAll(GenBaseModel):
    logger = LoggerHandler(level="INFO")

    logger.info(
        "Parsing HiC File With Translational Motion Start --当前进程：{}".format(os.getpid()))

    def run_parsing_hic(self, resolution, chrom):

        chrom = str(chrom)  # 将数字转换为字符串

        # HiC对象
        hic = hicstraw.HiCFile(self.hic_file)

        # 基因组ID
        genome_id = hic.getGenomeID()

        # 父文件名
        father_file = os.path.basename(self.hic_file).split(".")[0]

        # 父文件夹
        genome_folder = os.path.join(self.save_dir, father_file)
        self.logger.debug(
            "Create Genome Folder: {0} --当前进程：{1}".format(genome_folder, os.getpid()))
        self.create_folder(genome_folder)

        chromosomes = {}  # 染色体长度
        for chromo in hic.getChromosomes():
            chromosomes[chromo.name] = chromo.length

        del chromosomes['All']  # 去除"All"
        try:
            del chromosomes['MT']  # 去除"MT" 线粒体
        except KeyError:
            self.logger.debug("No MT Chromosome")

        temp_info_file = str(resolution) + "_info.txt"
        info_file = os.path.join(genome_folder, temp_info_file)  # 记录坐标信息
        with open(info_file, 'a+') as f:

            # 范围与增量
            temp_increase = self.increment(resolution)

            # 创建分辨率文件夹
            temp_folder = os.path.join(genome_folder, str(resolution))
            self.logger.debug(
                "Create Resolution Folder: {0} --当前进程：{1}".format(temp_folder, os.getpid()))
            self.create_folder(temp_folder)

            matrix_object_chr = hic.getMatrixZoomData(
                chrom, chrom, "observed", "NONE", "BP", resolution)

            start = 0  # 染色体起始
            end = chromosomes[chrom]  # 终止

            # 染色体内滑动
            for site_1 in range(start, end, temp_increase["increase"]):
                for site_2 in range(
                        start, end, temp_increase["increase"]):

                    flag = False  # 跳出外循环标志

                    temp_q = uuid.uuid1()

                    # 图片文件名
                    temp_folder2 = os.path.join(
                        temp_folder,
                        father_file +
                        "_" +
                        str(resolution) +
                        "_" +
                        str(temp_q) +
                        ".jpg")

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
                            genome_id,
                            chrom,
                            start,
                            end,
                            chrom,
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
                        t = GsmAll.info_records(
                            temp_folder2,
                            genome_id,
                            chrom,
                            site_1,
                            site_1 +
                            temp_increase["dim"],
                            chrom,
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
                        t = GsmAll.info_records(
                            temp_folder2,
                            genome_id,
                            chrom,
                            end - temp_increase["dim"],
                            end,
                            chrom,
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
                        t = GsmAll.info_records(
                            temp_folder2,
                            genome_id,
                            chrom,
                            site_1,
                            site_1 +
                            temp_increase["dim"],
                            chrom,
                            site_2,
                            site_2 +
                            temp_increase["dim"])
                        f.writelines(t + "\n")
                if flag:
                    break
        # 分辨率logging
        self.logger.debug("Resolution: %s Done" % resolution)
        self.logger.debug("Parsing HiC File With Translational Motion Done")


def main():
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

    pool = Pool(10)  # 进程数
    for resolution in resolutions:
        for chrom in chroms:
            pool.apply_async(
                gsm.run_parsing_hic, args=(
                    resolution, chrom,))

    pool.close()
    pool.join()

    print("All Processes Done")


if __name__ == "__main__":
    main()
