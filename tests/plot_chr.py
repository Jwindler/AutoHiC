#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: plot_chr.py
@time: 12/12/22 10:05 AM
@function: visualize Whole genome chromosome
"""
import os
import numpy as np
import hicstraw
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import pyplot as plt

from src.core.utils.logger import logger
from src.core.utils.get_conf import get_conf
from src.core import settings


# FIXME: setting need to be modified


def plot_hic_map(dense_matrix, color, maxcolor, genome_name, out_path, figure_size, dpi, save, chr_dict=None):
    # TODO: chr_dict be used to add chromosome name
    fig, ax = plt.subplots(figsize=figure_size)
    REDMAP = LinearSegmentedColormap.from_list(color, [(1, 1, 1), (1, 0, 0)])
    im = ax.matshow(dense_matrix, cmap=REDMAP, vmin=0, vmax=maxcolor)
    ax.set_title(genome_name)
    plt.xticks([])
    plt.yticks([])
    fig.colorbar(im, ax=ax)
    if save:
        # FIXME: add other format to save
        plt.savefig(os.path.join(out_path, genome_name) + ".svg", dpi=dpi)
    plt.show()
    plt.close()


def plot_chr(hic_date, genome_size=None, chr_name=None, genome_name="result", color="bright_red",
             color_threshold=350,
             resolution=None,
             out_path="./",
             nor_method="NONE", figure_size=(10, 10), dpi=300, save=True):
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
        logger.info("genome name is None, please check your genome input")

    if resolution is None:
        resolution = hic.getResolutions()[0]
        logger.info("resolution is None, use default resolution %s" % resolution)

    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)

    # get config dict
    cfg = get_conf()

    # resolution max length and width
    res_max_len = cfg["rse_max_len"][resolution]
    # res_max_len = cfg["rse_max_len"][125000]

    hic_len = 0  # hic length
    for chrom in hic.getChromosomes():
        hic_len = chrom.length

    # check if you need to cut matrix
    if res_max_len > hic_len:
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(0, hic_len, 0, hic_len)
        plot_hic_map(numpy_matrix_chr, color, color_threshold, out_path=out_path, genome_name=genome_name,
                     figure_size=figure_size, dpi=dpi, save=save)

    else:
        # cut matrix
        block_num = int(hic_len / res_max_len) + 1
        iter_len = np.linspace(0, hic_len, block_num + 1)
        incr_distence = iter_len[1]
        final_matrix = None
        for i in iter_len[1:]:
            temp_matrix = None
            for j in iter_len[1:]:

                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(int(i - incr_distence), int(i),
                                                                        int(j - incr_distence), int(j))
                if not np.any(temp_matrix):
                    temp_matrix = numpy_matrix_chr
                else:
                    temp_matrix = np.hstack((temp_matrix, numpy_matrix_chr))

            if not np.any(final_matrix):
                final_matrix = temp_matrix
            else:
                final_matrix = np.vstack((final_matrix, temp_matrix))

        # 去除全零行
        not_row = final_matrix[[not np.all(final_matrix[i] == 0) for i in range(final_matrix.shape[0])], :]
        # 去除全零列
        bot_col = not_row[:, [not np.all(not_row[:, i] == 0) for i in range(not_row.shape[1])]]

        plot_hic_map(bot_col, color, color_threshold, out_path=out_path, genome_name=genome_name,
                     figure_size=figure_size, dpi=dpi, save=save)


def main():
    hic_date = "/home/jzj/Downloads/Schistocerca.rawchrom.hic"
    plot_chr(hic_date)


if __name__ == "__main__":
    main()
