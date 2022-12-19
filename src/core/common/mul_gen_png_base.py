#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: mul_gen_png_base.py
@time: 6/24/22 11:53 AM
@function: multiprocessing generate HiC png
"""

import os
import uuid

import hicstraw

from src.core.common.hic_base_model import GenBaseModel
from src.core.utils.logger import logger


class GsmAll(GenBaseModel):
    logger.info(
        "Parsing HiC File With Translational Motion Start --当前进程：{}".format(os.getpid()))

    def run_parsing_hic(self, resolution, chrom):

        chrom = str(chrom)

        # get hic object
        hic = hicstraw.HiCFile(self.hic_file)

        genome_id = hic.getGenomeID()

        # father folder name
        father_file = os.path.basename(self.hic_file).split(".")[0]

        # father folder
        genome_folder = os.path.join(self.save_dir, father_file)
        logger.debug(
            "Create Genome Folder: {0} --当前进程：{1}".format(genome_folder, os.getpid()))
        self.create_folder(genome_folder)

        chromosomes = {}  # chromosome length
        for chromo in hic.getChromosomes():
            chromosomes[chromo.name] = chromo.length

        del chromosomes['All']  # remove "All"
        try:
            del chromosomes['MT']  # remove "MT"
        except KeyError:
            logger.debug("No MT Chromosome")

        temp_info_file = str(resolution) + "_info.txt"
        info_file = os.path.join(genome_folder, temp_info_file)  # write to info file
        with open(info_file, 'a+') as f:

            # dim range and increment
            temp_increase = self.increment(resolution)

            # create resolution folder
            temp_folder = os.path.join(genome_folder, str(resolution))
            logger.debug(
                "Create Resolution Folder: {0} --当前进程：{1}".format(temp_folder, os.getpid()))
            self.create_folder(temp_folder)

            matrix_object_chr = hic.getMatrixZoomData(
                chrom, chrom, "observed", "NONE", "BP", resolution)

            start = 0  # start position
            end = chromosomes[chrom]  # end position

            # sliding in chromosome
            for site_1 in range(start, end, temp_increase["increase"]):
                for site_2 in range(
                        start, end, temp_increase["increase"]):

                    flag = False  # flag to break iteration

                    temp_q = uuid.uuid1()

                    # png file name
                    temp_folder2 = os.path.join(
                        temp_folder,
                        father_file +
                        "_" +
                        str(resolution) +
                        "_" +
                        str(temp_q) +
                        ".jpg")

                    # chr length < defined dim range
                    if end < temp_increase["dim"]:
                        flag = True  # flag to break iteration
                        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(
                            start, end, start, end)

                        # generate png
                        self.plot_hic_map(
                            numpy_matrix_chr, resolution, temp_folder2)

                        # create record
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

                    # a range less than the boundary
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

                    # another range less than the boundary
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

                    # in boundary
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

        # logger to info
        logger.debug("Resolution: %s Done" % resolution)
        logger.debug("Parsing HiC File With Translational Motion Done")
