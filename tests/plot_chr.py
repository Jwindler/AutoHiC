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


def plot_hic_map(dense_matrix, color, maxcolor, genome_name, out_path, figure_size, dpi, fig_format, save,
                 chr_dict=None):
    # TODO: chr_dict be used to add chromosome name
    fig, ax = plt.subplots(figsize=figure_size)
    redmap = LinearSegmentedColormap.from_list(color, [(1, 1, 1), (1, 0, 0)])
    im = ax.matshow(dense_matrix, cmap=redmap, vmin=0, vmax=maxcolor)
    # ax.set_title(genome_name)
    plt.axis('off')  # remove axis
    # plt.xticks([])
    # plt.yticks([])
    # fig.colorbar(im, ax=ax)
    if save:
        # FIXME: add other format to save
        plt.savefig(os.path.join(out_path, genome_name) + "_chr." + fig_format, dpi=dpi, bbox_inches='tight')
    plt.show()  # not show figure
    plt.close()


def plot_chr(hic_date, genome_size=None, chr_name=None, genome_name=None, color="bright_red",
             color_threshold=None,
             resolution=None,
             out_path=None,
             nor_method="NONE", figure_size=(8, 8), dpi=300, fig_format="jpg", save=True):
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
        figure_size: figure size
        dpi: figure dpi
        fig_format: figure save format(jpg or svg)
        save: save figure or not

    Returns:

    """
    # check input arguments
    if hic_date is None:
        logger.error("hic data path is None, please check your input")
        raise ValueError("hic data path is None, please check it")

    if out_path is None:
        out_path = os.path.dirname(hic_date)

    hic = hicstraw.HiCFile(hic_date)

    hic_len = 0  # hic length
    for chrom in hic.getChromosomes():
        hic_len = chrom.length

    # get config dict
    cfg = get_conf()

    if genome_name is None:
        logger.info("genome name is None, please check your genome input")
        genome_name = os.path.basename(hic_date)

    if resolution is None:
        resolution = hic.getResolutions()[0]
        logger.info("resolution is None, use default resolution %s to test" % resolution)

    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)

    # resolution max length and width
    res_max_len = cfg["rse_max_len"][resolution]

    # check if you need to cut matrix
    if res_max_len > hic_len:
        logger.info("resolution max length bigger than hic length")
        for res in hic.getResolutions():
            if cfg["rse_max_len"][res] > hic_len:
                resolution = res
                continue
        logger.info("get contact matrix use resolution %s" % resolution)
        # get new interaction matrix object
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(0, hic_len, 0, hic_len)
        color_threshold = (np.percentile(numpy_matrix_chr, 99))
        plot_hic_map(numpy_matrix_chr, color, color_threshold, out_path=out_path, genome_name=genome_name,
                     figure_size=figure_size, dpi=dpi, fig_format=fig_format, save=save)

    else:
        logger.info("resolution max length less than hic length, use test resolution")
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
        color_threshold = (np.percentile(bot_col, 99))
        plot_hic_map(bot_col, color, color_threshold, out_path=out_path, genome_name=genome_name,
                     figure_size=figure_size, dpi=dpi, fig_format=fig_format, save=save)


def main():
    hic_date = "/home/jzj/Downloads/dnazoo/ASM200746v1.rawchrom.hic"
    plot_chr(hic_date)


if __name__ == "__main__":
    main()
