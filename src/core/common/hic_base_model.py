#!/usr/scripts/env python
# encoding: utf-8

"""
@author: jzj
@contact: jzjlab@163.com
@file: hic_base_model.py
@time: 6/14/22 3:00 PM
@function: generate image base class
"""

import json
import os

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from src.core.utils.get_conf import get_conf
from src.core.utils.logger import logger


class GenBaseModel:
    logger.info("Base Model Initiating ...")

    # get config dict
    cfg = get_conf()

    def __init__(self, hic_file, save_dir):
        self.hic_file = hic_file
        self.save_dir = save_dir

        logger.info(
            "Execute File: {0} --当前进程：{1}".format(self.hic_file, os.getpid()))

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

        result = None  # No_Use
        # check resolution in color_range_sets
        if resolution in color_range_sets.keys():
            return color_range_sets[resolution]
        else:  # get closest resolution
            min_temp = 9999999

            for key, value in color_range_sets.items():
                temp = abs(key - resolution)
                if temp < min_temp:
                    min_temp = temp
                    result = key

            return color_range_sets[result]

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
        len_width_sets = GenBaseModel.cfg['len_width_sets']

        # default increment
        increment_sets = GenBaseModel.cfg['increment_sets']

        result = None  # No_Use
        # check resolution in increment_sets
        if resolution in increment_sets.keys():
            dim_increase["increase"] = increment_sets[resolution]
            dim_increase["dim"] = len_width_sets[resolution]
            return dim_increase
        else:  # get closest resolution value
            min_temp = 9999999  #
            for key, value in increment_sets.items():
                temp = abs(key - resolution)
                if temp < min_temp:
                    min_temp = temp
                    result = key

            # slide increment
            dim_increase["increase"] = increment_sets[result]

            # slide dim range
            dim_increase["dim"] = len_width_sets[result]

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
    def plot_hic_map(matrix, resolution, fig_save_dir):
        """
            plot hic map
        Args:
            matrix: hic matrix
            resolution: hic resolution
            fig_save_dir: figure save dir

        Returns:

        """
        redmap = LinearSegmentedColormap.from_list(
            "bright_red", [(1, 1, 1), (1, 0, 0)])

        # 可视化
        plt.matshow(
            matrix,
            cmap=redmap,
            vmin=0,
            vmax=GenBaseModel.maxcolor(resolution))

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


def main():
    pass


if __name__ == "__main__":
    main()
