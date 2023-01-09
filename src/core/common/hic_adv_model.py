#!/usr/scripts/env python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: hic_adv_model_v2.py
@time: 9/2/22 10:42 AM
@function: parse Hic file, generate contact png
"""

import json
import os
import uuid

import hicstraw
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from src.assembly.make_asy import random_color
from src.core.utils.get_conf import get_conf
from src.core.utils.logger import logger


class GenBaseModel:
    # get config dict
    cfg = get_conf()

    def __init__(self, hic_file, genome_id, out_file):
        logger.info("Base Model Initiating ...")
        self.hic_file = hic_file  # hic file path
        self.genome_id = genome_id  # genome id
        self.out_file = out_file  # output file path

        # create genome folder
        # father folder
        self.father_file = os.path.basename(self.hic_file).split(".")[0]

        self.genome_folder = os.path.join(self.out_file, self.genome_id)
        logger.info("Create Genome Folder: %s" % self.genome_folder)
        self.create_folder(self.genome_folder)

    def get_resolutions(self):
        hic = hicstraw.HiCFile(self.hic_file)  # create hic object
        return hic.getResolutions()

    def get_chr_len(self):
        hic_len = 0  # genome length
        hic = hicstraw.HiCFile(self.hic_file)  # create hic object
        for chrom in hic.getChromosomes():
            hic_len = chrom.length
        return hic_len

    @staticmethod
    def maxcolor(resolution):
        """
            get resolution max color threshold
        Args:
            resolution: hic resolution

        Returns:
            max color threshold
        """

        # default color range
        color_range_sets = GenBaseModel.cfg["color_range_sets"]

        temp_return = None  # default return

        # check resolution in color_range_sets
        if resolution in color_range_sets.keys():
            return color_range_sets[resolution]
        else:  # get closest resolution
            for key, value in color_range_sets.items():
                if resolution < key:
                    temp_return = value
                    continue
                else:
                    return color_range_sets[key]

            return temp_return

    @staticmethod
    def increment(resolution):
        """
            get resolution increment
        Args:
            resolution: hic resolution

        Returns:
            resolution increment
        """

        dim_increase = {}

        # default color range
        len_width_sets = GenBaseModel.cfg["len_width_sets"]

        # default increment
        increment_sets = GenBaseModel.cfg["increment_sets_detail"]

        # check resolution in increment_sets
        if resolution in increment_sets.keys():
            dim_increase["increase"] = increment_sets[resolution]
            dim_increase["dim"] = len_width_sets[resolution]
            return dim_increase
        else:  # get closest resolution value
            for key, value in increment_sets.items():
                if resolution < key:
                    # slide increment
                    dim_increase["increase"] = increment_sets[key]

                    # slide dim range
                    dim_increase["dim"] = len_width_sets[key]
                    continue
                else:
                    # slide increment
                    dim_increase["increase"] = increment_sets[key]

                    # slide dim range
                    dim_increase["dim"] = len_width_sets[key]

                    return dim_increase
            return dim_increase

    @staticmethod
    def create_folder(file_dir):
        """
            create folder
        Args:
            file_dir: folder path

        Returns:

        """

        # create folder
        try:
            os.makedirs(file_dir)
        except FileExistsError:  # folder exists
            logger.debug("Folder Already Exists")

    @staticmethod
    def plot_hic_map(matrix, resolution, fig_save_dir, ran_color=False):
        """
            plot hic map
        Args:
            matrix: hic matrix
            resolution: hic resolution
            fig_save_dir: figure save dir
            ran_color: random color or not

        Returns:

        """
        redmap = LinearSegmentedColormap.from_list(
            "bright_red", [(1, 1, 1), (1, 0, 0)])

        # vmax = GenBaseModel.maxcolor(resolution)
        vmax = np.percentile(matrix, 99)  # get matrix top 99% value
        if vmax == 0:
            vmax = 2
        elif ran_color:
            vmax = random_color()

        # visualize
        plt.matshow(
            matrix,
            cmap=redmap,
            vmin=0,
            vmax=vmax)

        plt.axis('off')  # remove axis

        # remove x and y-axis
        plt.xticks([])
        plt.yticks([])

        # save figure
        plt.savefig(
            fig_save_dir,
            dpi=300,
            format="jpg",
            bbox_inches='tight',
            pad_inches=0.1)
        plt.close()

    @staticmethod
    def info_records(
            temp_folder2,
            genome_id,
            resolution,
            chr_a,
            chr_a_s,
            chr_a_e,
            chr_b,
            chr_b_s,
            chr_b_e):
        record = {
            temp_folder2: {
                "genome_id": genome_id,
                "resolution": resolution,
                "chr_A": chr_a,
                "chr_A_start": chr_a_s,
                "chr_A_end": chr_a_e,
                "chr_B": chr_b,
                "chr_B_start": chr_b_s,
                "chr_B_end": chr_b_e,
            }
        }

        return json.dumps(record)

    def gen_png(self, resolution, a_start, a_end, b_start, b_end, ran_color=False):
        """
            generate png
        Args:
            resolution: hic resolution
            a_start: chr A start
            a_end: chr A end
            b_start: chr B start
            b_end: chr B end
            ran_color: random color or not

        Returns:

        """

        hic = hicstraw.HiCFile(self.hic_file)  # create hic object

        # create resolutions folder
        temp_folder = os.path.join(self.genome_folder, str(resolution))

        # get matrix object by resolution
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", resolution)

        temp_q = uuid.uuid4().hex  # generate random string

        # png file name
        temp_folder2 = os.path.join(temp_folder, str(temp_q) + ".jpg")

        # get contact matrix
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(a_start, a_end, b_start, b_end)

        # plot hic contact map
        if ran_color:
            self.plot_hic_map(numpy_matrix_chr, resolution, temp_folder2, ran_color=True)
        else:
            self.plot_hic_map(numpy_matrix_chr, resolution, temp_folder2)

        # create info record
        temp_field = self.info_records(
            temp_folder2,
            self.genome_id,
            resolution,
            "assembly",
            a_start,
            a_end,
            "assembly",
            b_start,
            b_end) + "\n"

        return temp_field
