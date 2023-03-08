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
from src.core.utils.get_hic_real_len import get_hic_real_len


def plot_hic_map(dense_matrix, color, genome_name, out_path, figure_size, dpi, fig_format, save,
                 chr_dict=None):
    #
    maxcolor = (np.percentile(dense_matrix, 99))

    # TODO: chr_dict be used to add chromosome name
    fig, ax = plt.subplots(figsize=figure_size)
    red_map = LinearSegmentedColormap.from_list(color, [(1, 1, 1), (1, 0, 0)])

    im = ax.matshow(dense_matrix, cmap=red_map, vmin=0, vmax=maxcolor)
    # ax.set_title(genome_name)
    plt.axis('off')  # remove axis
    # plt.xticks([])
    # plt.yticks([])
    # fig.colorbar(im, ax=ax)
    if save:
        # FIXME: add other format to save
        plt.savefig(os.path.join(out_path, genome_name) + "_chr." + fig_format, dpi=dpi, bbox_inches='tight',
                    pad_inches=0)
    plt.show()  # not show figure
    plt.close()


def plot_chr(hic_file, assembly_file=None, genome_size=None, chr_name=None, genome_name=None, color="bright_red",
             resolution=None,
             out_path=None,
             nor_method="NONE", figure_size=(8, 8), dpi=300, fig_format="jpg", save=True):
    """
        plot whole genome chromosome interaction map in one figure
    Args:
        hic_file: hic data path
        assembly_file: asy data path
        genome_name: genome name
        resolution: resolution
        out_path: output path
        genome_size: genome size
        nor_method: normalization method (NONE, VC, VC_SQRT, KR, SCALE, etc.)
        chr_name: chromosome name
        color: color
        figure_size: figure size
        dpi: figure dpi
        fig_format: figure save format(jpg or svg)
        save: save figure or not

    Returns:

    """
    # check input arguments
    if hic_file is None:
        raise ValueError("hic data path is None, please check your input\n")

    if out_path is None:
        logger.warning("Out path is None, use hic file path as out path\n")
        out_path = os.path.dirname(hic_file)

    hic = hicstraw.HiCFile(hic_file)

    hic_len = None  # hic length
    if assembly_file is None:
        for chrom in hic.getChromosomes():
            hic_len = chrom.length
        logger.info("hic file full length is %s\n" % hic_len)
    else:
        hic_len = get_hic_real_len(hic_file, assembly_file)
        logger.info("hic real full length is %s\n" % hic_len)

    # get config dict
    cfg = get_conf()

    if genome_name is None:
        logger.info("Genome name is None, please check your genome input\n")
        genome_name = os.path.basename(hic_file)

    if resolution is None:
        resolution = hic.getResolutions()[0]
        logger.info("Resolution is None, use default resolution %s to plot\n" % resolution)

    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)

    # resolution max length and width
    res_max_len = cfg["rse_max_len"][resolution]

    # check if you need to cut matrix
    if res_max_len > hic_len:
        logger.info("Resolution max length bigger than hic length\n")
        for res in hic.getResolutions():
            if cfg["rse_max_len"][res] > hic_len:
                resolution = res
                continue
        logger.info("Get contact matrix use resolution is %s\n" % resolution)
        # get new interaction matrix object
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(0, hic_len, 0, hic_len)
    else:
        logger.info("Resolution max length less than hic length, use max resolution")

        # cut matrix
        block_num = int(hic_len / res_max_len) + 1
        iter_len = np.linspace(0, hic_len, block_num + 1)
        incr_distance = iter_len[1]
        final_matrix = None
        for i in iter_len[1:]:
            temp_matrix = None
            for j in iter_len[1:]:

                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(int(i - incr_distance), int(i),
                                                                        int(j - incr_distance), int(j))
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
        numpy_matrix_chr = not_row[:, [not np.all(not_row[:, i] == 0) for i in range(not_row.shape[1])]]

    # TODO: 根据 juicer box 来对比
    plot_hic_map(numpy_matrix_chr, color, out_path=out_path, genome_name=genome_name,
                 figure_size=figure_size, dpi=dpi, fig_format=fig_format, save=save)


def main():
    hic_file = "/home/jzj/Data/Elements/328_hic/sis1-161031-pseudohap.rawchrom.hic"
    assembly_file = "/home/jzj/Jupyter-Docker/buffer/chr_data_test/ASM360417v1.rawchrom.assembly"
    out_path = "/home/jzj/Downloads"
    plot_chr(hic_file, assembly_file=None, out_path=out_path, fig_format="png")


if __name__ == "__main__":
    main()
