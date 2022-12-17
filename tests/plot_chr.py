#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: plot_chr.py
@time: 12/12/22 10:05 AM
@function: visualize Whole genome chromosome
"""

import numpy as np
import hicstraw
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import pyplot as plt
from matplotlib import gridspec
import seaborn as sns
from src.core.utils.logger import logger
from src.core.utils.get_conf import get_conf


def plot_hic_map(dense_matrix, maxcolor, color):
    REDMAP = LinearSegmentedColormap.from_list(color, [(1, 1, 1), (1, 0, 0)])
    plt.matshow(dense_matrix, cmap=REDMAP, vmin=0, vmax=maxcolor)

    plt.axis('off')  # 去坐标轴
    plt.xticks([])
    plt.yticks([])
    plt.show()
    # plt.savefig("/home/jovyan/buffer/test",dpi=300,format="jpg",bbox_inches='tight',pad_inches=-0.01)
    plt.close()


def plot_chr(hic_date, genome_name, genome_size, chr_name, color="bright_red", color_threshold=6000, resolution=None,
             out_path="./",
             nor_method=None, label_loc="center", figure_size=None, dpi=300, show=False, save=True):
    """
        plot whole genome chromosome interaction map in one figure
    Args:
        hic_date: hic data path
        genome_name: genome name
        resolution: resolution
        out_path: output path
        genome_size: genome size
        nor_method: normalization method (NONE, VC, VC_SQRT, KR, SCALE, etc.)
        chr_name: chromosome name
        color: color
        color_threshold: color threshold
        label_loc: label location (default: center)

    Returns:

    """
    # check input arguments
    if hic_date is None:
        logger.error("hic data path is None, please check your input")
        raise ValueError("hic data path is None, please check it")

    hic = hicstraw.HiCFile(hic_date)

    if genome_name is None:
        logger.info("genome name is None, use default genome name")
        genome_name = hic.getGenomeID()

    if resolution is None:
        logger.info("resolution is None, use default resolution")
        resolution = hic.getResolution()[0]

    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)

    # 获取配置字典
    cfg = get_conf()

    # check if you need to cut matrix
    res_max_len = cfg["len_width_sets"][resolution]


def main():
    pass


if __name__ == "__main__":
    main()
