#!/usr/bin/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: GSM_all.py
@time: 6/13/22 9:54 PM
@function: HiC文件生成染色体一对一的互作图片（全局移动）
"""


import os
import hicstraw

from autohic.common.base_gen_model import GenBaseModel
from autohic.utils.logger import LoggerHandler


class GsmAll(GenBaseModel):
    logger = LoggerHandler()

    def run_parsing_hic(self):
        self.logger.info("Parsing HiC File With Translational Motion Start")
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
                self.logger.debug("Create Resolution Folder: %s" % temp_folder)
                self.create_folder(temp_folder)

                # 循环染色体对
                for chrom in chromosomes:
                    matrix_object_chr = hic.getMatrixZoomData(
                        chrom, chrom, "observed", "NONE", "BP", resolution)

                    start = 0  # 染色体起始
                    end = chromosomes[chrom]  # 终止

                    # 染色体内滑动
                    for site_1 in range(start, end, temp_increase["increase"]):
                        for site_2 in range(
                                start, end, temp_increase["increase"]):

                            flag = False  # 跳出外循环标志

                            # 图片文件名
                            temp_folder2 = os.path.join(
                                temp_folder, father_file + "_" + str(num) + ".jpg")

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

                                num += 1
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

                                num += 1
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

                                num += 1
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
                            num += 1  # 图片名称加1
                        if flag:
                            break
                # 分辨率logging
                self.logger.info("Resolution: %s Done" % resolution)
        self.logger.info("Parsing HiC File With Translational Motion Done")


def main():
    temp = GsmAll(
        "/home/jzj/Jupyter-Docker/HiC-Straw/GSM/GSM1551550.hic",
        "/home/jzj/buffer")
    temp.run_parsing_hic()


if __name__ == "__main__":
    main()
