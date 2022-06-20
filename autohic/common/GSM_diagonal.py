#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: GSM.py
@time: 6/13/22 9:45 AM
@function: GSM类型的HiC文件生成染色体一对一的互作图片（斜对角移动）
"""


import os
import hicstraw

from autohic.common.base_gen_model import GenBaseModel
from autohic.utils.logger import LoggerHandler


class GsmDiagonal(GenBaseModel):
    logger = LoggerHandler()

    def run_parsing_hic(self):
        self.logger.info("Parsing HiC File with Diagonal Angle Start")
        self.logger.info("Execute File: %s" % self.hic_file)
        num = 1  # 图片起始名称

        # HiC对象
        hic = hicstraw.HiCFile(self.hic_file)

        # 基因组ID
        genome_id = hic.getGenomeID()

        # 父文件名
        father_file = os.path.basename(self.hic_file).split(".")[0]

        # 父文件夹
        genome_folder = os.path.join(self.save_dir, father_file)
        self.logger.debug("Create Genome Folder: %s" % genome_folder)
        self.create_folder(genome_folder)

        # 分辨率数组
        resolutions = hic.getResolutions()

        chromosomes = {}  # 染色体长度
        for chrom in hic.getChromosomes():
            chromosomes[chrom.name] = chrom.length

        del chromosomes['All']  # 去除"All"
        try:
            del chromosomes['MT']  # 去除"MT" 线粒体
        except KeyError:
            self.logger.info("No MT Chromosome")

        info_file = os.path.join(genome_folder, "info.txt")  # 记录坐标信息
        with open(info_file, 'a+') as f:

            # 分辨率
            for resolution in resolutions:

                # 范围与增量
                temp_increase = self.increment(resolution)

                # 创建分辨率文件夹
                temp_folder = os.path.join(genome_folder, str(resolution))
                self.create_folder(temp_folder)
                self.logger.debug("Create Resolution Folder: %s" % temp_folder)

                # 循环染色体对
                for chrom in chromosomes:
                    # 染色体logging
                    # self.logger.info("Chromosome: %s" % chrom)
                    matrix_object_chr = hic.getMatrixZoomData(
                        chrom, chrom, "observed", "NONE", "BP", resolution)

                    start = 0  # 染色体起始
                    end = chromosomes[chrom]  # 终止

                    # 染色体内滑动
                    for site in range(start, end, temp_increase["increase"]):
                        temp_folder2 = os.path.join(
                            temp_folder, father_file + "_" + str(num) + ".jpg")

                        # 染色体总长度小于 预定义的 宽度
                        if end < temp_increase["dim"]:
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

                            num += 1
                            break

                        # 末尾情况
                        elif site + temp_increase["dim"] > end:

                            # 提取互作矩阵
                            numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                                end - temp_increase["dim"], end, end - temp_increase["dim"], end)

                            # 图片生成
                            self.plot_hic_map(
                                numpy_matrix_chr, resolution, temp_folder2)

                            # 构建记录
                            t = self.info_records(
                                temp_folder2,
                                genome_id,
                                chrom,
                                end - temp_increase["dim"],
                                end,
                                chrom,
                                end - temp_increase["dim"],
                                end)
                            f.writelines(t + "\n")

                            num += 1
                            break

                        else:
                            # 提取互作矩阵
                            numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                                site, site + temp_increase["dim"], site, site + temp_increase["dim"])

                            # 图片生成
                            self.plot_hic_map(
                                numpy_matrix_chr, resolution, temp_folder2)

                            # 构建记录
                            t = self.info_records(
                                temp_folder2,
                                genome_id,
                                chrom,
                                site,
                                site + temp_increase["dim"],
                                chrom,
                                site,
                                site + temp_increase["dim"])
                            f.writelines(t + "\n")
                        num += 1  # 图片名称 + 1
                # 分辨率logging
                self.logger.info("Resolution: %s Done" % resolution)
        self.logger.info("Parsing HiC File with Diagonal Angle Done")


def main():
    temp = GsmDiagonal(
        "/home/jzj/Jupyter-Docker/HiC-Straw/GSM/GSE71831.hic",
        "/home/jzj/buffer")
    temp.run_parsing_hic()


if __name__ == "__main__":
    main()
