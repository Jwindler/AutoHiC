#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: visualizer.py
@time: 6/9/23 5:48 PM
@function: 
"""

import os

import hicstraw
import numpy as np
import typer
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from src.utils.get_cfg import get_max_hic_len


def plot_chr(hic_file: str = typer.Option(..., "--hic-file", "-hic", help="hic file path"),
             out_path: str = typer.Option("./", "--out-path", "-out", help="out path of interaction heat map "),
             genome_name: str = typer.Option(None, "--genome-name", "-name", help="genome name"),
             hic_len: int = typer.Option(None, "--hic-length", "-len", help="hic visualize length"),
             maxcolor: int = typer.Option(None, "--max-color", "-max", help="max color of interaction heat map "),
             resolution: int = typer.Option(None, "--resolution", "-r", help="resolution of interaction heat map "),
             figure_size: int = typer.Option(9, "--figure-size", "-size", help="figure size"),
             dpi: int = typer.Option(300, "--dpi", "-d", help="figure dpi"),
             fig_format: str = typer.Option("svg", "--figure_format", "-format", help="figure format, png, svg, pdf")):
    """
    @function: visualize Whole genome chromosome interaction heat map
    Args:
        hic_file: hic file path
        out_path: out path
        genome_name: genome name
        hic_len: hic visualize length
        maxcolor: max color
        resolution: visualize resolution
        figure_size: figure size
        dpi: figure dpi
        fig_format: figure format

    Returns:
        Whole genome chromosome interaction heat map
    """
    hic = hicstraw.HiCFile(hic_file)

    if hic_len is None:
        for chrom in hic.getChromosomes():
            hic_len = chrom.length
        print("hic file full length is %s \n" % hic_len)

    color = [(1, 1, 1), (1, 0, 0)]

    if resolution is None:
        resolution = hic.getResolutions()[0]
        print("Resolution is None, use default resolution %s to plot \n" % resolution)

    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", resolution)

    # resolution max length and width
    res_max_len = get_max_hic_len(resolution)

    # check if you need to cut matrix
    if res_max_len > hic_len:
        print("Resolution max length bigger than hic length \n")
        for res in hic.getResolutions():
            if get_max_hic_len(res) > hic_len:
                resolution = res
                continue
        print("Get contact matrix use resolution is %s\n" % resolution)
        # get new interaction matrix object
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", resolution)
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(0, hic_len, 0, hic_len)
    else:
        print("Resolution max length less than hic length, use max resolution")

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

        not_row = final_matrix[[not np.all(final_matrix[i] == 0) for i in range(final_matrix.shape[0])], :]
        numpy_matrix_chr = not_row[:, [not np.all(not_row[:, i] == 0) for i in range(not_row.shape[1])]]

    # matrix flip
    dense_matrix = np.flipud(numpy_matrix_chr)

    color_percent = 95
    if maxcolor is None:
        maxcolor = (np.percentile(dense_matrix, color_percent))

    fig, ax = plt.subplots(figsize=(figure_size, figure_size))
    red_map = LinearSegmentedColormap.from_list("bright_red", color)

    im = ax.matshow(dense_matrix, cmap=red_map, vmin=0, vmax=maxcolor)

    # set genome title
    ax.set_title(genome_name, fontsize=25)

    ax.set_yticks([])
    ax.set_xticks([])  # need to adjust

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.savefig(os.path.join(out_path, "chromosome." + fig_format), bbox_inches='tight', pad_inches=0.1,
                dpi=dpi,
                format=fig_format)
    # plt.show()  # not show figure
    plt.close()


if __name__ == "__main__":
    typer.run(plot_chr)
